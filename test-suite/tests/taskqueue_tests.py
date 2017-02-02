import datetime
import json
import uuid
from time import sleep

from hawkeye_utils import HawkeyeTestCase
from hawkeye_test_runner import HawkeyeTestSuite


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

class QueueExistsTest(HawkeyeTestCase):
  def tearDown(self):
    self.http_delete('/taskqueue/pull')

  def run_hawkeye_test(self):
    response = self.http_get('/taskqueue/exists')
    self.assertEquals(response.status, 200)

    queue_info = json.loads(response.payload)

    # Expected Queues:
    # 'default', 'hawkeyepython-PushQueue-0', 'hawkeyepython-PullQueue-0'
    self.assertEquals(len(queue_info['queues']), 3)
    self.assertEquals(queue_info['exists'], [True, True, True])

class QueueStatisticsTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/taskqueue/counter?stats=true')
    self.assertEquals(response.status, 200)
    task_info = json.loads(response.payload)
    self.assertEquals(task_info['queue'], 'default')

class PullQueueTest(HawkeyeTestCase):
  def setup(self):
    self.key = str(uuid.uuid1())
    self.key_async = str(uuid.uuid1())

  def tearDown(self):
    self.http_delete('/taskqueue/pull')

  def run_hawkeye_test(self):
    self.setup()
    self.run_insert_test()
    self.run_lease_by_tag_and_delete_test()
    self.run_lease_and_delete_test()

  def run_insert_test(self):
    # Add pull task.
    response = self.http_post('/taskqueue/pull', 'key={0}&action=add'.\
      format(self.key))
    result = json.loads(response.payload)
    self.assertEquals(response.status, 200)
    self.assertTrue(result['success'])

    # Add pull task (async).
    response = self.http_post('/taskqueue/pull', 'key={0}&action=add_async'.\
      format(self.key_async))
    result = json.loads(response.payload)
    self.assertEquals(response.status, 200)
    self.assertTrue(result['success'])

  def run_lease_and_delete_test(self):
    # Lease and delete.
    start = datetime.datetime.now()
    end = start + datetime.timedelta(0, 30)
    while True:
      response = self.http_get('/taskqueue/pull?action=lease')
      self.assertEquals(response.status, 200)
      task_info = json.loads(response.payload)

      if len(task_info['tasks']) == 1 and self.key in task_info['tasks']:
        break

      if datetime.datetime.now() > end:
        self.fail('Pull queue lease_tasks operation deadline exceeded with no '
                  'result')
      else:
        sleep(2)

  def run_lease_by_tag_and_delete_test(self):
    # Lease by tag and delete by name.
    start = datetime.datetime.now()
    end = start + datetime.timedelta(0, 30)
    while True:
      response = self.http_get('/taskqueue/pull?action=lease_by_tag&tag=newest')
      self.assertEquals(response.status, 200)
      task_info = json.loads(response.payload)

      if len(task_info['tasks']) == 1 and self.key_async in task_info['tasks']:
        break

      if datetime.datetime.now() > end:
        self.fail('Pull queue lease_by_tag operation deadline exceeded with no '
                  'result')
      else:
        sleep(2)

class LeaseModificationTest(HawkeyeTestCase):
  def tearDown(self):
    self.http_delete('/taskqueue/pull')

  def run_hawkeye_test(self):
    response = self.http_get('/taskqueue/pull/lease_modification')
    self.assertEquals(response.status, 200)

class BriefLeaseTest(HawkeyeTestCase):
  """ Ensures the same task is not leased twice in the same request. """
  def tearDown(self):
    self.http_delete('/taskqueue/pull')

  def run_hawkeye_test(self):
    response = self.http_get('/taskqueue/pull/brief_lease')
    self.assertEquals(response.status, 200)

class RESTPullQueueTest(HawkeyeTestCase):
  def tearDown(self):
    self.http_delete('/taskqueue/pull/rest')

  def run_hawkeye_test(self):
    # Retrieve default Pull Queue information.
    response = self.http_get('/taskqueue/pull/rest?test=get-queue')
    task_info = json.loads(response.payload)
    self.assertEquals(response.status, 200)
    self.assertTrue(task_info['success'])

    # Retrieve default Pull Queue information with app prefix (e.g. s~app-name).
    response = self.http_get('/taskqueue/pull/rest?test=get-queue&prefix=true')
    task_info = json.loads(response.payload)
    self.assertEquals(response.status, 200)
    self.assertTrue(task_info['success'])

    # List all enqueued Pull tasks. Should return nothing.
    response = self.http_get('/taskqueue/pull/rest?test=list')
    task_info = json.loads(response.payload)
    self.assertEquals(response.status, 200)
    self.assertTrue(task_info['success'])
    self.assertIsNone(task_info['tasks'])

    # Lease Pull tasks. Should return nothing.
    response = self.http_post('/taskqueue/pull/rest', 'test=lease')
    task_info = json.loads(response.payload)
    self.assertEquals(response.status, 200)
    self.assertTrue(task_info['success'])
    self.assertIsNone(task_info['tasks'])

    key = str(uuid.uuid1())

    # Insert Pull task with tag 'oldest'.
    response = self.http_post('/taskqueue/pull/rest',
                              'key={0}&test=insert&tag=oldest'.format(key))
    task_info = json.loads(response.payload)
    self.assertEquals(response.status, 200)
    self.assertTrue(task_info['success'])

    # Retrieve Pull task.
    response = self.http_get('/taskqueue/pull/rest?key={0}&test=get'.
      format(key))
    task_info = json.loads(response.payload)
    self.assertEquals(response.status, 200)
    self.assertTrue(task_info['success'])

    # Insert Pull task with same ID should fail.
    response = self.http_post('/taskqueue/pull/rest',
                              'key={0}&test=insert'.format(key))
    task_info = json.loads(response.payload)
    self.assertEquals(response.status, 400)
    self.assertFalse(task_info['success'])

    # Insert another Pull task with tag 'oldest'.
    oldest_tag_key = str(uuid.uuid1())
    response = self.http_post(
      '/taskqueue/pull/rest',
      'key={0}&test=insert&tag=oldest'.format(oldest_tag_key)
    )
    task_info = json.loads(response.payload)
    self.assertEquals(response.status, 200)
    self.assertTrue(task_info['success'])

    # Insert Pull task with tag 'newest'.
    newest_tag_key = str(uuid.uuid1())
    response = self.http_post(
      '/taskqueue/pull/rest',
      'key={0}&test=insert&tag=newest'.format(newest_tag_key))
    task_info = json.loads(response.payload)
    self.assertEquals(response.status, 200)
    self.assertTrue(task_info['success'])

    # List all enqueued Pull Tasks.
    response = self.http_get('/taskqueue/pull/rest?test=list')
    task_info = json.loads(response.payload)
    self.assertEquals(response.status, 200)
    self.assertTrue(task_info['success'])
    self.assertEquals(len(task_info['tasks']), 3)

    # Lease Pull tasks with tag 'newest'.
    response = self.http_post(
      '/taskqueue/pull/rest',
      'test=lease&groupByTag=true&tag=newest'
    )
    task_info = json.loads(response.payload)
    tasks = \
      [(task['id'], task['leaseTimestamp']) for task in task_info['tasks']]
    self.assertEquals(response.status, 200)
    self.assertTrue(task_info['success'])
    self.assertEquals(len(task_info['tasks']), 1)

    # Update/Patch Pull tasks that are leased out of a TaskQueue.
    for index, task in enumerate(tasks):
      # Alternate between update and patch methods.
      patch = True if index%2 else False

      response = self.http_post(
        '/taskqueue/pull/rest',
        'key={0}&test=update&leaseTimestamp={1}&patch={2}'.format(task[0],
                                                                  task[1],
                                                                  patch))
      task_info = json.loads(response.payload)
      self.assertEquals(response.status, 200)
      self.assertTrue(task_info['success'])

      expected_eta = datetime.datetime.\
        fromtimestamp(long(task[1])/1000000.0)+datetime.timedelta(seconds=60)
      response_eta = datetime.datetime.\
        fromtimestamp(long(task_info['task']['leaseTimestamp'])/1000000.0)
      self.assertLess(abs(response_eta-expected_eta).total_seconds(), 60)

    # Test default Pull Queue statistics.
    response = self.http_get('/taskqueue/pull/rest?'
                             'test=get-queue&getStats=true')
    task_info = json.loads(response.payload)
    self.assertEquals(response.status, 200)
    self.assertTrue(task_info['success'])
    self.assertIn('stats', task_info['queue'])
    self.assertEquals(task_info['queue']['stats']['totalTasks'], 3)
    self.assertEquals(task_info['queue']['stats']['leasedLastMinute'], 1)
    self.assertEquals(task_info['queue']['stats']['leasedLastHour'], 1)

    # List all enqueued Pull Tasks, leased/non-leased/expired.
    response = self.http_get('/taskqueue/pull/rest?test=list')
    task_info = json.loads(response.payload)
    self.assertEquals(response.status, 200)
    self.assertTrue(task_info['success'])
    self.assertEquals(len(task_info['tasks']), 3)

    # Lease Pull tasks with implicit tag 'oldest'.
    response = self.http_post(
      '/taskqueue/pull/rest',
      'test=lease&groupByTag=true'
    )
    task_info = json.loads(response.payload)
    self.assertEquals(response.status, 200)
    self.assertTrue(task_info['success'])
    self.assertEquals(len(task_info['tasks']), 2)

    # Delete all Pull tasks.
    response = self.http_post('/taskqueue/pull/rest',
                              'key={0}&test=delete'.format(key))
    task_info = json.loads(response.payload)
    self.assertEquals(response.status, 200)
    self.assertTrue(task_info['success'])

    response = self.http_post('/taskqueue/pull/rest',
                              'key={0}&test=delete'.format(oldest_tag_key))
    task_info = json.loads(response.payload)
    self.assertEquals(response.status, 200)
    self.assertTrue(task_info['success'])

    response = self.http_post('/taskqueue/pull/rest',
                              'key={0}&test=delete'.format(newest_tag_key))
    task_info = json.loads(response.payload)
    self.assertEquals(response.status, 200)
    self.assertTrue(task_info['success'])

    response = self.http_post('/taskqueue/pull/rest', 'test=payload-validity')
    self.assertEquals(response.status, 200)


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
    response = self.http_post('/taskqueue/clean_up', '')
    self.assertEquals(response.status, 200)

def suite(lang):
  suite = HawkeyeTestSuite('Task Queue Test Suite', 'taskqueue')
  suite.addTest(QueueExistsTest())
  suite.addTest(PushQueueTest())
  suite.addTest(DeferredTaskTest())
  suite.addTest(QueueStatisticsTest())
  suite.addTest(PullQueueTest())
  suite.addTest(LeaseModificationTest())
  suite.addTest(TaskRetryTest())
  suite.addTest(TaskEtaTest())
  suite.addTest(BriefLeaseTest())

  if lang == 'python':
    suite.addTest(RESTPullQueueTest())
    suite.addTest(TransactionalTaskTest())
    suite.addTest(TransactionalFailedTaskTest())
    suite.addTest(CleanUpTaskEntities())

  # Does not work due to a bug in the dev server
  # Check SO/questions/13273067/app-engine-python-development-server-taskqueue-backend
  #suite.addTest(BackendTaskTest())
  return suite
