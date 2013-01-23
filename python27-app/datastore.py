try:
  import json
except ImportError:
  import simplejson as json

from google.appengine.ext import webapp, db
import uuid
import webapp2
import wsgiref

class Project(db.Model):
  project_id = db.StringProperty(required=True)
  name = db.StringProperty(required=True)
  description = db.StringProperty(required=True)
  rating = db.IntegerProperty(required=True)
  license = db.StringProperty(required=True)

class Module(db.Model):
  module_id = db.StringProperty(required=True)
  name = db.StringProperty(required=True)
  description = db.StringProperty(required=True)

class Counter(db.Model):
  counter = db.IntegerProperty(required=True)

def serialize(entity):
  dict = {'name': entity.name, 'description': entity.description}
  if isinstance(entity, Project):
    dict['project_id'] = entity.project_id
    dict['type'] = 'project'
    dict['rating'] = entity.rating
    dict['license'] = entity.license
  elif isinstance(entity, Module):
    dict['module_id'] = entity.module_id
    dict['type'] = 'module'
  else:
    dict['type'] = 'unknown'
  return dict

class ProjectHandler(webapp2.RequestHandler):
    def get(self):
      id = self.request.get('id')
      name = self.request.get('name')
      if id is None or id.strip() == '':
        if name is not None and len(name) > 0:
          query = db.GqlQuery("SELECT * FROM Project WHERE name = '%s'" % name)
        else:
          query = db.GqlQuery("SELECT * FROM Project")
      else:
        query = db.GqlQuery("SELECT * FROM Project WHERE "
                            "project_id = '%s'" % str(id))

      data = []
      for result in query:
        data.append(result)
      self.response.headers['Content-Type'] = "application/json"
      self.response.out.write(json.dumps(data, default=serialize))

    def post(self):
      project_id = str(uuid.uuid1())
      project_name = self.request.get('name')
      project = Project(project_id=project_id,
        name=project_name,
        rating=int(self.request.get('rating')),
        description=self.request.get('description'),
        license=self.request.get('license'),
        key_name=project_name)
      project.put()
      self.response.headers['Content-Type'] = "application/json"
      self.response.set_status(201)
      self.response.out.write(
        json.dumps({ 'success' : True, 'project_id' : project_id }))

    def delete(self):
      db.delete(Project.all())

class ModuleHandler(webapp2.RequestHandler):
  def get(self):
    id = self.request.get('id')
    if id is None or id.strip() == '':
      query = db.GqlQuery("SELECT * FROM Module")
    else:
      query = db.GqlQuery("SELECT * FROM Module WHERE "
                          "module_id = '%s'" % str(id))

    data = []
    for result in query:
      data.append(result)
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps(data, default=serialize))

  def post(self):
    project_id = self.request.get('project_id')
    query = db.GqlQuery("SELECT * FROM Project WHERE "
                        "project_id = '%s'" % str(project_id))
    module_id = str(uuid.uuid1())
    module_name = self.request.get('name')
    module = Module(module_id=module_id,
      name=module_name,
      description=self.request.get('description'),
      parent=query[0],
      key_name=module_name)
    module.put()
    self.response.headers['Content-Type'] = "application/json"
    self.response.set_status(201)
    self.response.out.write(
      json.dumps({ 'success' : True, 'module_id' : module_id }))

  def delete(self):
    db.delete(Module.all())

class ProjectModuleHandler(webapp2.RequestHandler):
  def get(self):
    project_id = self.request.get('project_id')
    project_query = db.GqlQuery("SELECT * FROM Project WHERE "
                                "project_id = '%s'" % project_id)
    q = db.Query()
    q.ancestor(project_query[0])
    data = []
    for entity in q:
      data.append(entity)
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps(data, default=serialize))

class ProjectKeyHandler(webapp2.RequestHandler):
  def get(self):
    project_id = self.request.get('project_id')
    ancestor = self.request.get('ancestor')
    project_query = db.GqlQuery("SELECT * FROM Project WHERE "
                                "project_id = '%s'" % project_id)
    q = db.Query()
    if ancestor is not None and ancestor == 'true':
      q.ancestor(project_query[0])
    if self.request.get('comparator') == 'ge':
      q.filter('__key__ >=', project_query[0])
    elif self.request.get('comparator') == 'gt':
      q.filter('__key__ >', project_query[0])
    else:
      raise Exception('Unsupported comparator')

    data = []
    for entity in q:
      if isinstance(entity, Project) or isinstance(entity, Module):
        data.append(entity)
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps(data, default=serialize))

class EntityNameHandler(webapp2.RequestHandler):
  def get(self):
    project_name = self.request.get('project_name')
    module_name = self.request.get('module_name')
    if project_name is not None and len(project_name) > 0:
      if module_name is not None and len(module_name) > 0:
        project_query = db.GqlQuery("SELECT * FROM Project WHERE "
                                    "name = '%s'" % project_name)
        entity = Module.get_by_key_name(module_name, parent=project_query[0])
      else:
        entity = Project.get_by_key_name(project_name, parent=None)
      self.response.headers['Content-Type'] = "application/json"
      self.response.out.write(json.dumps(entity, default=serialize))
    else:
      raise Exception('Missing parameters')

class ProjectRatingHandler(webapp2.RequestHandler):
  def get(self):
    rating = self.request.get('rating')
    comparator = self.request.get('comparator')
    limit = self.request.get('limit')
    desc = self.request.get('desc')
    q = Project.all()
    if comparator is None or comparator == '' or comparator == 'eq':
      q.filter('rating = ', int(rating))
    elif comparator == 'gt':
      q.filter('rating > ', int(rating))
    elif comparator == 'ge':
      q.filter('rating >= ', int(rating))
    elif comparator == 'lt':
      q.filter('rating < ', int(rating))
    elif comparator == 'le':
      q.filter('rating <= ', int(rating))
    elif comparator == 'ne':
      q.filter('rating != ', int(rating))
    else:
      raise Exception('Unsupported comparator')

    if desc is not None and desc == 'true':
      q.order('-rating')

    if limit is not None and len(limit) > 0:
      q = q.fetch(int(limit))

    data = []
    for entity in q:
      data.append(entity)
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps(data, default=serialize))

class ProjectFieldHandler(webapp2.RequestHandler):
  def get(self):
    fields = self.request.get('fields')
    gql = self.request.get('gql')
    rate_limit = self.request.get('rate_limit')
    if gql is not None and gql == 'true':
      q = db.GqlQuery("SELECT %s FROM Project" % fields)
    else:
      field_tuple = tuple(fields.split(','))
      q = db.Query(Project, projection=field_tuple)
      if rate_limit is not None and len(rate_limit) > 0 and 'rating' in field_tuple:
        q.filter('rating >= ', int(rate_limit))

    data = []
    for entity in q:
      data.append(entity)
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps(data, default=serialize))

class ProjectBrowserHandler(webapp2.RequestHandler):
  def get(self):
    cursor_str = self.request.get('cursor')
    q = Project.all()
    if cursor_str:
      q.with_cursor(cursor_str)

    result = q.fetch(1)
    cursor = q.cursor()
    self.response.headers['Content-Type'] = "application/json"
    if len(result) == 1:
      self.response.out.write(
        json.dumps({ 'project' :  result[0].name, 'next' : cursor }))
    else:
      self.response.out.write(
        json.dumps({ 'project' :  None, 'next' : None }))

class ProjectFilterHandler(webapp2.RequestHandler):
  def get(self):
    license = self.request.get('license')
    rate_limit = self.request.get('rate_limit')
    q = db.GqlQuery("SELECT * FROM Project WHERE license = '%s' " \
                    "AND rating >= %s" % (license, rate_limit))
    data = []
    for entity in q:
      data.append(entity)
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps(data, default=serialize))

class TransactionHandler(webapp2.RequestHandler):
  def increment_counter(self, key, amount):
    counter = Counter.get_by_key_name(key)
    if counter is None:
      counter = Counter(key_name=key, counter=0)

    for i in range(0,amount):
      counter.counter += 1
      if counter.counter == 5:
        raise Exception('Mock Exception')
      counter.put()

  def increment_counters(self, key, amount):
    backup = key + '_backup'
    counter1 = Counter.get_by_key_name(key)
    counter2 = Counter.get_by_key_name(backup)
    if counter1 is None:
      counter1 = Counter(key_name=key, counter=0)
      counter2 = Counter(key_name=backup, counter=0)

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
        xg_on = db.create_transaction_options(xg=True)
        db.run_in_transaction_options(xg_on,
          self.increment_counters, key, int(amount))
        counter1 = Counter.get_by_key_name(key)
        counter2 = Counter.get_by_key_name(key + '_backup')
        status = {
          'success' : True,
          'counter' : counter1.counter,
          'backup' : counter2.counter
        }
      except Exception:
        counter1 = Counter.get_by_key_name(key)
        counter2 = Counter.get_by_key_name(key + '_backup')
        status = {
          'success' : False,
          'counter' : counter1.counter,
          'backup' : counter2.counter
        }
    else:
      try:
        db.run_in_transaction(self.increment_counter, key, int(amount))
        counter = Counter.get_by_key_name(key)
        status = { 'success' : True, 'counter' : counter.counter }
      except Exception:
        counter = Counter.get_by_key_name(key)
        status = { 'success' : False, 'counter' : counter.counter }
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps(status))

  def delete(self):
    db.delete(Counter.all())

"""
  This test will create Company, Employee and PhoneNumber
Entities where each employee has the same parent Company 
and each Employee is the parent of a unique PhoneNumber.
  We query all Employees, in increments of 1 result using cursors, 
and make sure it is the correct type, hasn't been seen already and
that the total number of results is correct.
"""
class ComplexCursorHandler(webapp2.RequestHandler):
  def get(self):
    status = {'success' : True }
    self.response.headers['Content-Type'] = "application/json"
    try:
      num_employees = 4
      seen_entities = set() 
      self.set_up_data()
      query = Employee.all()
      result_list = query.fetch(1)
      ctr = 0
      while len(result_list) == 1:
        result = result_list[0]
        if result.__class__.__name__ != "Employee":
          raise Exception('Unexpected kind from query')
        if result.key().id() in seen_entities:
          raise Exception('Saw same result twice')
        seen_entities.add(result.key().id()) 
        ctr = ctr + 1
        cursor = query.cursor()
        query.with_cursor(cursor)
        result_list = query.fetch(1)
      if ctr != num_employees: 
        raise Exception('Did not retrieve ' + str(num_employees) + ' Employees')
    except Exception:
      status = {'success' : False}  
      self.response.out.write(json.dumps(status))
      raise
    finally:
      self.clean_up_data()
    
    self.response.out.write(json.dumps(status))

  def set_up_data(self):
    company = Company(name = "AppScale")
    company.put()  
    
    employee1 = Employee(name = "A", parent = company)
    employee1.put()
    employee2 = Employee(name = "B", parent = company)
    employee2.put()
    employee3 = Employee(name = "C", parent = company)
    employee3.put()
    employee4 = Employee(name = "D", parent = company)
    employee4.put()

    pn1 = PhoneNumber(work = "1111111111", parent = employee1)
    pn1.put()
    pn2 = PhoneNumber(work = "2222222222", parent = employee2)
    pn2.put()
    pn3 = PhoneNumber(work = "3333333333", parent = employee3)
    pn3.put()
    pn4 = PhoneNumber(work = "4444444444", parent = employee4)
    pn4.put()
    
  def clean_up_data(self):
    db.delete(Company.all())
    db.delete(Employee.all())
    db.delete(PhoneNumber.all())

class Employee(db.Model):
  name = db.StringProperty(required=True)

class Company(db.Model):
  name = db.StringProperty(required=True)

class PhoneNumber(db.Model):
  work = db.StringProperty(required=True)

application = webapp.WSGIApplication([
  ('/python/datastore/project', ProjectHandler),
  ('/python/datastore/module', ModuleHandler),
  ('/python/datastore/project_modules', ProjectModuleHandler),
  ('/python/datastore/project_keys', ProjectKeyHandler),
  ('/python/datastore/entity_names', EntityNameHandler),
  ('/python/datastore/project_ratings', ProjectRatingHandler),
  ('/python/datastore/project_fields', ProjectFieldHandler),
  ('/python/datastore/project_filter', ProjectFilterHandler),
  ('/python/datastore/project_cursor', ProjectBrowserHandler),
  ('/python/datastore/complex_cursor', ComplexCursorHandler),
  ('/python/datastore/transactions', TransactionHandler),
], debug=True)

if __name__ == '__main__':
  wsgiref.handlers.CGIHandler().run(application)
