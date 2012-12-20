try:
  import json
except ImportError:
  import simplejson as json

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
  dict = {}
  if isinstance(entity, NDBProject):
    dict['project_id'] = entity.key.urlsafe()
    dict['type'] = 'project'
    if len(entity._projection) == 0 or 'name' in entity._projection:
      dict['name'] = entity.name
    else:
      dict['name'] = None

    if len(entity._projection) == 0 or 'description' in entity._projection:
      dict['description'] = entity.description
    else:
      dict['description'] = None

    if len(entity._projection) == 0 or 'rating' in entity._projection:
      dict['rating'] = entity.rating
    else:
      dict['rating'] = None

    if len(entity._projection) == 0 or 'license' in entity._projection:
      dict['license'] = entity.license
    else:
      dict['license'] = None
  elif isinstance(entity, NDBModule):
    dict['name'] = entity.name
    dict['description'] = entity.description
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

class NDBProjectModuleHandler(webapp2.RequestHandler):
  def get(self):
    project_id = self.request.get('project_id')
    q = NDBModule.query(ancestor=ndb.Key(urlsafe=project_id))
    data = []
    for entity in q:
      data.append(entity)
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps(data, default=serialize))

class NDBProjectRatingHandler(webapp2.RequestHandler):
  def get(self):
    rating = self.request.get('rating')
    comparator = self.request.get('comparator')
    limit = self.request.get('limit')
    desc = self.request.get('desc')
    if comparator is None or comparator == '' or comparator == 'eq':
      q = NDBProject.query(NDBProject.rating == int(rating))
    elif comparator == 'gt':
      q = NDBProject.query(NDBProject.rating > int(rating))
    elif comparator == 'ge':
      q = NDBProject.query(NDBProject.rating >= int(rating))
    elif comparator == 'lt':
      q = NDBProject.query(NDBProject.rating < int(rating))
    elif comparator == 'le':
      q = NDBProject.query(NDBProject.rating <= int(rating))
    elif comparator == 'ne':
      q = NDBProject.query(NDBProject.rating != int(rating))
    else:
      raise Exception('Unsupported comparator')

    if desc is not None and desc == 'true':
      q = q.order(-NDBProject.rating)

    if limit is not None and len(limit) > 0:
      q = q.fetch(int(limit))

    data = []
    for entity in q:
      data.append(entity)
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps(data, default=serialize))

class NDBProjectFieldHandler(webapp2.RequestHandler):
  def get(self):
    fields = self.request.get('fields')
    rate_limit = self.request.get('rate_limit')
    field_tuple = fields.split(',')
    if rate_limit is not None and len(rate_limit) > 0 and 'rating' in field_tuple:
      q = NDBProject.query(NDBProject.rating >= int(rate_limit)).fetch(projection=field_tuple)
    else:
      q = NDBProject.query().fetch(projection=field_tuple)

    data = []
    for entity in q:
      data.append(entity)
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps(data, default=serialize))

class NDBProjectFilterHandler(webapp2.RequestHandler):
  def get(self):
    license = self.request.get('license')
    rate_limit = self.request.get('rate_limit')
    gql = self.request.get('gql')
    if gql is not None and gql == 'true':
      q = ndb.gql("SELECT * FROM NDBProject WHERE license = '%s' "\
                      "AND rating >= %s" % (license, rate_limit))
    else:
      q = NDBProject.query(ndb.AND(NDBProject.license == license,
        NDBProject.rating >= int(rate_limit)))

    data = []
    for entity in q:
      data.append(entity)
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps(data, default=serialize))

class NDBProjectLicenseFilterHandler(webapp2.RequestHandler):
  def get(self):
    licenses = self.request.get('licenses')
    q = NDBProject.query(NDBProject.license.IN(licenses.split(',')))
    data = []
    for entity in q:
      data.append(entity)
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps(data, default=serialize))

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
      except Exception:
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

  def delete(self):
    q = NDBCounter.query()
    for entity in q:
      entity.key.delete()

class NDBProjectCursorHandler(webapp2.RequestHandler):
  def get(self):
    cursor_value = self.request.get('cursor')
    cursor = ndb.Cursor(urlsafe=cursor_value)
    project, next_cursor, more = NDBProject.query().fetch_page(1, start_cursor=cursor)
    if len(project) == 1:
      output = { 'project' : project[0].name, 'next' : next_cursor.urlsafe() }
    else:
      output = { 'project' : None, 'next' : None }
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps(output))

application = webapp.WSGIApplication([
  ('/python/ndb/project', NDBProjectHandler),
  ('/python/ndb/module', NDBModuleHandler),
  ('/python/ndb/project_modules', NDBProjectModuleHandler),
  ('/python/ndb/project_ratings', NDBProjectRatingHandler),
  ('/python/ndb/project_fields', NDBProjectFieldHandler),
  ('/python/ndb/project_filter', NDBProjectFilterHandler),
  ('/python/ndb/project_license_filter', NDBProjectLicenseFilterHandler),
  ('/python/ndb/transactions', NDBTransactionHandler),
  ('/python/ndb/project_cursor', NDBProjectCursorHandler),
], debug=True)

if __name__ == '__main__':
  wsgiref.handlers.CGIHandler().run(application)