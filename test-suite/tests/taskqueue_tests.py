import json
from time import sleep
import uuid
import datetime
from hawkeye_utils import HawkeyeTestCase, HawkeyeTestSuite

__author__ = 'hiranya'

class PushQueueTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_delete('/taskqueue/counter')
    self.assertEquals(response.status, 200)

    key = str(uuid.uuid1())
    response = self.http_post('/taskqueue/counter',
      'key={0}'.format(key))
    task_info = json.loads(response.payload)
    self.assertEquals(response.status, 200)
    self.assertTrue(task_info['status'])
    self.get_and_assert_counter(key, 1)

    response = self.http_post('/taskqueue/counter',
      'key={0}&get=true'.format(key))
    task_info = json.loads(response.payload)
    self.assertEquals(response.status, 200)
    self.assertTrue(task_info['status'])
    self.get_and_assert_counter(key, 2)

    for _ in range(10):
      response = self.http_post('/taskqueue/counter',
        'key={0}'.format(key))
      task_info = json.loads(response.payload)
      self.assertEquals(response.status, 200)
      self.assertTrue(task_info['status'])
    self.get_and_assert_counter(key, 12)

  def get_and_assert_counter(self, key, expected):
    """
    Perform a HTTP GET on /taskqueue/counter for the given key and
    obtain the counter value from GAE datastore API. The returned value
    will be asserted against the provided expected value. This method
    is blocking in that it blocks until a valid response is received from
    the backend service. If a valid response is not received within 10
    minutes, this method will force the parent test case to fail.

    Args:
      key A datastore key string
      expected  Expected integer value
    """

    start = datetime.datetime.now()
    end = start + datetime.timedelta(0, 600)
    while True:
      response = self.http_get('/taskqueue/counter?key={0}'.format(key))
      self.assertTrue(response.status == 200 or response.status == 404)
      if response.status == 200:
        task_info = json.loads(response.payload)
        if task_info[key] == expected:
          break

      if datetime.datetime.now() > end:
        self.fail('Push queue deadline exceeded with no result')
      else:
        sleep(2)

class DeferredTaskTest(PushQueueTest):
  def run_hawkeye_test(self):
    key = str(uuid.uuid1())
    response = self.http_post('/taskqueue/counter',
      'key={0}&defer=true'.format(key))
    task_info = json.loads(response.payload)
    self.assertEquals(response.status, 200)
    self.assertTrue(task_info['status'])
    self.get_and_assert_counter(key, 1)

    response = self.http_post('/taskqueue/counter',
      'key={0}&defer=true'.format(key))
    task_info = json.loads(response.payload)
    self.assertEquals(response.status, 200)
    self.assertTrue(task_info['status'])
    self.get_and_assert_counter(key, 2)

    for _ in range(10):
      response = self.http_post('/taskqueue/counter',
        'key={0}&defer=true'.format(key))
      task_info = json.loads(response.payload)
      self.assertEquals(response.status, 200)
      self.assertTrue(task_info['status'])
    self.get_and_assert_counter(key, 12)

class BackendTaskTest(PushQueueTest):
  def run_hawkeye_test(self):
    key = str(uuid.uuid1())
    response = self.http_post('/taskqueue/counter',
      'key={0}&backend=true'.format(key))
    task_info = json.loads(response.payload)
    self.assertEquals(response.status, 200)
    self.assertTrue(task_info['status'])
    self.get_and_assert_counter(key, 1)

    response = self.http_post('/taskqueue/counter',
      'key={0}&backend=true'.format(key))
    task_info = json.loads(response.payload)
    self.assertEquals(response.status, 200)
    self.assertTrue(task_info['status'])
    self.get_and_assert_counter(key, 2)

    for _ in range(10):
      response = self.http_post('/taskqueue/counter',
        'key={0}&backend=true'.format(key))
      task_info = json.loads(response.payload)
      self.assertEquals(response.status, 200)
      self.assertTrue(task_info['status'])
    self.get_and_assert_counter(key, 12)

class QueueStatisticsTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/taskqueue/counter?stats=true')
    self.assertEquals(response.status, 200)
    task_info = json.loads(response.payload)
    self.assertEquals(task_info['queue'], 'default')

class PullQueueTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    key = str(uuid.uuid1())
    response = self.http_post('/taskqueue/pull',
      'key={0}'.format(key))
    task_info = json.loads(response.payload)
    self.assertEquals(response.status, 200)
    self.assertTrue(task_info['status'])

    start = datetime.datetime.now()
    end = start + datetime.timedelta(0, 60)
    while True:
      response = self.http_get('/taskqueue/pull')
      self.assertEquals(response.status, 200)
      task_info = json.loads(response.payload)
      if len(task_info['tasks']) == 1 and key in task_info['tasks']:
        break
      if datetime.datetime.now() > end:
        self.fail('Pull queue deadline exceeded with no result')
      else:
        sleep(2)

def suite(lang):
  suite = HawkeyeTestSuite('Task Queue Test Suite', 'taskqueue')
  suite.addTest(PushQueueTest())
  suite.addTest(DeferredTaskTest())
  suite.addTest(QueueStatisticsTest())
  suite.addTest(PullQueueTest())

  # Does not work due to a bug in the dev server
  # Check SO/questions/13273067/app-engine-python-development-server-taskqueue-backend
  #suite.addTest(BackendTaskTest())
  return suite

