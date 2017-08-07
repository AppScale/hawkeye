import datetime
import time
import urllib

import webapp2
from google.appengine.api import taskqueue
from google.appengine.api import urlfetch
from google.appengine.api import urlfetch_errors
from google.appengine.api.taskqueue import TaskLeaseExpiredError
from google.appengine.ext import db
from google.appengine.ext import deferred

import utils
from datastore import SDK_CONSISTENCY_WAIT

try:
  import json
except ImportError:
  import simplejson as json


UPDATED_BY_TXN = "TXN_UPDATE"
UPDATED_BY_TQ = "TQ_UPDATE"

# Default Push Queue.
DEFAULT_PUSH_QUEUE = 'default'

# A small interval to wait for a service.
SMALL_WAIT = 5

# From the GAE docs:
# A queue name can contain uppercase and lowercase letters, numbers,
# and hyphens. The maximum length for a queue name is 100 characters.

# The name of the queue that is used for push queue operations.
PUSH_QUEUE_NAME = "hawkeyepython-PushQueue-0"
# The name of the queue that is used for pull queue operations.
PULL_QUEUE_NAME = "hawkeyepython-PullQueue-0"

# A separate pull queue used for testing the REST API.
REST_PULL_QUEUE = 'rest-pull-queue'


class TaskEntity(db.Model):
  value = db.StringProperty(required=True)


class QueueHandler(webapp2.RequestHandler):
  def get(self):
    results = {'queues': [], 'exists': []}
    self.response.set_status(200)

    # Test default push queue.
    queue = DEFAULT_PUSH_QUEUE
    results['queues'].append(queue)
    try:
      taskqueue.Queue(queue).\
        add(taskqueue.Task(url='/python/taskqueue/clean_up'))
      results['exists'].append(True)
    except taskqueue.UnknownQueueError:
      self.response.set_status(404)
      results['exists'].append(False)

    # Test push queue.
    queue = PUSH_QUEUE_NAME
    results['queues'].append(queue)
    try:
      taskqueue.Queue(queue).\
        add(taskqueue.Task(url='/python/taskqueue/clean_up'))
      results['exists'].append(True)
    except taskqueue.UnknownQueueError:
      self.response.set_status(404)
      results['exists'].append(False)

    # Test pull queue.
    queue = PULL_QUEUE_NAME
    results['queues'].append(queue)
    try:
      taskqueue.Queue(queue).\
        add(taskqueue.Task(payload='this is a fake payload', method='PULL'))
      results['exists'].append(True)
    except taskqueue.UnknownQueueError:
      self.response.set_status(404)
      results['exists'].append(False)

    self.response.out.write(json.dumps(results))

class TaskCounterHandler(webapp2.RequestHandler):
  def get(self):
    key = self.request.get('key')
    stats = self.request.get('stats')
    if key is not None and len(key) > 0:
      counter = utils.TaskCounter.get_by_key_name(key)
      if counter is not None:
        self.response.headers['Content-Type'] = "application/json"
        self.response.out.write(json.dumps({ key : counter.count }))
      else:
        self.response.set_status(404)
    elif stats is not None and stats == 'true':
      statsResult = taskqueue.QueueStatistics.fetch(DEFAULT_PUSH_QUEUE)
      self.response.headers['Content-Type'] = "application/json"
      result = {
        'queue' : statsResult.queue.name,
        'tasks' : statsResult.tasks,
        'oldest_eta' : statsResult.oldest_eta_usec,
        'exec_last_minute' : statsResult.executed_last_minute,
        'in_flight' : statsResult.in_flight,
      }
      self.response.out.write(json.dumps(result))

  def post(self):
    key = self.request.get('key')
    get_method = self.request.get('get')
    defer = self.request.get('defer')
    retry = self.request.get('retry')
    backend = self.request.get('backend')
    eta = self.request.get('eta')

    if backend is not None and backend == 'true':
      taskqueue.add(url='/python/taskqueue/worker',
        params={'key': key}, target='hawkeyepython', queue_name=DEFAULT_PUSH_QUEUE)
    elif defer is not None and defer == 'true':
      deferred.defer(utils.process, key)
    elif get_method is not None and get_method == 'true':
      taskqueue.add(url='/python/taskqueue/worker?key=' + key, method='GET',
        queue_name=DEFAULT_PUSH_QUEUE)
    elif eta is not None and eta != '':
      time_now = datetime.datetime.now()
      eta = time_now + datetime.timedelta(0, long(eta))
      taskqueue.add(url='/python/taskqueue/worker', eta=eta, params={'key': key,
        'eta': 'true'}, queue_name=DEFAULT_PUSH_QUEUE)
    else:
      taskqueue.add(url='/python/taskqueue/worker', params={'key': key,
        'retry': retry}, queue_name=DEFAULT_PUSH_QUEUE)
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps({ 'status' : True }))

  def delete(self):
    db.delete(utils.TaskCounter.all())

class PullTaskHandler(webapp2.RequestHandler):
  QUEUE = taskqueue.Queue(PULL_QUEUE_NAME)

  def get(self):
    action = self.request.get('action', None)
    tag = self.request.get('tag', None)

    self.response.headers['Content-Type'] = "application/json"
    result = []
    if action == "lease":
      tasks = self.QUEUE.lease_tasks(3600, 100)
      for task in tasks:
        result.append(task.payload)
        rpc = self.QUEUE.delete_tasks_async(task)
        if rpc:
          rpc.wait()
          deleted_task = rpc.get_result()
          if not deleted_task.was_deleted:
            self.response.out.write('delete_tasks_async failed')
            return
    elif action == "lease_by_tag":
      tasks = self.QUEUE.lease_tasks_by_tag(3600, 100, tag=tag)
      for task in tasks:
        result.append(task.payload)
        deleted_task = self.QUEUE.delete_tasks_by_name(task.name)
        if not deleted_task.was_deleted:
          self.response.out.write('delete_task_by_name failed')
          return

    self.response.out.write(json.dumps({'success': True, 'tasks': result}))

  def post(self):
    key = self.request.get('key')
    action = self.request.get('action', None)

    if action == "add":
      task = taskqueue.Task(payload=key, method='PULL')
      self.QUEUE.add(task)
      self.response.out.write(json.dumps({'success': True}))
    elif action == "add_async":
      task = taskqueue.Task(payload=key, method="PULL", tag='newest',
        countdown=10)
      rpc = self.QUEUE.add_async(task)
      if rpc is not None:
        rpc.wait()
        task = rpc.get_result()
        if not task.name:
          self.response.write('Task name missing')
        self.response.out.write(json.dumps({'success': True}))
      else:
        self.response.out.write(json.dumps({'success': False}))

  def delete(self):
    self.QUEUE.purge()

class LeaseModificationHandler(webapp2.RequestHandler):
  def get(self):
    payload = 'hello world'
    q = taskqueue.Queue(PULL_QUEUE_NAME)
    q.add([taskqueue.Task(payload=payload, method='PULL')])

    # Account for short delay between add and lease availability in GAE.
    time.sleep(SMALL_WAIT)

    # Make sure the task has been leased for the appropriate time.
    duration = 120
    task = q.lease_tasks(lease_seconds=duration, max_tasks=1)[0]
    tz = task.eta.tzinfo
    expected = datetime.datetime.now(tz) + datetime.timedelta(seconds=duration)
    try:
      assert abs((task.eta - expected).total_seconds()) < SMALL_WAIT
    except AssertionError:
      self.error(500)
      self.response.write(
        'Initial Lease: ETA={}, Expected={}'.format(task.eta, expected))
      return

    # Make sure the lease time has been modified.
    duration = 2
    q.modify_task_lease(task, lease_seconds=duration)
    expected = datetime.datetime.now(tz) + datetime.timedelta(seconds=duration)
    try:
      assert abs((task.eta - expected).total_seconds()) < SMALL_WAIT
    except AssertionError:
      self.error(500)
      self.response.write(
        'Lease Update: ETA={}, Expected={}'.format(task.eta, expected))
      return

    time.sleep(duration + 1)

    # Make sure the lease can't be modified after expiration.
    try:
      q.modify_task_lease(task, 240)
    except TaskLeaseExpiredError:
      pass
    else:
      self.error(500)
      self.response.write('Task lease was modified after expiration.')

class BriefLeaseHandler(webapp2.RequestHandler):
  def get(self):
    payload = 'hello world'
    q = taskqueue.Queue(PULL_QUEUE_NAME)
    to_add = [taskqueue.Task(payload=payload, method='PULL'),
              taskqueue.Task(payload=payload, method='PULL')]
    q.add(to_add)

    # Account for short delay between add and lease availability in GAE.
    time.sleep(SMALL_WAIT)

    # Only 2 tasks should be leased despite asking for 3.
    duration = .001  # 1 nanosecond.
    tasks = q.lease_tasks(lease_seconds=duration, max_tasks=3)
    if len(tasks) > 2:
      self.error(500)
      self.response.write('Leased: {}, Expected: {}'.format(tasks, to_add))

class RESTPullQueueHandler(webapp2.RequestHandler):
  def get(self):
    key = self.request.get('key', None)
    test = self.request.get('test', None)
    getStats = self.request.get('getStats', False)
    prefix_on = self.request.get('prefix', False)

    app_id = 'hawkeyepython27'
    if prefix_on:
      app_id = 's~{}'.format(app_id)
    url_prefix = '{scheme}://{host}:{port}' \
      '/taskqueue/v1beta2/projects/{app_id}/taskqueues/{queue}'.format(
        scheme='https',
        host=self.request.host.split(':')[0],
        port='8199',
        app_id=app_id,
        queue=REST_PULL_QUEUE)

    # Test pull queue via REST API.
    if test == 'get-queue':
      url = url_prefix
      if getStats:
        url += '?getStats=true'

      self.response.headers['Content-Type'] = "application/json"
      try:
        tq_response = urlfetch.fetch(url, method='GET')
      except urlfetch_errors.DownloadError as download_error:
        self.response.set_status(500)
        self.response.out.write(
          json.dumps({'success': False, 'error': download_error.message}))
        return

      if tq_response.status_code == 200:
        queue = json.loads(tq_response.content)
        self.response.out.write(json.dumps({'success': True, 'queue': queue}))
        return
      else:
        self.response.set_status(tq_response.status_code)
        self.response.out.write(
          json.dumps({'success': False, 'error': tq_response.content}))
        return
    elif test == 'get':
      url = '{url_prefix}/tasks/{task_id}'.format(url_prefix=url_prefix,
                                                  task_id=key)

      self.response.headers['Content-Type'] = "application/json"
      try:
        tq_response = urlfetch.fetch(url, method='GET')
      except urlfetch_errors.DownloadError as download_error:
        self.response.set_status(500)
        self.response.out.write(
          json.dumps({'success': False, 'error': download_error.message}))
        return

      if tq_response.status_code == 200:
        self.response.out.write(json.dumps({'success': True}))
        return
      else:
        self.response.set_status(tq_response.status_code)
        self.response.out.write(
          json.dumps({'success': False, 'error': tq_response.content}))
        return
    elif test == 'list':
      url = '{url_prefix}/tasks'.format(url_prefix=url_prefix)

      self.response.headers['Content-Type'] = "application/json"
      try:
        tq_response = urlfetch.fetch(url, method='GET')
      except urlfetch_errors.DownloadError as download_error:
        self.response.set_status(500)
        self.response.out.write(
          json.dumps({'success': False, 'error': download_error.message}))
        return

      if tq_response.status_code == 200:
        content = json.loads(tq_response.content)
        tasks = None
        if 'items' in content:
          tasks = content['items']
        self.response.out.write(json.dumps({'success': True, 'tasks': tasks}))
        return
      else:
        self.response.set_status(tq_response.status_code)
        self.response.out.write(
          json.dumps({'success': False, 'error': tq_response.content}))
        return
    else:
      self.response.set_status(500)
      self.response.out.write('Test was not specified.')

  def post(self):
    key = self.request.get('key', None)
    test = self.request.get('test', None)
    groupByTag = self.request.get('groupByTag', False)
    tag = self.request.get('tag', None)
    patch = self.request.get('patch', False)
    leaseTimestamp = self.request.get('leaseTimestamp', None)

    url_prefix = '{scheme}://{host}:{port}' \
      '/taskqueue/v1beta2/projects/{app_id}/taskqueues/{queue}'.format(
        scheme='https',
        host=self.request.host.split(':')[0],
        port='8199',
        app_id='hawkeyepython27',
        queue=REST_PULL_QUEUE)

    # Insert a Pull task.
    if test == 'insert':
      url = '{url_prefix}/tasks'.format(url_prefix=url_prefix)
      payload = {"id": key, "payloadBase64": "1234", "retry_count": 1}
      if tag:
        payload['tag'] = tag

      self.response.headers['Content-Type'] = "application/json"
      try:
        tq_response = urlfetch.fetch(url,
                                     payload=json.dumps(payload),
                                     method='POST')
      except urlfetch_errors.DownloadError as download_error:
        self.response.set_status(500)
        self.response.out.write(
          json.dumps({'success': False, 'error': download_error.message}))
        return

      if tq_response.status_code == 200:
        self.response.out.write(json.dumps({'success': True}))
        return
      else:
        self.response.set_status(tq_response.status_code)
        self.response.out.write(
          json.dumps({'success': False, 'error': tq_response.content}))
        return
    elif test == 'lease':
      url = '{url_prefix}/tasks/lease'.format(url_prefix=url_prefix)
      payload = {"leaseSecs": 60, "numTasks": 1000}
      if groupByTag:
        payload['groupByTag'] = groupByTag
        if tag:
          payload['tag'] = tag

      self.response.headers['Content-Type'] = "application/json"
      try:
        tq_response = urlfetch.fetch(
          url,
          payload=urllib.urlencode(payload),
          method='POST',
        )
      except urlfetch_errors.DownloadError as download_error:
        self.response.set_status(500)
        self.response.out.write(
          json.dumps({'success': False, 'error': download_error.message}))
        return

      if tq_response.status_code == 200:
        content = json.loads(tq_response.content)
        tasks = None
        if 'items' in content:
          tasks = content['items']
        self.response.out.write(
          json.dumps({'success': True, 'tasks': tasks}))
        return
      else:
        self.response.set_status(tq_response.status_code)
        self.response.out.write(
          json.dumps({'success': False, 'error': tq_response.content}))
        return
    elif test == 'update':
      url = '{url_prefix}/tasks/{task_id}?newLeaseSeconds={newLeaseSeconds}'.\
        format(url_prefix=url_prefix, task_id=key, newLeaseSeconds=60)
      method = 'POST'
      payload = {
        'id': key,
        'leaseTimestamp': leaseTimestamp
      }
      if patch:
        method = 'PATCH'
        payload['queueName'] = REST_PULL_QUEUE

      self.response.headers['Content-Type'] = "application/json"
      try:
        tq_response = urlfetch.fetch(url,
                                     payload=json.dumps(payload),
                                     method=method)
      except urlfetch_errors.DownloadError as download_error:
        self.response.set_status(500)
        self.response.out.write(
          json.dumps({'success': False, 'error': download_error.message}))
        return

      if tq_response.status_code == 200:
        task_info = json.loads(tq_response.content)
        self.response.out.write(json.dumps({'success': True, 'task': task_info}))
        return
      else:
        self.response.set_status(tq_response.status_code)
        self.response.out.write(
          json.dumps({'success': False, 'error': tq_response.content}))
        return
    elif test == 'delete':
      url = '{url_prefix}/tasks/{task_id}'.format(url_prefix=url_prefix,
                                                  task_id=key)

      self.response.headers['Content-Type'] = "application/json"
      try:
        tq_response = urlfetch.fetch(url, method='DELETE')
      except urlfetch_errors.DownloadError as download_error:
        self.response.set_status(500)
        self.response.out.write(
          json.dumps({'success': False, 'error': download_error.message}))
        return

      if tq_response.status_code == 200:
        self.response.out.write(json.dumps({'success': True}))
        return
      else:
        self.response.set_status(tq_response.status_code)
        self.response.out.write(
          json.dumps({'success': False, 'error': tq_response.content}))
        return
    elif test == 'payload-validity':
      url = '{}/tasks'.format(url_prefix)

      # Payloads containing invalid characters should be rejected.
      payload = {'payloadBase64': 'invalid#payload'}
      result = urlfetch.fetch(url, json.dumps(payload), 'POST')
      if result.status_code != 400:
        self.response.set_status(500)
        error = 'Received {} with invalid payload: {}'.format(
          result.status_code, repr(payload['payloadBase64']))
        self.response.out.write(error)
        return

      # Payloads containing non-urlsafe characters should be rejected.
      payload = {'payloadBase64': '/NDQaWRvMm/1UQ=='}
      result = urlfetch.fetch(url, json.dumps(payload), 'POST')
      if result.status_code != 400:
        self.response.set_status(500)
        error = 'Received {} with invalid payload: {}'.format(
          result.status_code, repr(payload['payloadBase64']))
        self.response.out.write(error)
        return

      # Payloads containing urlsafe replacements should be accepted.
      payload = {'payloadBase64': '_NDQaWRvMm_1UQ=='}
      result = urlfetch.fetch(url, json.dumps(payload), 'POST')
      if result.status_code != 200:
        self.response.set_status(500)
        error = 'Received {} with valid payload: {}'.format(
          result.status_code, repr(payload['payloadBase64']))
        self.response.out.write(error)
        return

      # Payloads with incorrect padding should still be accepted.
      payload = {'payloadBase64': 'asdf123'}
      result = urlfetch.fetch(url, json.dumps(payload), 'POST')
      if result.status_code != 200:
        self.response.set_status(500)
        error = 'Error for payload {}: {}'.format(
          repr(payload['payloadBase64']), result.content)
        self.response.out.write(error)
        return

      task = json.loads(result.content)
      if task['payloadBase64'] != 'asdf120=':
        self.response.set_status(500)
        error = 'Received payload: {}'.format(repr(task['payloadBase64']))
        self.response.out.write(error)
        return
    else:
      self.response.set_status(500)
      self.response.out.write('Test was not specified.')

  def delete(self):
    q = taskqueue.Queue(REST_PULL_QUEUE)
    q.purge()


class TransactionalTaskHandler(webapp2.RequestHandler):
  def post(self):
    def task_txn(key, throw_exception):
      taskqueue.add(url='/python/taskqueue/transworker',
        params={'key': key}, transactional=True, queue_name=DEFAULT_PUSH_QUEUE)
      # Enqueue a task update a key, assert that value
      task_ent = TaskEntity(value=UPDATED_BY_TXN, key_name=key)
      task_ent.put()
      if throw_exception:
        raise
      # Client should poll to see if the task ran correctly

    key = self.request.get('key')

    raise_exception = False
    if self.request.get('raise_exception'):
      raise_exception = True

    assert key != None

    try:
      db.run_in_transaction(task_txn, key, raise_exception)
    except Exception:
      self.response.out.write(json.dumps({'value' : "None"}))
      return
    else:
      value = TaskEntity.get_by_key_name(key).value
      self.response.out.write(json.dumps({'value' : value}))


  def get(self):
    key = self.request.get('key')
    entity = TaskEntity.get_by_key_name(key)
    value = None

    if entity:
      value = entity.value

    self.response.out.write(json.dumps({ 'value' : value}))

class TransactionalTaskWorker(webapp2.RequestHandler):
  def post(self):
    key = self.request.get('key')
    task_ent = TaskEntity.get_by_key_name(key)
    task_ent.value = UPDATED_BY_TQ
    task_ent.put()

class TaskCounterWorker(webapp2.RequestHandler):
  def get(self):
    utils.process(self.request.get('key'))

  def post(self):
    retry = self.request.get('retry')
    failures = self.request.headers.get("X-AppEngine-TaskRetryCount")
    eta_test = self.request.get('eta')
    eta = self.request.headers.get("X-AppEngine-TaskETA")
    if retry == 'true' and failures == "0":
      raise Exception
    elif eta_test == 'true':
      utils.processEta(self.request.get('key'), eta)
    else:
      utils.process(self.request.get('key'))

class CleanUpTaskEntities(webapp2.RequestHandler):
  def post(self):
    batch_size = 200
    while True:
      query = TaskEntity.all()
      entity_batch = query.fetch(batch_size)
      if not entity_batch:
        self.response.set_status(200)
        return
      entities_fetched = len(entity_batch)
      db.delete(entity_batch)
      time.sleep(SDK_CONSISTENCY_WAIT)
      if entities_fetched < batch_size:
        break
    self.response.set_status(200)

urls = [
  ('/python/taskqueue/exists', QueueHandler),
  ('/python/taskqueue/counter', TaskCounterHandler),
  ('/python/taskqueue/worker', TaskCounterWorker),
  ('/python/taskqueue/transworker', TransactionalTaskWorker),
  ('/python/taskqueue/trans', TransactionalTaskHandler),
  ('/python/taskqueue/pull', PullTaskHandler),
  ('/python/taskqueue/pull/rest', RESTPullQueueHandler),
  ('/python/taskqueue/pull/lease_modification', LeaseModificationHandler),
  ('/python/taskqueue/pull/brief_lease', BriefLeaseHandler),
  ('/python/taskqueue/clean_up', CleanUpTaskEntities),
]
