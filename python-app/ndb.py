import json
import wsgiref
from google.appengine.ext import ndb, webapp
import webapp2

__author__ = 'hiranya'

class NDBProject(ndb.Model):
  name = ndb.StringProperty(required=True)
  description = ndb.StringProperty(required=True)
  rating = ndb.IntegerProperty(required=True)
  license = ndb.StringProperty(required=True)

class NDBModule(ndb.Model):
  name = ndb.StringProperty(required=True)
  description = ndb.StringProperty(required=True)

class NDBCounter(ndb.Model):
  counter = ndb.IntegerProperty(required=True)

def serialize(entity):
  dict = {'name': entity.name, 'description': entity.description}
  if isinstance(entity, NDBProject):
    dict['project_id'] = entity.key.urlsafe()
    dict['type'] = 'project'
    dict['rating'] = entity.rating
    dict['license'] = entity.license
  elif isinstance(entity, NDBModule):
    dict['module_id'] = entity.key.urlsafe()
    dict['type'] = 'module'
  else:
    dict['type'] = 'unknown'
  return dict

class NDBProjectHandler(webapp2.RequestHandler):
  def get(self):
    id = self.request.get('id')
    if id is None or id.strip() == '':
      entities = NDBProject.query()
    else:
      key = ndb.Key(urlsafe=id)
      entities = [ key.get() ]

    data = []
    for result in entities:
      data.append(result)
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps(data, default=serialize))

  def post(self):
    project_name = self.request.get('name')
    project = NDBProject(name=project_name, rating=int(self.request.get('rating')),
      description=self.request.get('description'), license=self.request.get('license'))
    project_key = project.put()
    self.response.headers['Content-Type'] = "application/json"
    self.response.set_status(201)
    self.response.out.write(json.dumps({ 'success' : True, 'project_id' : project_key.urlsafe() }))

  def delete(self):
    q = NDBProject.query()
    for entity in q:
      entity.key.delete()

class NDBModuleHandler(webapp2.RequestHandler):
  def get(self):
    id = self.request.get('id')
    if id is None or id.strip() == '':
      query = NDBModule.query()
    else:
      query = [ ndb.Key(urlsafe=id).get() ]

    data = []
    for result in query:
      data.append(result)
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps(data, default=serialize))

  def post(self):
    project_id = self.request.get('project_id')
    project_key = ndb.Key(urlsafe=project_id)
    module_name = self.request.get('name')
    module = NDBModule(name=module_name, description=self.request.get('description'), parent=project_key)
    module_id = module.put()
    self.response.headers['Content-Type'] = "application/json"
    self.response.set_status(201)
    self.response.out.write(json.dumps({ 'success' : True, 'module_id' : module_id.urlsafe() }))

  def delete(self):
    q = NDBModule.query()
    for entity in q:
      entity.key.delete()

class NDBTransactionHandler(webapp2.RequestHandler):
  @ndb.transactional
  def increment_counter(self, key, amount):
    counter = NDBCounter.get_by_id(key)
    if counter is None:
      counter = NDBCounter(id=key, counter=0)

    for i in range(0,amount):
      counter.counter += 1
      if counter.counter == 5:
        raise Exception('Mock Exception')
      counter.put()

  @ndb.transactional(xg=True)
  def increment_counters(self, key, amount):
    backup = key + '_backup'
    counter1 = NDBCounter.get_by_id(key)
    counter2 = NDBCounter.get_by_id(backup)
    if counter1 is None:
      counter1 = NDBCounter(id=key, counter=0)
      counter2 = NDBCounter(id=backup, counter=0)

    for i in range(0,amount):
      counter1.counter += 1
      counter2.counter += 1
      if counter1.counter == 5:
        raise Exception('Mock Exception')
      counter1.put()
      counter2.put()

  def get(self):
    key = self.request.get('key')
    amount = self.request.get('amount')
    xg = self.request.get('xg')
    if xg is not None and xg == 'true':
      try:
        self.increment_counters(key, int(amount))
        counter1 = NDBCounter.get_by_id(key)
        counter2 = NDBCounter.get_by_id(key + '_backup')
        status = { 'success' : True, 'counter' : counter1.counter, 'backup' : counter2.counter }
      except Exception as e:
        counter1 = NDBCounter.get_by_id(key)
        counter2 = NDBCounter.get_by_id(key + '_backup')
        status = { 'success' : False, 'counter' : counter1.counter, 'backup' : counter2.counter }
    else:
      try:
        self.increment_counter(key, int(amount))
        counter = NDBCounter.get_by_id(key)
        status = { 'success' : True, 'counter' : counter.counter }
      except Exception:
        counter = NDBCounter.get_by_id(key)
        status = { 'success' : False, 'counter' : counter.counter }
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps(status))

application = webapp.WSGIApplication([
  ('/python/ndb/project', NDBProjectHandler),
  ('/python/ndb/module', NDBModuleHandler),
  ('/python/ndb/transactions', NDBTransactionHandler),
], debug=True)

if __name__ == '__main__':
  wsgiref.handlers.CGIHandler().run(application)