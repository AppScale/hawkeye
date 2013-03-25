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
    put_future = db.put_async(project)
    put_future.get_result()
    self.response.headers['Content-Type'] = "application/json"
    self.response.set_status(201)
    self.response.out.write(
      json.dumps({ 'success' : True, 'project_id' : project_id }))

  def delete(self):
    delete_future = db.delete_async(Project.all())
    delete_future.get_result()

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
    put_future = db.put_async(module)
    put_future.get_result()
    self.response.headers['Content-Type'] = "application/json"
    self.response.set_status(201)
    self.response.out.write(
      json.dumps({ 'success' : True, 'module_id' : module_id }))

  def delete(self):
    delete_future = db.delete_async(Module.all())
    delete_future.get_result()

class ProjectModuleHandler(webapp2.RequestHandler):
  def get(self):
    project_id = self.request.get('project_id')
    order = self.request.get('order')
    q = []

    if order:
      project_query = db.GqlQuery("SELECT * FROM Project WHERE "
                                "project_id = '%s'" % project_id)
      # Create kind query with an ancestor and ordering.
      q = db.Query(Module)
      q.ancestor(project_query[0])
      q.order("-" + order)
    else:
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
        get_future = db.get_async(db.Key.from_path('Module',
          module_name, parent=project_query[0].key()))
        entity = get_future.get_result()
      else:
        get_future = db.get_async(db.Key.from_path('Project',
          project_name, parent=None))
        entity = get_future.get_result()
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
    get_future = db.get_async(db.Key.from_path('Counter', key))
    counter = get_future.get_result()
    if counter is None:
      counter = Counter(key_name=key, counter=0)

    for i in range(0,amount):
      counter.counter += 1
      if counter.counter == 5:
        raise Exception('Mock Exception')
      put_future = db.put_async(counter)
      put_future.get_result()

  def increment_counters(self, key, amount):
    backup = key + '_backup'
    counter1_future = db.get_async(db.Key.from_path('Counter', key))
    counter2_future = db.get_async(db.Key.from_path('Counter', backup))

    counter1 = counter1_future.get_result()
    counter2 = counter2_future.get_result()
    if counter1 is None:
      counter1 = Counter(key_name=key, counter=0)
      counter2 = Counter(key_name=backup, counter=0)

    for i in range(0,amount):
      counter1.counter += 1
      counter2.counter += 1
      if counter1.counter == 5:
        raise Exception('Mock Exception')
      counter1_future = db.put_async(counter1)
      counter2_future = db.put_async(counter2)
      counter1_future.get_result()
      counter2_future.get_result()

  def get(self):
    key = self.request.get('key')
    amount = self.request.get('amount')
    xg = self.request.get('xg')
    if xg is not None and xg == 'true':
      try:
        xg_on = db.create_transaction_options(xg=True)
        db.run_in_transaction_options(xg_on,
          self.increment_counters, key, int(amount))
        counter1_future = db.get_async(db.Key.from_path('Counter', key))
        counter2_future = db.get_async(db.Key.from_path('Counter', 
          key + '_backup'))

        counter1 = counter1_future.get_result()
        counter2 = counter2_future.get_result()
        status = {
          'success' : True,
          'counter' : counter1.counter,
          'backup' : counter2.counter
        }
      except Exception:
        counter1_future = db.get_async(db.Key.from_path('Counter', key))
        counter2_future = db.get_async(db.Key.from_path('Counter',
          key + '_backup'))

        counter1 = counter1_future.get_result()
        counter2 = counter2_future.get_result()
        status = {
          'success' : False,
          'counter' : counter1.counter,
          'backup' : counter2.counter
        }
    else:
      try:
        db.run_in_transaction(self.increment_counter, key, int(amount))
        counter_future = db.get_async(db.Key.from_path('Counter', key))
        counter = counter_future.get_result()
        status = { 'success' : True, 'counter' : counter.counter }
      except Exception:
        counter_future = db.get_async(db.Key.from_path('Counter', key))
        counter = counter_future.get_result()
        status = { 'success' : False, 'counter' : counter.counter }
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps(status))

  def delete(self):
    delete_future = db.delete_async(Counter.all())
    delete_future.get_result()

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
    put_future = db.put_async(company)
    put_future.get_result()
    
    employee1 = Employee(name = "A", parent = company)
    employee1_future = db.put_async(employee1)
    employee2 = Employee(name = "B", parent = company)
    employee2_future = db.put_async(employee2)
    employee3 = Employee(name = "C", parent = company)
    employee3_future = db.put_async(employee3)
    employee4 = Employee(name = "D", parent = company)
    employee4_future = db.put_async(employee4)

    employee1_future.get_result()
    employee2_future.get_result()
    employee3_future.get_result()
    employee4_future.get_result()

    pn1 = PhoneNumber(work = "1111111111", parent = employee1)
    pn1_future = db.put_async(pn1)
    pn2 = PhoneNumber(work = "2222222222", parent = employee2)
    pn2_future = db.put_async(pn2)
    pn3 = PhoneNumber(work = "3333333333", parent = employee3)
    pn3_future = db.put_async(pn3)
    pn4 = PhoneNumber(work = "4444444444", parent = employee4)
    pn4_future = db.put_async(pn4)

    pn1_future.get_result()
    pn2_future.get_result()
    pn3_future.get_result()
    pn4_future.get_result()
    
  def clean_up_data(self):
    company_future = db.delete_async(Company.all())
    employee_future = db.delete_async(Employee.all())
    phone_number_future = db.delete_async(PhoneNumber.all())

    company_future.get_result()
    employee_future.get_result()
    phone_number_future.get_result()

class CountQueryHandler(webapp2.RequestHandler):
  def get(self):
    status = {'success' : True}
    self.response.headers['Content-Type'] = "application/json"
    try:
      employee1 = Employee(name = "Raj")
      employee1_future = db.put_async(employee1)
      employee2 = Employee(name = "Tyler")
      employee2_future = db.put_async(employee2)

      employee1_future.get_result()
      employee2_future.get_result()

      count1 = Employee.all().count(limit=5, deadline=60)
      if count1 != 2:
        raise Exception('Did not retrieve 2 Employees, got ' + str(count1))
      employee3 = Employee(name = "Brian")
      employee3_future = db.put_async(employee3)
      employee3_future.get_result()
      count2 = Employee.all().count(limit=5, deadline=60)
      if count2 != 3:
        raise Exception('Did not retrieve 3 Employees, got ' + str(count2))
    except Exception:
      status = {'success' : False}
      self.response.out.write(json.dumps(status))
      raise
    finally:
      delete_future = db.delete_async(Employee.all())
      delete_future.get_result()

class Employee(db.Model):
  name = db.StringProperty(required=True)

class Company(db.Model):
  name = db.StringProperty(required=True)

class PhoneNumber(db.Model):
  work = db.StringProperty(required=True)

application = webapp.WSGIApplication([
  ('/python/async_datastore/project', ProjectHandler),
  ('/python/async_datastore/module', ModuleHandler),
  ('/python/async_datastore/project_modules', ProjectModuleHandler),
  ('/python/async_datastore/project_keys', ProjectKeyHandler),
  ('/python/async_datastore/entity_names', EntityNameHandler),
  ('/python/async_datastore/project_ratings', ProjectRatingHandler),
  ('/python/async_datastore/project_fields', ProjectFieldHandler),
  ('/python/async_datastore/project_filter', ProjectFilterHandler),
  ('/python/async_datastore/project_cursor', ProjectBrowserHandler),
  ('/python/async_datastore/complex_cursor', ComplexCursorHandler),
  ('/python/async_datastore/count_query', CountQueryHandler),
  ('/python/async_datastore/transactions', TransactionHandler),
], debug=True)

if __name__ == '__main__':
  wsgiref.handlers.CGIHandler().run(application)
