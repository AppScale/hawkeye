try:
  import json
except ImportError:
  import simplejson as json

from google.appengine.api import datastore_errors
from google.appengine.api import namespace_manager
from google.appengine.ext import db
from google.appengine.ext import ndb
from google.appengine.ext import webapp

import logging
import random
import string
import time
import unittest
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

class Cars(db.Model):
  model = db.StringProperty(required=True)
  make = db.StringProperty(required=True)
  color = db.StringProperty(required=True) 

class CompositeCars(db.Model):
  model = db.StringProperty(required=True)
  make = db.StringProperty(required=True)
  color = db.StringProperty(required=True)
  value = db.IntegerProperty(required=True)

class TestModel(ndb.Model):
  field = ndb.StringProperty()
  bool_field = ndb.BooleanProperty()

class Post(db.Model):
  content = db.StringProperty()
  tags = db.StringListProperty()
  date_added = db.DateTimeProperty(auto_now_add=True)

class TestException(Exception):
  pass

class CompositeMultipleFiltersOnProperty(webapp2.RequestHandler):
  """ Queries that use a set of equality filters use the zigzag merge join 
  algorithm.
  """
  def get(self):
    non_set_cars = []
    for x in range(0, 10):
      model = random.choice(["SModel", "Civic", "S2000"])
      make = random.choice(["Tesla", "Ford"])
      # The color will never match what we are querying for.
      color = random.choice(["red", "green", "blue"])
      value = x
      car = CompositeCars(model=model, make=make, color=color, value=value)
      
      non_set_cars.append(car)
    db.put(non_set_cars)

    set_cars = []
    for x in range(0, 10):
      car = CompositeCars(model="SModel", make="Tesla", color="purple", value=x)
      set_cars.append(car)
    db.put(set_cars)

    second_set = []
    for x in range(0, 10):
      car = CompositeCars(model="Camry", make="Toyota", color="gold", value=x)
      second_set.append(car)
    db.put(second_set)

    q = CompositeCars.all()
    q.filter("model =", "SModel")
    q.filter("make =", "Tesla")
    q.filter("color =", "purple")
    q.filter("value >", 4)  
    q.filter("value <", 6)  
    results = q.fetch(100)

    q = CompositeCars.all()
    q.filter("model =", "SModel")
    q.filter("make =", "Tesla")
    q.filter("color =", "purple")
    q.filter("value >=", 4)  
    q.filter("value <=", 6)  
    results_2 = q.fetch(100)

    q = CompositeCars.all()
    q.filter("model =", "Camry")
    q.filter("make =", "Toyota")
    q.filter("color =", "gold")
    q.filter("value >", 4)  
    q.filter("value <=", 6)  
    results_3 = q.fetch(100)

    q = CompositeCars.all()
    q.filter("model =", "Camry")
    q.filter("make =", "Toyota")
    q.filter("color =", "gold")
    q.filter("value >=", 4)  
    q.filter("value <", 6)  
    results_4 = q.fetch(100)

    q = CompositeCars.all()
    q.filter("model =", "Camry")
    q.filter("make =", "Toyota")
    q.filter("color =", "gold")
    q.filter("value >", 4)  
    q.filter("value <=", 6)  
    q.order('-value')
    results_5 = q.fetch(100)

    q = CompositeCars.all()
    q.filter("model =", "Camry")
    q.filter("make =", "Toyota")
    q.filter("color =", "gold")
    q.filter("value >=", 4)  
    q.filter("value <", 6)  
    q.order('-value')
    results_6 = q.fetch(100)


    db.delete(non_set_cars)
    db.delete(set_cars)
    db.delete(second_set)

    if len(results) != 1:
      logging.error("Result for query was {0}, expected 1 item".format(results))
      for result in results:
        logging.info("Item: {0}".format(result.value))
      self.response.set_status(404)
    elif len(results_2) != 3:
      logging.error("Result for query was {0}, expected 3 items".format(results_2))
      self.response.set_status(404)
    elif len(results_3) != 2:
      logging.error("Result for query was {0}, expected 2 items".format(results_3))
      self.response.set_status(404)
    elif len(results_4) != 2:
      logging.error("Result for query was {0}, expected 2 items".format(results_4))
      self.response.set_status(404)
    elif len(results_5) != 2:
      logging.error("Result for query was {0}, expected 2 items".format(results_5))
      self.response.set_status(404)
    elif len(results_6) != 2:
      logging.error("Result for query was {0}, expected 2 items".format(results_6))
      self.response.set_status(404)
    else:
      self.response.set_status(200)


class ZigZagQueryHandler(webapp2.RequestHandler):
  """ Queries that use a set of equality filters use the zigzag merge join 
  algorithm.
  """
  def get(self):
    non_set_cars = []
    for x in range(0, 10):
      model = random.choice(["SModel", "Civic", "S2000"])
      make = random.choice(["Tesla", "Ford"])
      # The color will never match what we are querying for.
      color = random.choice(["red", "green", "blue"])
      car = Cars(model=model, make=make, color=color)
      
      non_set_cars.append(car)
    db.put(non_set_cars)

    set_cars = []
    for x in range(0, 3):
      car = Cars(model="SModel", make="Tesla", color="purple")
      set_cars.append(car) 
    db.put(set_cars)

    second_set = []
    for x in range(0, 3):
      car = Cars(model="Camry", make="Toyota", color="gold")
      second_set.append(car)
    db.put(second_set)

    q = Cars.all()
    q.filter("model =", "SModel")
    q.filter("make =", "Tesla")
    q.filter("color =", "purple")
    results = q.fetch(100)

    q = Cars.all()
    q.filter("model =", "Camry")
    q.filter("make =", "Toyota")
    q.filter("color =", "gold")
    results2 = q.fetch(100)

    db.delete(non_set_cars)
    db.delete(set_cars)
    db.delete(second_set)

    if len(results) == 3 and len(results2) == 3:
      self.response.set_status(200)
    else:
      logging.error("Result for ZigZaq query was %s and %s" % (str(results), 
        str(results2)))
      self.response.set_status(404)

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

class CountQueryHandler(webapp2.RequestHandler):
  def get(self):
    status = {'success' : True}
    self.response.headers['Content-Type'] = "application/json"
    try:
      employee1 = Employee(name = "Raj")
      employee1.put()
      employee2 = Employee(name = "Tyler")
      employee2.put()
      count1 = Employee.all().count(limit=5, deadline=60)
      if count1 != 2:
        raise Exception('Did not retrieve 2 Employees, got ' + str(count1))
      employee3 = Employee(name = "Brian")
      employee3.put()
      count2 = Employee.all().count(limit=5, deadline=60)
      if count2 != 3:
        raise Exception('Did not retrieve 3 Employees, got ' + str(count2))
    except Exception:
      status = {'success' : False}
      self.response.out.write(json.dumps(status))
      raise
    finally:
      db.delete(Employee.all())

class Employee(db.Model):
  name = db.StringProperty(required=True)

class Company(db.Model):
  name = db.StringProperty(required=True)

class PhoneNumber(db.Model):
  work = db.StringProperty(required=True)

# The following test checks if a concurrent transaction exception is raised
# when it shouldn't be.
class TestConcurrentTransaction(unittest.TestCase):

  NAMESPACE = "appscale-test-concurrent-txn"

  def setUp(self):
    namespace_manager.set_namespace(self.NAMESPACE)

  def tearDown(self):
    try:
      keys = TestModel.query().fetch(keys_only=True)
      ndb.delete_multi(keys)
    except Exception as e:
      logging.error("{}".format(e))

  def test_failed_update_in_transaction_and_get(self):
    identifier = str(uuid.uuid4())
    TestModel(id=identifier).put()

    @ndb.transactional
    def failed_update():
      TestModel(id=identifier).put()
      raise TestException("Test")

    self.assertRaises(TestException, failed_update)
    TestModel.get_by_id(identifier)

  def test_failed_update_in_transaction_and_put(self):
    identifier = str(uuid.uuid4())
    TestModel(id=identifier).put()

    @ndb.transactional
    def failed_update():
      TestModel(id=identifier).put()
      raise TestException("Test")

    self.assertRaises(TestException, failed_update)
    TestModel(id=identifier).put()

  def test_failed_update_in_transaction_and_delete(self):
    identifier = str(uuid.uuid4())
    TestModel(id=identifier).put()

    @ndb.transactional
    def failed_update():
      TestModel(id=identifier).put()
      raise TestException("Test")

    self.assertRaises(TestException, failed_update)
    ndb.Key(TestModel, identifier).delete()

  def test_failed_create_in_transaction_and_get(self):
    identifier = str(uuid.uuid4())

    @ndb.transactional
    def failed_update():
      TestModel(id=identifier).put()
      raise TestException("Test")

    self.assertRaises(TestException, failed_update)
    TestModel.get_by_id(identifier)

  def test_failed_create_in_transaction_and_put(self):
    identifier = str(uuid.uuid4())

    @ndb.transactional
    def failed_update():
      TestModel(id=identifier).put()
      raise TestException("Test")

    self.assertRaises(TestException, failed_update)
    TestModel(id=identifier).put()

  def test_failed_create_in_transaction_and_delete(self):
    identifier = str(uuid.uuid4())

    @ndb.transactional
    def failed_update():
      TestModel(id=identifier).put()
      raise TestException("Test")

    self.assertRaises(TestException, failed_update)
    ndb.Key(TestModel, identifier).delete()

  def test_failed_update_in_transaction_and_transactional_get(self):
    identifier = str(uuid.uuid4())
    TestModel(id=identifier).put()

    @ndb.transactional
    def failed_update():
      TestModel(id=identifier).put()
      raise TestException("Test")

    self.assertRaises(TestException, failed_update)
    ndb.transaction(lambda: TestModel.get_by_id(identifier))

  def test_failed_update_in_transaction_and_transactional_put(self):
    identifier = str(uuid.uuid4())
    TestModel(id=identifier).put()

    @ndb.transactional
    def failed_update():
      TestModel(id=identifier).put()
      raise TestException("Test")

    self.assertRaises(TestException, failed_update)
    ndb.transaction(lambda: TestModel(id=identifier).put())

  def test_failed_update_in_transaction_and_transactional_delete(self):
    identifier = str(uuid.uuid4())
    TestModel(id=identifier).put()

    @ndb.transactional
    def failed_update():
      TestModel(id=identifier).put()
      raise TestException("Test")

    self.assertRaises(TestException, failed_update)
    ndb.transaction(lambda: ndb.Key(TestModel, identifier).delete())

  def test_failed_create_in_transaction_and_transactional_get(self):
    identifier = str(uuid.uuid4())

    @ndb.transactional
    def failed_update():
      TestModel(id=identifier).put()
      raise TestException("Test")

    self.assertRaises(TestException, failed_update)
    ndb.transaction(lambda: TestModel.get_by_id(identifier))

  def test_failed_create_in_transaction_and_transactional_put(self):
    identifier = str(uuid.uuid4())

    @ndb.transactional
    def failed_update():
      TestModel(id=identifier).put()
      raise TestException("Test")

    self.assertRaises(TestException, failed_update)
    ndb.transaction(lambda: TestModel(id=identifier).put())

  def test_failed_create_in_transaction_and_transactional_delete(self):
    identifier = str(uuid.uuid4())

    @ndb.transactional
    def failed_update():
      TestModel(id=identifier).put()
      raise TestException("Test")

    self.assertRaises(TestException, failed_update)
    ndb.transaction(lambda: ndb.Key(TestModel, identifier).delete())

class TestConcurrentTransactionHandler(webapp2.RequestHandler):
  def get(self):
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestConcurrentTransaction))
    result = unittest.TextTestRunner().run(suite)
    if not result.wasSuccessful():
      self.error(500)

# The following test checks if entities can be found even after a delete
# succeeds in a failed transaction.
class TestQueryingAfterFailedTxn(unittest.TestCase):
  ids = ["save-time-single-ID"]
  fetchers = [
    ("Get (unordered)",
     lambda: TestModel.query().get()),
    ("Get (ordered by key)",
     lambda: TestModel.query().order(TestModel._key).get()),
    ("Get (ordered by field)",
     lambda: TestModel.query().order(TestModel.field).get()),
    ("Fetch (unordered)",
     lambda: TestModel.query().fetch()),
    ("Fetch (ordered by key)",
     lambda: TestModel.query().order(TestModel._key).fetch()),
    ("Fetch (ordered by field)",
     lambda: TestModel.query().order(TestModel.field).fetch()),
    ("Fetch keys (unordered)",
     lambda: TestModel.query().fetch(keys_only=True)),
    ("Fetch keys (ordered by key)",
     lambda: TestModel.query().order(TestModel._key).fetch(keys_only=True)),
    ("Fetch keys (ordered by field)",
     lambda: TestModel.query().order(TestModel.field).fetch(keys_only=True)),
    ("Get filtered (unordered)",
     lambda: TestModel.query().filter(TestModel.field > '').get()),
    ("Get filtered (ordered by field)",
     lambda: TestModel.query().filter(TestModel.field > '').order(TestModel.field).get()),
    ("Fetch filtered (unordered)",
     lambda: TestModel.query().filter(TestModel.field > '').fetch()),
    ("Fetch filtered (ordered by field)",
     lambda: TestModel.query().filter(TestModel.field > '').order(TestModel.field).fetch()),
    ("Fetch keys filtered (unordered)",
     lambda: TestModel.query().filter(TestModel.field > '').fetch(keys_only=True)),
    ("Fetch keys filtered (ordered by field)",
     lambda: TestModel.query().filter(TestModel.field > '').order(TestModel.field).fetch(keys_only=True)),
  ]

  @staticmethod
  def rand_str():
    return ''.join((random.choice(string.ascii_letters) for _ in xrange(10)))

  def setUp(self):
    namespace_manager.set_namespace("appscale-test-querying")
    self.errors = []

  def tearDown(self):
    keys = TestModel.query().fetch(keys_only=True)
    ndb.delete_multi(keys)

  def _errors_to_msg(self, context):
    return "\n{}:\n{}".format(context, "\n".join(self.errors))

  def _check_and_delete(self, id_, has_to_be):
    gotten_by_id = TestModel.get_by_id(id_)
    if bool(gotten_by_id) != has_to_be:
      suffix = "(is not gotten)" if has_to_be else "(is gotten)"
      err = "    {} > Get by ID: Failed {}".format(id_, suffix)
      self.errors.append(err)
    time.sleep(0.5)
    for fetcher_comment, fetcher in self.fetchers:
      result = fetcher()
      if bool(result) != has_to_be:
        suffix = "(is not fetched)" if has_to_be else "(is fetched)"
        err = "    {} > {}: Failed {}".format(id_, fetcher_comment, suffix)
        self.errors.append(err)
    ndb.Key(TestModel, id_).delete()

  def test_put_and_get_and_query(self):
    for identifier in self.ids:
      TestModel(id=identifier, field=self.rand_str()).put()
      self._check_and_delete(identifier, True)
    ctx = "Create > Check"
    self.assertEqual(len(self.errors), 0, self._errors_to_msg(ctx))

  def test_failed_create_in_txn_and_get_and_query(self):
    @ndb.transactional
    def create(id_):
      TestModel(id=id_, field=self.rand_str()).put()
      raise TestException("expected error")
    for identifier in self.ids:
      self.assertRaises(TestException, create, identifier)
      self._check_and_delete(identifier, False)
    ctx = "Create in failed txn (non-xg) > Check"
    self.assertEqual(len(self.errors), 0, self._errors_to_msg(ctx))

  def test_failed_create_in_xg_txn_and_get_and_query(self):
    @ndb.transactional(xg=True)
    def create(id_):
      TestModel(id=id_, field=self.rand_str()).put()
      TestModel(id="second-entity-group", field=self.rand_str()).put()
      raise TestException("expected error")
    for identifier in self.ids:
      self.assertRaises(TestException, create, identifier)
      self._check_and_delete(identifier, False)
    ctx = "Create in failed txn (valid-xg: 2 groups) > Check"
    self.assertEqual(len(self.errors), 0, self._errors_to_msg(ctx))

  def test_failed_create_in_many_groups_txn_and_get_and_query(self):
    @ndb.transactional(xg=True)
    def create(id_):
      TestModel(id=id_, field=self.rand_str()).put()
      for x in xrange(30):
        TestModel(id="entity-group-{}".format(x), field=self.rand_str()).put()
    for identifier in self.ids:
      self.assertRaises(datastore_errors.Error, create, identifier)
      self._check_and_delete(identifier, False)
    ctx = "Create in failed txn (invalid-xg: 30 groups) > Check"
    self.assertEqual(len(self.errors), 0, self._errors_to_msg(ctx))

  def test_failed_update_in_txn_and_get_and_query(self):
    def create_and_update(id_):
      @ndb.transactional
      def update():
        TestModel(id=id_, field=self.rand_str()).put()
        raise TestException("expected error")
      TestModel(id=id_, field=self.rand_str()).put()
      update()
    for identifier in self.ids:
      self.assertRaises(TestException, create_and_update, identifier)
      self._check_and_delete(identifier, True)
    ctx = "Create > Update in failed txn (non-xg) > Check"
    self.assertEqual(len(self.errors), 0, self._errors_to_msg(ctx))

  def test_failed_update_in_xg_txn_and_get_and_query(self):
    def create_and_update(id_):
      @ndb.transactional(xg=True)
      def update():
        TestModel(id=id_, field=self.rand_str()).put()
        TestModel(id="second-entity-group", field=self.rand_str()).put()
        raise TestException("expected error")
      TestModel(id=id_, field=self.rand_str()).put()
      update()
    for identifier in self.ids:
      self.assertRaises(TestException, create_and_update, identifier)
      self._check_and_delete(identifier, True)
    ctx = "Create > Update in failed txn (valid-xg: 2 groups) > Check"
    self.assertEqual(len(self.errors), 0, self._errors_to_msg(ctx))

  def test_failed_update_in_many_groups_txn_and_get_and_query(self):
    def create_and_update(id_):
      @ndb.transactional(xg=True)
      def update():
        TestModel(id=id_, field=self.rand_str()).put()
        for x in xrange(30):
          TestModel(id="entity-group-{}".format(x), field=self.rand_str()).put()
      TestModel(id=id_, field=self.rand_str()).put()
      update()
    for identifier in self.ids:
      self.assertRaises(datastore_errors.Error, create_and_update, identifier)
      self._check_and_delete(identifier, True)
    ctx = "Create > Update in failed txn (invalid-xg: 30 groups) > Check"
    self.assertEqual(len(self.errors), 0, self._errors_to_msg(ctx))

  def test_failed_delete_in_txn_and_get_and_query(self):
    def create_and_delete(id_):
      @ndb.transactional
      def delete():
        ndb.Key(TestModel, id_).delete()
        raise TestException("expected error")
      TestModel(id=id_, field=self.rand_str()).put()
      delete()
    for identifier in self.ids:
      self.assertRaises(TestException, create_and_delete, identifier)
      self._check_and_delete(identifier, True)
    ctx = "Create > Delete in failed txn (non-xg) > Check"
    self.assertEqual(len(self.errors), 0, self._errors_to_msg(ctx))

  def test_failed_delete_in_xg_txn_and_get_and_query(self):
    def create_and_delete(id_):
      @ndb.transactional(xg=True)
      def delete():
        ndb.Key(TestModel, id_).delete()
        TestModel(id="second-entity-group", field=self.rand_str()).put()
        raise TestException("expected error")
      TestModel(id=id_, field=self.rand_str()).put()
      delete()
    for identifier in self.ids:
      self.assertRaises(TestException, create_and_delete, identifier)
      self._check_and_delete(identifier, True)
    ctx = "Create > Delete in failed txn (valid-xg: 2 groups) > Check"
    self.assertEqual(len(self.errors), 0, self._errors_to_msg(ctx))

  def test_failed_delete_in_many_groups_txn_and_get_and_query(self):
    def create_and_delete(id_):
      @ndb.transactional(xg=True)
      def delete():
        ndb.Key(TestModel, id_).delete()
        for x in xrange(30):
          TestModel(id="entity-group-{}".format(x), field=self.rand_str()).put()
      TestModel(id=id_, field=self.rand_str()).put()
      delete()
    for identifier in self.ids:
      self.assertRaises(datastore_errors.Error, create_and_delete, identifier)
      self._check_and_delete(identifier, True)
    ctx = "Create > Delete in failed txn (invalid-xg: 30 groups) > Check"
    self.assertEqual(len(self.errors), 0, self._errors_to_msg(ctx))

class TestQueryingAfterFailedTxnHandler(webapp2.RequestHandler):
  def get(self):
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestQueryingAfterFailedTxn))
    result = unittest.TextTestRunner().run(suite)
    if not result.wasSuccessful():
      self.error(500)

class TestQueryPagination(unittest.TestCase):
  page_size = 3
  query_builders = [
    ("Fetch (unordered)",
     lambda: TestModel.query()),
    ("Fetch (ordered by key)",
     lambda: TestModel.query().order(TestModel._key)),
    ("Fetch (ordered by field)",
     lambda: TestModel.query().order(TestModel.field)),
    ("Fetch filtered (unordered)",
     lambda: TestModel.query().filter(TestModel.field > '')),
    ("Fetch filtered (ordered by field)",
     lambda: TestModel.query().filter(TestModel.field > '').order(TestModel.field))
  ]

  @staticmethod
  def rand_str():
    return ''.join((random.choice(string.ascii_letters) for _ in xrange(10)))

  def setUp(self):
    self.errors = []

  def _init_entities_and_namespace(self):
    namespace_manager.set_namespace("appscale-test-pagination")
    self.entities = [
      TestModel(id="entity-{}".format(x), field=self.rand_str()) for x in xrange(10)
    ]
    ndb.put_multi(self.entities)
    self.keys = [entity.key for entity in self.entities]

  def _errors_to_msg(self, context):
    return "\n{}:\n{}".format(context, "\n".join(self.errors))

  def _check_and_delete(self, fetcher, context):
    for comment, query_builder in self.query_builders:
      self._init_entities_and_namespace()
      time.sleep(0.5)
      entities = fetcher(query_builder())
      if len(entities) != len(self.entities):
        err_fmt = "    {}: Failed ({} of {} are fetched)"
        err = err_fmt.format(comment, len(entities), len(self.entities))
        self.errors.append(err)
      ndb.delete_multi(self.keys)
    self.assertEqual(len(self.errors), 0, self._errors_to_msg(context))

  def test_one_shot_querying(self):
    def one_shot_fetcher(query):
      return query.fetch()
    ctx = "One shot - fetch()"
    self._check_and_delete(one_shot_fetcher, ctx)

  def test_limit_offset_querying(self):
    def limit_offset_fetcher(query):
      results = []
      page = query.fetch(limit=self.page_size)
      offset = self.page_size
      while page:
        results += page
        page = query.fetch(limit=self.page_size, offset=offset)
        offset += self.page_size
      return results
    ctx = "Limit-offset pagination - fetch(limit, offset)"
    self._check_and_delete(limit_offset_fetcher, ctx)

  def test_cursor_querying(self):
    def cursor_fetcher(query):
      results = []
      page, cursor, has_more = query.fetch_page(self.page_size, start_cursor=None)
      results += page
      while has_more and cursor:
        page, cursor, has_more = query.fetch_page(self.page_size, start_cursor=cursor)
        results += page
      return results
    ctx = "Cursor pagination - fetch(limit, start_cursor)"
    self._check_and_delete(cursor_fetcher, ctx)

class TestQueryPaginationHandler(webapp2.RequestHandler):
  def get(self):
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestQueryPagination))
    result = unittest.TextTestRunner().run(suite)
    if not result.wasSuccessful():
      self.error(500)

class TestMaxGroupsInTxn(unittest.TestCase):
  fetchers = [
    ("Get (unordered)",
     lambda: TestModel.query().get()),
    ("Get (ordered by key)",
     lambda: TestModel.query().order(TestModel._key).get()),
    ("Get (ordered by field)",
     lambda: TestModel.query().order(TestModel.field).get()),
    ("Fetch (unordered)",
     lambda: TestModel.query().fetch()),
  ]

  @staticmethod
  def rand_str():
    return ''.join((random.choice(string.ascii_letters) for _ in xrange(10)))

  def setUp(self):
    namespace_manager.set_namespace("appscale-test-querying")

  def tearDown(self):
    keys = TestModel.query().fetch(keys_only=True)
    ndb.delete_multi(keys)

  def test_max_groups_in_txn(self):
    @ndb.transactional(xg=True)
    def create(groups):
      for x in xrange(groups):
        TestModel(id="entity-group-{}".format(x), field=self.rand_str()).put()
    create(25)
    self.assertRaises(datastore_errors.Error, create, 26)

class TestMaxGroupsInTxnHandler(webapp2.RequestHandler):
  def get(self):
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMaxGroupsInTxn))
    result = unittest.TextTestRunner().run(suite)
    if not result.wasSuccessful():
      self.error(500)

class TestIndexIntegrity(unittest.TestCase):
  def setUp(self):
    namespace_manager.set_namespace("appscale-test-querying")

  def tearDown(self):
    keys = TestModel.query().fetch(keys_only=True)
    ndb.delete_multi(keys)

  def test_index_just_created(self):
    id_ = str(uuid.uuid4())
    TestModel(id=id_ + "1", field="value", bool_field=True).put()
    TestModel(id=id_ + "2", field="---", bool_field=True).put()
    TestModel(id=id_ + "3", field=None, bool_field=True).put()
    TestModel(id=id_ + "4", field="value", bool_field=False).put()
    TestModel(id=id_ + "5", field="value", bool_field=None).put()
    TestModel(id=id_ + "6", field="---", bool_field=False).put()
    TestModel(id=id_ + "7", field=None, bool_field=None).put()
    time.sleep(0.5)
    results = TestModel.query() \
      .filter(TestModel.field=="value") \
      .filter(TestModel.bool_field==True) \
      .fetch()
    field_values = [(entity.field, entity.bool_field) for entity in results]
    self.assertEqual(field_values, [("value", True)])

  def test_index_updated(self):
    id_ = str(uuid.uuid4())
    TestModel(id=id_ + "1", field="value", bool_field=True).put()
    TestModel(id=id_ + "2", field="value", bool_field=True).put()
    TestModel(id=id_ + "3", field="value", bool_field=True).put()
    TestModel(id=id_ + "4", field="value", bool_field=True).put()
    TestModel(id=id_ + "5", field="value", bool_field=True).put()
    TestModel(id=id_ + "6", field="value", bool_field=True).put()
    TestModel(id=id_ + "7", field="value", bool_field=True).put()
    TestModel(id=id_ + "1", field="value", bool_field=True).put()
    TestModel(id=id_ + "2", field="---", bool_field=True).put()
    TestModel(id=id_ + "3", field=None, bool_field=True).put()
    TestModel(id=id_ + "4", field="value", bool_field=False).put()
    TestModel(id=id_ + "5", field="value", bool_field=None).put()
    TestModel(id=id_ + "6", field="---", bool_field=False).put()
    TestModel(id=id_ + "7", field=None, bool_field=None).put()
    time.sleep(0.5)
    results = TestModel.query() \
      .filter(TestModel.field=="value") \
      .filter(TestModel.bool_field==True) \
      .fetch()
    field_values = [(entity.field, entity.bool_field) for entity in results]
    self.assertEqual(field_values, [("value", True)])

class TestIndexIntegrityHandler(webapp2.RequestHandler):
  def get(self):
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestIndexIntegrity))
    result = unittest.TextTestRunner().run(suite)
    if not result.wasSuccessful():
      self.error(500)

class TestMultipleEqualityFilters(unittest.TestCase):
  def setUp(self):
    namespace_manager.set_namespace("appscale-test-querying-2")
    Post(tags=['boo'], content='test').put()
    Post(tags=['baz'], content='test').put()
    Post(tags=['boo', 'baz'], content='test').put()
    time.sleep(.5)

  def tearDown(self):
    posts = Post.all().run()
    for post in posts:
      post.delete()
    time.sleep(.5)

  def test_multiple_equality_filters_for_single_prop(self):
    query = Post.all()
    self.assertEqual(query.count(), 3)

    query = Post.all().filter('tags = ', 'boo')
    self.assertEqual(query.count(), 2)

    query = Post.all().filter('tags = ', 'baz')
    self.assertEqual(query.count(), 2)

    query = Post.all().filter('tags = ', 'boo').filter('tags = ', 'baz')
    self.assertEqual(query.count(), 1)

    query = Post.all().filter('tags = ', 'baz').filter('tags = ', 'boo')
    self.assertEqual(query.count(), 1)

  def test_multiple_equality_filters_for_zz_merge(self):
    query = Post.all()
    self.assertEqual(query.count(), 3)

    query = Post.all().filter('tags = ', 'boo').filter('content =', 'test')
    self.assertEqual(query.count(), 2)

    query = Post.all().filter('tags = ', 'baz').filter('content =', 'test')
    self.assertEqual(query.count(), 2)

    query = Post.all().filter('tags = ', 'boo').filter('tags = ', 'baz')\
      .filter('content =', 'test')
    self.assertEqual(query.count(), 1)

    query = Post.all().filter('tags = ', 'baz').filter('tags = ', 'boo')\
      .filter('content =', 'test')
    self.assertEqual(query.count(), 1)

  def test_multiple_equality_filters_for_composite(self):
    query = Post.all()
    self.assertEqual(query.count(), 3)

    query = Post.all().order('-date_added').filter('tags = ', 'boo')
    self.assertEqual(query.count(), 2)

    query = Post.all().order('-date_added').filter('tags = ', 'baz')
    self.assertEqual(query.count(), 2)

    query = Post.all().order('-date_added')\
      .filter('tags = ', 'boo').filter('tags = ', 'baz')
    self.assertEqual(query.count(), 1)

    query = Post.all().order('-date_added')\
      .filter('tags = ', 'baz').filter('tags = ', 'boo')
    self.assertEqual(query.count(), 1)

class TestMultipleEqualityFiltersHandler(webapp2.RequestHandler):
  def get(self):
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMultipleEqualityFilters))
    result = unittest.TextTestRunner().run(suite)
    if not result.wasSuccessful():
      self.error(500)

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
  ('/python/datastore/count_query', CountQueryHandler),
  ('/python/datastore/transactions', TransactionHandler),
  ('/python/datastore/zigzag', ZigZagQueryHandler),
  ('/python/datastore/composite_multiple', CompositeMultipleFiltersOnProperty),
  ('/python/datastore/concurrent_transactions', TestConcurrentTransactionHandler),
  ('/python/datastore/querying_after_failed_txn', TestQueryingAfterFailedTxnHandler),
  ('/python/datastore/query_pagination', TestQueryPaginationHandler),
  ('/python/datastore/max_groups_in_txn', TestMaxGroupsInTxnHandler),
  ('/python/datastore/index_integrity', TestIndexIntegrityHandler),
  ('/python/datastore/multiple_equality_filters', TestMultipleEqualityFiltersHandler),
], debug=True)

if __name__ == '__main__':
  wsgiref.handlers.CGIHandler().run(application)
