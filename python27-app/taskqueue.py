import datetime
import time
import urllib
import utils
import webapp2
import wsgiref

from google.appengine.api import taskqueue
from google.appengine.api import urlfetch
from google.appengine.api import urlfetch_errors
from google.appengine.ext import deferred
from google.appengine.ext import db
from google.appengine.ext import webapp

from datastore import SDK_CONSISTENCY_WAIT

try:
  import json
except ImportError:
  import simplejson as json


UPDATED_BY_TXN = "TXN_UPDATE"
UPDATED_BY_TQ = "TQ_UPDATE"

# Default Push Queue.
DEFAULT_PUSH_QUEUE = 'default'

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
  def get(self):
    q = taskqueue.Queue(PULL_QUEUE_NAME)
    tasks = q.lease_tasks(3600, 100)
    result = []
    for task in tasks:
      result.append(task.payload)
    q.delete_tasks(tasks)
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps({ 'tasks' : result }))

  def post(self):
    key = self.request.get('key')
    q = taskqueue.Queue(PULL_QUEUE_NAME)
    q.add([taskqueue.Task(payload=key, method='PULL')])
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps({ 'status' : True }))

  def delete(self):
    q = taskqueue.Queue(PULL_QUEUE_NAME)
    q.purge()

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
        scheme='http',
        host='localhost',
        port='17446',
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
        tasks = json.loads(tq_response.content)['items']
        self.response.out.write(json.dumps({'success': True, 'tasks': tasks}))
        return
      else:
        self.response.set_status(tq_response.status_code)
        self.response.out.write(
          json.dumps({'success': False, 'error': tq_response.content}))
        return

  def post(self):
    key = self.request.get('key', None)
    test = self.request.get('test', None)
    groupByTag = self.request.get('groupByTag', False)
    tag = self.request.get('tag', None)
    patch = self.request.get('patch', False)
    leaseTimestamp = self.request.get('leaseTimestamp', None)

    url_prefix = '{scheme}://{host}:{port}' \
      '/taskqueue/v1beta2/projects/{app_id}/taskqueues/{queue}'.format(
        scheme='http',
        host='localhost',
        port='17446',
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
        tasks = json.loads(tq_response.content)['items']
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

application = webapp.WSGIApplication([
  ('/python/taskqueue/exists', QueueHandler),
  ('/python/taskqueue/counter', TaskCounterHandler),
  ('/python/taskqueue/worker', TaskCounterWorker),
  ('/python/taskqueue/transworker', TransactionalTaskWorker),
  ('/python/taskqueue/trans', TransactionalTaskHandler),
  ('/python/taskqueue/pull', PullTaskHandler),
  ('/python/taskqueue/pull/rest', RESTPullQueueHandler),
  ('/python/taskqueue/clean_up', CleanUpTaskEntities),
], debug=True)

if __name__ == '__main__':
  wsgiref.handlers.CGIHandler().run(application)
