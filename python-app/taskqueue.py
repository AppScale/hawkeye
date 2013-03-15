import wsgiref
from google.appengine.api import taskqueue
import utils
import datetime

try:
  import json
except ImportError:
  import simplejson as json

from google.appengine.ext import db, webapp, deferred
import webapp2

__author__ = 'hiranya'

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
      statsResult = taskqueue.QueueStatistics.fetch('default')
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
        params={'key': key}, target='hawkeyepython')
    elif defer is not None and defer == 'true':
      deferred.defer(utils.process, key)
    elif get_method is not None and get_method == 'true':
      taskqueue.add(url='/python/taskqueue/worker?key=' + key, method='GET')
    elif eta is not None:
      time_now = datetime.datetime.now()
      eta = time_now + datetime.timedelta(0, long(eta))
      taskqueue.add(url='/python/taskqueue/worker', eta=eta, params={'key': key, 'eta': 'true'})
    else:
      taskqueue.add(url='/python/taskqueue/worker', params={'key': key, 'retry': retry})
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps({ 'status' : True }))

  def delete(self):
    db.delete(utils.TaskCounter.all())

class PullTaskHandler(webapp2.RequestHandler):
  def get(self):
    q = taskqueue.Queue('hawkeyepython-pull-queue')
    tasks = q.lease_tasks(3600, 100)
    result = []
    for task in tasks:
      result.append(task.payload)
    q.delete_tasks(tasks)
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps({ 'tasks' : result }))

  def post(self):
    key = self.request.get('key')
    q = taskqueue.Queue('hawkeyepython-pull-queue')
    q.add([taskqueue.Task(payload=key, method='PULL')])
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps({ 'status' : True }))

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
      utils.process(self.request.get('key'), eta)
    else:
      utils.process(self.request.get('key'))

application = webapp.WSGIApplication([
  ('/python/taskqueue/counter', TaskCounterHandler),
  ('/python/taskqueue/worker', TaskCounterWorker),
  ('/python/taskqueue/pull', PullTaskHandler),
], debug=True)

if __name__ == '__main__':
  wsgiref.handlers.CGIHandler().run(application)



