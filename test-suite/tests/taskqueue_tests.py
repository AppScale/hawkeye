import json
from time import sleep
import uuid
import datetime
from hawkeye_utils import HawkeyeTestCase, HawkeyeTestSuite

__author__ = 'hiranya'

class PushQueueTest(HawkeyeTestCase):
  def runTest(self):
    status, headers, payload = self.http_delete('/taskqueue/counter')
    self.assertEquals(status, 200)

    key = str(uuid.uuid1())
    status, headers, payload = self.http_post('/taskqueue/counter',
      'key={0}'.format(key))
    task_info = json.loads(payload)
    self.assertEquals(status, 200)
    self.assertTrue(task_info['status'])
    self.get_and_assert_counter(key, 1)

    status, headers, payload = self.http_post('/taskqueue/counter',
      'key={0}&get=true'.format(key))
    task_info = json.loads(payload)
    self.assertEquals(status, 200)
    self.assertTrue(task_info['status'])
    self.get_and_assert_counter(key, 2)

    for i in range(0, 10):
      status, headers, payload = self.http_post('/taskqueue/counter',
        'key={0}'.format(key))
      task_info = json.loads(payload)
      self.assertEquals(status, 200)
      self.assertTrue(task_info['status'])
    self.get_and_assert_counter(key, 12)

  def get_and_assert_counter(self, key, expected):
    start = datetime.datetime.now()
    end = start + datetime.timedelta(0, 600)
    while True:
      status, headers, payload = self.http_get('/taskqueue/counter?' \
                                               'key={0}'.format(key))
      self.assertTrue(status == 200 or status == 404)
      if status == 200:
        task_info = json.loads(payload)
        if task_info[key] == expected:
          break

      if datetime.datetime.now() > end:
        self.fail('Push queue deadline exceeded with no result')
      else:
        sleep(2)

class DeferredTaskTest(PushQueueTest):
  def runTest(self):
    key = str(uuid.uuid1())
    status, headers, payload = self.http_post('/taskqueue/counter',
      'key={0}&defer=true'.format(key))
    task_info = json.loads(payload)
    self.assertEquals(status, 200)
    self.assertTrue(task_info['status'])
    self.get_and_assert_counter(key, 1)

    status, headers, payload = self.http_post('/taskqueue/counter',
      'key={0}&defer=true'.format(key))
    task_info = json.loads(payload)
    self.assertEquals(status, 200)
    self.assertTrue(task_info['status'])
    self.get_and_assert_counter(key, 2)

    for i in range(0, 10):
      status, headers, payload = self.http_post('/taskqueue/counter',
        'key={0}&defer=true'.format(key))
      task_info = json.loads(payload)
      self.assertEquals(status, 200)
      self.assertTrue(task_info['status'])
    self.get_and_assert_counter(key, 12)

class BackendTaskTest(PushQueueTest):
  def runTest(self):
    key = str(uuid.uuid1())
    status, headers, payload = self.http_post('/taskqueue/counter',
      'key={0}&backend=true'.format(key))
    task_info = json.loads(payload)
    self.assertEquals(status, 200)
    self.assertTrue(task_info['status'])
    self.get_and_assert_counter(key, 1)

    status, headers, payload = self.http_post('/taskqueue/counter',
      'key={0}&backend=true'.format(key))
    task_info = json.loads(payload)
    self.assertEquals(status, 200)
    self.assertTrue(task_info['status'])
    self.get_and_assert_counter(key, 2)

    for i in range(0, 10):
      status, headers, payload = self.http_post('/taskqueue/counter',
        'key={0}&backend=true'.format(key))
      task_info = json.loads(payload)
      self.assertEquals(status, 200)
      self.assertTrue(task_info['status'])
    self.get_and_assert_counter(key, 12)

class QueueStatisticsTest(HawkeyeTestCase):
  def runTest(self):
    status, headers, payload = self.http_get('/taskqueue/counter?stats=true')
    self.assertEquals(status, 200)
    task_info = json.loads(payload)
    self.assertEquals(task_info['queue'], 'default')

class PullQueueTest(HawkeyeTestCase):
  def runTest(self):
    key = str(uuid.uuid1())
    status, headers, payload = self.http_post('/taskqueue/pull',
      'key={0}'.format(key))
    task_info = json.loads(payload)
    self.assertEquals(status, 200)
    self.assertTrue(task_info['status'])

    start = datetime.datetime.now()
    end = start + datetime.timedelta(0, 60)
    while True:
      status, headers, payload = self.http_get('/taskqueue/pull')
      self.assertEquals(status, 200)
      task_info = json.loads(payload)
      if len(task_info['tasks']) == 1 and key in task_info['tasks']:
        break
      if datetime.datetime.now() > end:
        self.fail('Pull queue deadline exceeded with no result')
      else:
        sleep(2)

def suite():
  suite = HawkeyeTestSuite('Task Queue Test Suite', 'taskqueue')
  suite.addTest(PushQueueTest())
  suite.addTest(DeferredTaskTest())
  #suite.addTest(BackendTaskTest())
  suite.addTest(PullQueueTest())
  suite.addTest(QueueStatisticsTest())
  return suite

