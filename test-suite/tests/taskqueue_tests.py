import datetime
import json
import uuid
from time import sleep

from hawkeye_utils import HawkeyeTestCase
from hawkeye_utils import HawkeyeTestSuite

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
      sleep(1)
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
    end = start + datetime.timedelta(0, 60)
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
      sleep(1)
      response = self.http_post('/taskqueue/counter',
        'key={0}&defer=true'.format(key))
      task_info = json.loads(response.payload)
      self.assertEquals(response.status, 200)
      self.assertTrue(task_info['status'])
    self.get_and_assert_counter(key, 12)

class TaskEtaTest(PushQueueTest):
  def run_hawkeye_test(self):
    key = str(uuid.uuid1())
    #eta should be less than 30 because of get_and_assert_counter method
    eta = 10
    response = self.http_post('/taskqueue/counter',
      'key={0}&eta={1}'.format(key,eta))
    task_info = json.loads(response.payload)
    self.get_and_assert_counter(key, 1)

class TaskRetryTest(PushQueueTest):
  def run_hawkeye_test(self):
    key = str(uuid.uuid1())
    response = self.http_post('/taskqueue/counter',
      'key={0}&retry=true'.format(key))
    task_info = json.loads(response.payload)
    self.assertEquals(response.status, 200)
    self.assertTrue(task_info['status'])
    self.get_and_assert_counter(key, 1)

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
    end = start + datetime.timedelta(0, 30)
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

class TransactionalTaskTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    key = str(uuid.uuid1())
    response = self.http_post('/taskqueue/trans', 'key={0}'.format(key))
    value = json.loads(response.payload)['value']
    self.assertEquals('TXN_UPDATE', value)

    start = datetime.datetime.now()
    end = start + datetime.timedelta(0, 5)
    while True:
      response = self.http_get('/taskqueue/trans?key={0}'.format(key))
      self.assertEquals(response.status, 200)
      value = json.loads(response.payload)['value']

      if value == 'TQ_UPDATE':
        break

      if datetime.datetime.now() > end:
        self.fail('Transactional task did not run')
      else:
        sleep(1)

class TransactionalFailedTaskTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    key = str(uuid.uuid1())
    response = self.http_post('/taskqueue/trans', 'key={0}&raise_exception=True'.\
      format(key))
    value = json.loads(response.payload)['value']
    self.assertEquals('None', value)

    start = datetime.datetime.now()
    end = start + datetime.timedelta(0, 5)
    while True:
      response = self.http_get('/taskqueue/trans?key={0}'.format(key))
      self.assertEquals(response.status, 200)
      value = json.loads(response.payload)['value']
      # Make sure it does not change.
      if value != None:
        self.fail('Transaction value should have been None, was {0}'.format(value))

      if datetime.datetime.now() > end:
        break
      else:
        sleep(1)

class CleanUpTaskEntities(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/taskqueue/clean_up')
    self.assertEquals(response.status, 200)

def suite(lang):
  suite = HawkeyeTestSuite('Task Queue Test Suite', 'taskqueue')
  suite.addTest(PushQueueTest())
  suite.addTest(DeferredTaskTest())
  suite.addTest(QueueStatisticsTest())
  suite.addTest(PullQueueTest())
  suite.addTest(TaskRetryTest())
  suite.addTest(TaskEtaTest())
  suite.addTest(TransactionalTaskTest())
  suite.addTest(TransactionalFailedTaskTest())
  suite.addTest(CleanUpTaskEntities())
  # Does not work due to a bug in the dev server
  # Check SO/questions/13273067/app-engine-python-development-server-taskqueue-backend
  #suite.addTest(BackendTaskTest())
  return suite
