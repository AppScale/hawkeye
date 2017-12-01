import base64
import datetime
import json
import logging
import random
import string
import time
import unittest
import uuid

from google.appengine.api import datastore_errors
from google.appengine.ext import db
from google.appengine.ext import ndb
from google.appengine.ext import webapp
import webapp2

import utils

SDK_CONSISTENCY_WAIT = .5

def remove_db_entities(query):
  """ Remove all DB entities that match a given query.

  Args:
    query: A DB query object.
  """
  batch_size = 200
  while True:
    entity_batch = query.fetch(batch_size)
    entities_fetched = len(entity_batch)
    db.delete(entity_batch)
    time.sleep(SDK_CONSISTENCY_WAIT)
    if entities_fetched < batch_size:
      break

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
  model = db.StringProperty()
  make = db.StringProperty()
  color = db.StringProperty()
  value = db.IntegerProperty()

class TestModel(ndb.Model):
  field = ndb.StringProperty()
  bool_field = ndb.BooleanProperty()

class Post(db.Model):
  content = db.StringProperty()
  tags = db.StringListProperty()
  date_added = db.DateTimeProperty(auto_now_add=True)

class User(ndb.Model):
  username = ndb.StringProperty(required=True)
  brands = ndb.StringProperty(repeated=True)
  status = ndb.StringProperty(default='pending')

class NDBCompositeCar(ndb.Model):
  model = ndb.StringProperty()
  color = ndb.StringProperty()
  value = ndb.IntegerProperty()

class TestException(Exception):
  pass

class CompositeMultipleFiltersOnProperty(unittest.TestCase):
  """ Queries that use a set of equality filters use the zigzag merge join 
  algorithm.
  """
  def setUp(self):
    # Populate the index.
    non_set_cars = []
    for x in range(0, 10):
      model = random.choice(["SModel", "Civic", "S2000"])
      make = random.choice(["Tesla", "Ford"])
      color = random.choice(["red", "green", "blue"])
      value = x
      car = CompositeCars(model=model, make=make, color=color, value=value)
      non_set_cars.append(car)
    db.put(non_set_cars)

    time.sleep(SDK_CONSISTENCY_WAIT)

  def tearDown(self):
    cars = CompositeCars.all().run()
    for car in cars:
      car.delete()
    time.sleep(SDK_CONSISTENCY_WAIT)

  def test_operations_for_integers(self):
    cars = []
    for x in range(0, 10):
      car = CompositeCars(model="SModel", make="Tesla", color="purple", value=x)
      cars.append(car)
    for x in range(0, 10):
      car = CompositeCars(model="Camry", make="Toyota", color="gold", value=x)
      cars.append(car)
    db.put(cars)
    time.sleep(SDK_CONSISTENCY_WAIT)

    query = CompositeCars.all()\
      .filter("model =", "SModel")\
      .filter("make =", "Tesla")\
      .filter("color =", "purple")\
      .filter("value >", 4)\
      .filter("value <", 6)
    self.assertEqual(query.count(), 1)

    query = CompositeCars.all()\
      .filter("model =", "SModel")\
      .filter("make =", "Tesla")\
      .filter("color =", "purple")\
      .filter("value >=", 4)\
      .filter("value <=", 6)
    self.assertEqual(query.count(), 3)

    query = CompositeCars.all()\
      .filter("model =", "Camry")\
      .filter("make =", "Toyota")\
      .filter("color =", "gold")\
      .filter("value >", 4)\
      .filter("value <=", 6)
    self.assertEqual(query.count(), 2)

    query = CompositeCars.all()\
      .filter("model =", "Camry")\
      .filter("make =", "Toyota")\
      .filter("color =", "gold")\
      .filter("value >=", 4)\
      .filter("value <", 6)
    self.assertEqual(query.count(), 2)

    query = CompositeCars.all()\
      .filter("model =", "Camry")\
      .filter("make =", "Toyota")\
      .filter("color =", "gold")\
      .filter("value >", 4)\
      .filter("value <=", 6)\
      .order('-value')
    self.assertEqual(query.count(), 2)

    query = CompositeCars.all()\
      .filter("model =", "Camry")\
      .filter("make =", "Toyota")\
      .filter("color =", "gold")\
      .filter("value >=", 4)\
      .filter("value <", 6)\
      .order('-value')
    self.assertEqual(query.count(), 2)

  def test_empty_values(self):
    make_options = [None, 'Audi', 'Buick']
    model_options = [None, 'Model_1', 'Model_2']
    color_options = [None, 'aqua', 'black']
    value_options = [None, 1, 2]
    cars = []
    for make in make_options:
      for model in model_options:
        for color in color_options:
          for value in value_options:
            cars.append(
              CompositeCars(make=make, model=model, color=color, value=value))
    db.put(cars)
    time.sleep(SDK_CONSISTENCY_WAIT)

    for make in make_options:
      for model in model_options:
        for color in color_options:
          query = CompositeCars.all().filter('make =', make)\
            .filter('model =', model).filter('color =', color).order('value')
          results = query.fetch(limit=None)
          values_fetched = [car.value for car in results]
          self.assertListEqual(value_options, values_fetched)

class CompositeMultipleFiltersOnPropertyHandler(webapp2.RedirectHandler):
  def get(self):
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CompositeMultipleFiltersOnProperty))
    result = unittest.TextTestRunner().run(suite)
    if not result.wasSuccessful():
      self.error(500)
      self.response.write(utils.format_errors(result))

class IndexVersatility(unittest.TestCase):
  def tearDown(self):
    remove_db_entities(Counter.all())
    remove_db_entities(CompositeCars.all())

    keys = NDBCompositeCar.query().fetch(keys_only=True)
    ndb.delete_multi(keys)

    keys = User.query().fetch(keys_only=True)
    ndb.delete_multi(keys)
    time.sleep(SDK_CONSISTENCY_WAIT)

  def log_index(self, index):
    """ This should print what index the query actually used. """
    logging.info('Index kind: {}'.format(index.kind()))
    logging.info('Has ancestor? {}'.format(index.has_ancestor))
    for name, direction in index.properties():
      logging.info('Property name: {}'.format(name))
      if direction == db.Index.DESCENDING:
        logging.info('Sort direction: DESC')
      else:
        logging.info('Sort direction: ASC')

  def test_index_versatility(self):
    """
    This test assumes that the following index does not exist:
    - kind: NDBCompositeCar
      ancestor: yes
      properties:
      - name: value

    The datastore should use the following descending index instead:
    - kind: NDBCompositeCar
      ancestor: yes
      properties:
      - name: value
        direction: desc
    """
    parent = User(username='car_enthusiast').put()
    for value in range(10):
      NDBCompositeCar(parent=parent, value=value).put()
    time.sleep(SDK_CONSISTENCY_WAIT)

    query = NDBCompositeCar.query(ancestor=parent).\
      filter(NDBCompositeCar.value > 4)
    results = query.fetch(20)
    self.assertEqual(len(results), 5)
    values = [result.value for result in results]
    self.assertListEqual([5, 6, 7, 8, 9], values)

  def test_db_index_versatility(self):
    """
    This test assumes that the following index does not exist:
    - kind: CompositeCars
      ancestor: yes
      properties:
      - name: value

    The datastore should use the following descending index instead:
    - kind: CompositeCars
      ancestor: yes
      properties:
      - name: value
        direction: desc
    """
    parent = Counter(counter=1).put()
    for value in range(10):
      CompositeCars(parent=parent, value=value).put()
    time.sleep(SDK_CONSISTENCY_WAIT)

    query = CompositeCars.all().ancestor(parent).filter('value >', 4)
    self.assertEqual(query.count(), 5)
    query.fetch(100)
    for index in query.index_list():
      self.log_index(index)

class IndexVersatilityHandler(webapp2.RedirectHandler):
  def get(self):
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(IndexVersatility))
    result = unittest.TextTestRunner().run(suite)
    if not result.wasSuccessful():
      self.error(500)
      self.response.write(utils.format_errors(result))

class ZigZagQuery(unittest.TestCase):
  def tearDown(self):
    remove_db_entities(Cars.all())

  def test_zigzag_query(self):
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
    self.assertEqual(len(results), 3)

    q = Cars.all()
    q.filter("model =", "Camry")
    q.filter("make =", "Toyota")
    q.filter("color =", "gold")
    results = q.fetch(100)
    self.assertEqual(len(results), 3)

class ZigZagQueryHandler(webapp2.RequestHandler):
  """ Queries that use a set of equality filters use the zigzag merge join
  algorithm.
  """
  def get(self):
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ZigZagQuery))
    result = unittest.TextTestRunner().run(suite)
    if not result.wasSuccessful():
      self.error(500)
      self.response.write(utils.format_errors(result))

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
      self.response.write(utils.format_errors(result))

# The following test checks if entities can be found even after a delete
# succeeds in a failed transaction.
class TestQueryingAfterFailedTxn(unittest.TestCase):
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
    self.errors = []

  def tearDown(self):
    keys = TestModel.query().fetch(keys_only=True)
    ndb.delete_multi(keys)

  def _errors_to_msg(self, context):
    return "\n{}:\n{}".format(context, "\n".join(self.errors))

  def _check_and_delete(self, id_, has_to_be):
    time.sleep(SDK_CONSISTENCY_WAIT)
    gotten_by_id = TestModel.get_by_id(id_)
    if bool(gotten_by_id) != has_to_be:
      suffix = "(is not gotten)" if has_to_be else "(is gotten)"
      err = "    {} > Get by ID: Failed {}".format(id_, suffix)
      self.errors.append(err)
    for fetcher_comment, fetcher in self.fetchers:
      result = fetcher()
      if bool(result) != has_to_be:
        suffix = "(is not fetched)" if has_to_be else "(is fetched)"
        err = "    {} > {}: Failed {}".format(id_, fetcher_comment, suffix)
        self.errors.append(err)
    ndb.Key(TestModel, id_).delete()

  def test_put_and_get_and_query(self):
    identifier = str(uuid.uuid4())
    TestModel(id=identifier, field=self.rand_str()).put()
    self._check_and_delete(identifier, True)
    ctx = "Create > Check"
    self.assertEqual(len(self.errors), 0, self._errors_to_msg(ctx))

  def test_failed_create_in_txn_and_get_and_query(self):
    @ndb.transactional
    def create(id_):
      TestModel(id=id_, field=self.rand_str()).put()
      raise TestException("expected error")

    identifier = str(uuid.uuid4())
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

    identifier = str(uuid.uuid4())
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

    identifier = str(uuid.uuid4())
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

    identifier = str(uuid.uuid4())
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

    identifier = str(uuid.uuid4())
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

    identifier = str(uuid.uuid4())
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

    identifier = str(uuid.uuid4())
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

    identifier = str(uuid.uuid4())
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

    identifier = str(uuid.uuid4())
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
      self.response.write(utils.format_errors(result))

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
    keys = TestModel.query().fetch(keys_only=True)
    ndb.delete_multi(keys)

  def _init_entities(self):
    self.entities = [
      TestModel(id="entity-{}".format(x), field=self.rand_str()) for x in xrange(10)
    ]
    ndb.put_multi(self.entities)
    self.keys = [entity.key for entity in self.entities]

  def _errors_to_msg(self, context):
    return "\n{}:\n{}".format(context, "\n".join(self.errors))

  def _check_and_delete(self, fetcher, context):
    for comment, query_builder in self.query_builders:
      self._init_entities()
      time.sleep(SDK_CONSISTENCY_WAIT)
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
      self.response.write(utils.format_errors(result))

class TestCursorQueries(unittest.TestCase):
  def setUp(self):
    self.parent = Project(
      project_id=''.join(random.choice(string.digits) for _ in range(10)),
      name=''.join(random.choice(string.ascii_letters) for _ in range(10)),
      description='test',
      rating=random.randint(0, 1000),
      license='test',
    )
    self.parent.put()
    time.sleep(SDK_CONSISTENCY_WAIT)

  def tearDown(self):
    keys = NDBCompositeCar.query().fetch(keys_only=True)
    ndb.delete_multi(keys)

    remove_db_entities(Module.all().ancestor(self.parent))
    remove_db_entities(Module.all())
    self.parent.delete()
    remove_db_entities(CompositeCars.all())

  def fetch_with_db_cursor(self, query, page_size):
    """ Use a cursor to fetch DB entities.

    Args:
      query: A DB query object.
      page_size: An integer indicating the page size for each fetch.
    Returns:
      A list of entities.
    """
    results = []
    logging.debug('Fetching DB entities with page size: {}'.format(page_size))
    results += query.fetch(page_size)

    cursor = query.cursor()
    while True:
      query.with_cursor(start_cursor=cursor)
      page = query.fetch(page_size)
      results += page
      if len(page) < page_size:
        break
      cursor = query.cursor()

    return results

  def fetch_with_ndb_cursor(self, query, page_size, end_cursor=None):
    """ Use a cursor to fetch NDB entities.

    Args:
      query: An NDB query object.
      page_size: An integer indicating the page size for each fetch.
    Returns:
      A list of entities and a list of cursors used.
    """
    results = []
    cursors = []
    logging.debug('Fetching NDB entities with page size: {}'.format(page_size))
    page, cursor, has_more = query.fetch_page(page_size, start_cursor=None,
      end_cursor=end_cursor)
    results += page
    while has_more and cursor:
      cursors.append(cursor)
      page, cursor, has_more = query.fetch_page(page_size, start_cursor=cursor,
        end_cursor=end_cursor)
      results += page
    return results, cursors

  def test_composite_db_cursor(self):
    color = 'Color_1'
    make = 'Make_1'
    model = 'Model_1'
    total_entities = random.randint(1, 50)
    page_size = random.randint(5, 20)
    logging.debug('Inserting {} CompositeCars'.format(total_entities))

    for _ in range(total_entities):
      composite_car = CompositeCars(
        color=color,
        make=make,
        model=model,
        value=random.randint(0, total_entities)
      )
      composite_car.put()
    time.sleep(SDK_CONSISTENCY_WAIT)

    query = CompositeCars().all().\
      filter('make =', 'Make_1').\
      filter('color =', color).\
      filter('model =', model).\
      filter('value >=', 0)
    results = self.fetch_with_db_cursor(query, page_size)

    # Make sure all of the results were fetched.
    self.assertEqual(len(results), total_entities)

    # Make sure the values were fetched in ascending order.
    highest_value = 0
    for result in results:
      self.assertGreaterEqual(result.value, highest_value)
      highest_value = result.value

    query = CompositeCars().all().\
      filter('make =', 'Make_1').\
      filter('color =', color).\
      filter('model =', model).\
      order('-value')
    results = self.fetch_with_db_cursor(query, page_size)

    # Make sure all of the results were fetched.
    self.assertEqual(len(results), total_entities)

    # Make sure the values were fetched in descending order.
    lowest_value = total_entities
    for result in results:
      self.assertLessEqual(result.value, lowest_value)
      lowest_value = result.value

  def test_composite_ndb_cursor(self):
    color = 'Color_1'
    model = 'Model_1'
    total_entities = random.randint(1, 50)
    page_size = random.randint(5, 20)
    logging.debug('Inserting {} NDBCompositeCars'.format(total_entities))

    for _ in range(total_entities):
      NDBCompositeCar(
        color=color,
        model=model,
        value=random.randint(0, total_entities),
      ).put()
    time.sleep(SDK_CONSISTENCY_WAIT)

    query = NDBCompositeCar.query(
      NDBCompositeCar.color == color,
      NDBCompositeCar.model == model,
      NDBCompositeCar.value >= 0
    )
    results, _ = self.fetch_with_ndb_cursor(query, page_size)

    # Make sure all of the results were fetched.
    self.assertEqual(len(results), total_entities)

    # Make sure the values were fetched in ascending order.
    highest_value = 0
    for result in results:
      self.assertGreaterEqual(result.value, highest_value)
      highest_value = result.value

    query = NDBCompositeCar.query(
      NDBCompositeCar.color == color,
      NDBCompositeCar.model == model
    ).order(-NDBCompositeCar.value)
    results, _ = self.fetch_with_ndb_cursor(query, page_size)

    # Make sure all of the results were fetched.
    self.assertEqual(len(results), total_entities)

    # Make sure the values were fetched in descending order.
    lowest_value = total_entities
    for result in results:
      self.assertLessEqual(result.value, lowest_value)
      lowest_value = result.value

  def test_end_cursor(self):
    color = 'Color_1'
    model = 'Model_1'
    total_entities = random.randint(20, 50)
    page_size = random.randint(10, 19)
    logging.debug('Inserting {} NDBCompositeCars'.format(total_entities))

    for _ in range(total_entities):
      NDBCompositeCar(
        color=color,
        model=model,
        value=random.randint(0, total_entities),
      ).put()
    time.sleep(SDK_CONSISTENCY_WAIT)

    query = NDBCompositeCar.query(NDBCompositeCar.value >= 0)
    results, end_cursors = self.fetch_with_ndb_cursor(query, page_size)

    # Make sure all of the results were fetched.
    self.assertEqual(len(results), total_entities)

    for cursor_num, end_cursor in enumerate(end_cursors):
      logging.debug('Fetching up to {}'.format(end_cursor))
      results, _ = self.fetch_with_ndb_cursor(query, page_size,
        end_cursor=end_cursor)

      # Make sure the results up to each end cursor were fetched.
      self.assertEqual(len(results), page_size * (cursor_num + 1))

  def test_composite_end_cursor(self):
    color = 'Color_1'
    model = 'Model_1'
    total_entities = random.randint(20, 50)
    page_size = random.randint(10, 19)
    logging.debug('Inserting {} NDBCompositeCars'.format(total_entities))

    for _ in range(total_entities):
      NDBCompositeCar(
        color=color,
        model=model,
        value=random.randint(0, total_entities),
      ).put()
    time.sleep(SDK_CONSISTENCY_WAIT)

    query = NDBCompositeCar.query(
      NDBCompositeCar.color == color,
      NDBCompositeCar.model == model,
      NDBCompositeCar.value >= 0,
    )
    results, end_cursors = self.fetch_with_ndb_cursor(query, page_size)

    # Make sure all of the results were fetched.
    self.assertEqual(len(results), total_entities)

    # Make sure the values were fetched in ascending order.
    highest_value = 0
    for result in results:
      self.assertGreaterEqual(result.value, highest_value)
      highest_value = result.value

    for cursor_num, end_cursor in enumerate(end_cursors):
      logging.debug('Fetching up to {}'.format(end_cursor))
      results, _ = self.fetch_with_ndb_cursor(query, page_size,
        end_cursor=end_cursor)

      # Make sure the results up to each end cursor were fetched.
      self.assertEqual(len(results), page_size * (cursor_num + 1))

      # Make sure the values were fetched in ascending order.
      highest_value = 0
      for result in results:
        self.assertGreaterEqual(result.value, highest_value)
        highest_value = result.value

  def test_kindless_cursor(self):
    total_entities = random.randint(1, 50)
    page_size = random.randint(5, 20)

    logging.debug('Inserting {} Modules'.format(total_entities))
    first_module = None
    last_module = None
    padding_size = len(str(total_entities))
    for entity_num in range(total_entities):
      name = 'kindless_cursor_{}'.format(str(entity_num).zfill(padding_size))
      module = Module(
        module_id=str(uuid.uuid1()),
        name=name,
        description='test',
        key_name=name,
      )
      module.put()
      if entity_num == 0:
        first_module = module
      if entity_num == total_entities - 1:
        last_module = module
    time.sleep(SDK_CONSISTENCY_WAIT)

    query = db.Query().filter('__key__ >=', first_module).\
      filter('__key__ <=', last_module)
    results = self.fetch_with_db_cursor(query, page_size)

    # Make sure all of the results were fetched.
    self.assertEqual(len(results), total_entities)

  def test_kindless_ancestor_cursor(self):
    total_entities = random.randint(1, 50)
    page_size = random.randint(5, 20)

    logging.debug('Inserting {} Modules'.format(total_entities))
    for _ in range(total_entities):
      name = ''.join(random.choice(string.ascii_letters) for _ in range(20))
      module = Module(
        module_id=str(uuid.uuid1()),
        name=name,
        description='test',
        parent=self.parent,
        key_name=name,
      )
      module.put()
    time.sleep(SDK_CONSISTENCY_WAIT)

    query = db.Query().ancestor(self.parent).filter('__key__ >', self.parent)
    results = self.fetch_with_db_cursor(query, page_size)

    # Make sure all of the results were fetched.
    self.assertEqual(len(results), total_entities)

class TestCursorQueriesHandler(webapp.RequestHandler):
  def get(self):
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCursorQueries))
    result = unittest.TextTestRunner().run(suite)
    if not result.wasSuccessful():
      self.error(500)
      self.response.write(utils.format_errors(result))

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
      self.response.write(utils.format_errors(result))

class TestIndexIntegrity(unittest.TestCase):
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
    time.sleep(SDK_CONSISTENCY_WAIT)
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
    time.sleep(SDK_CONSISTENCY_WAIT)
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
      self.response.write(utils.format_errors(result))

class TestMultipleEqualityFilters(unittest.TestCase):
  def setUp(self):
    Post(tags=['boo'], content='test').put()
    Post(tags=['baz'], content='test').put()
    Post(tags=['boo', 'baz'], content='test').put()

    User(username='slothrop', brands=['brand1']).put()
    User(username='prentice', brands=['brand2', 'brand3']).put()
    User(username='bloat', brands=['brand1', 'brand2', 'brand3']).put()
    time.sleep(SDK_CONSISTENCY_WAIT)

  def tearDown(self):
    posts = Post.all().run()
    for post in posts:
      post.delete()

    keys = User.query().fetch(keys_only=True)
    ndb.delete_multi(keys)
    time.sleep(SDK_CONSISTENCY_WAIT)

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

  def test_ndb_multiple_equality_for_single_prop(self):
    query = User.query()
    self.assertEqual(query.count(), 3)

    query = User.query(User.brands == 'brand1')
    self.assertEqual(query.count(), 2)

    query = User.query(ndb.AND(User.brands == 'brand1',
      User.brands == 'brand2', User.brands == 'brand3'))
    self.assertEqual(query.count(), 1)

class TestMultipleEqualityFiltersHandler(webapp2.RequestHandler):
  def get(self):
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMultipleEqualityFilters))
    result = unittest.TextTestRunner().run(suite)
    if not result.wasSuccessful():
      self.error(500)
      self.response.write(utils.format_errors(result))

class TestCursorWithZigZagMerge(unittest.TestCase):
  def tearDown(self):
    for user in User.query():
      user.key.delete()
    time.sleep(SDK_CONSISTENCY_WAIT)

  def test_cursor_with_repeated_props(self):
    brand_options = [
      [],
      ['brand1'],
      ['brand2'],
      ['brand3'],
      ['brand1', 'brand2'],
      ['brand1', 'brand3'],
      ['brand2', 'brand3'],
      ['brand1', 'brand2', 'brand3']
    ]
    status_options = ['pending', 'approved', 'expired']

    brands_to_query = ['brand1']
    statuses_to_query = ['approved', 'expired']
    page_size = 5

    i = 1
    expected_usernames = []
    for brand_option in brand_options:
      for status in status_options:
        username = 'user{}'.format(i)
        User(username=username, brands=brand_option, status=status).put()
        if (any(brand in brands_to_query for brand in brand_option)
          and status in statuses_to_query):
          expected_usernames.append(username)
        i += 1

    time.sleep(SDK_CONSISTENCY_WAIT)

    retrieved_usernames = []
    cursor = None
    more = True

    while more:
      query = User.query().\
        filter(User.brands.IN(brands_to_query),
          User.status.IN(statuses_to_query)).\
        order(User._key)
      results, cursor, more = query.\
        fetch_page(page_size, start_cursor=cursor, keys_only=True)
      for result in results:
        retrieved_usernames.append(result.get().username)

    expected_usernames.sort()
    retrieved_usernames.sort()

    self.assertListEqual(expected_usernames, retrieved_usernames)

class TestCursorWithZigZagMergeHandler(webapp2.RequestHandler):
  def get(self):
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCursorWithZigZagMerge))
    result = unittest.TextTestRunner().run(suite)
    if not result.wasSuccessful():
      self.error(500)
      self.response.write(utils.format_errors(result))

class TestRepeatedProperties(unittest.TestCase):
  def tearDown(self):
    posts = Post.all().run()
    for post in posts:
      post.delete()
    time.sleep(SDK_CONSISTENCY_WAIT)

  def test_add_and_empty_repeated_props(self):
    Post(tags=['boo', 'baz'], content='test').put()
    time.sleep(SDK_CONSISTENCY_WAIT)

    query = Post.all().filter('tags = ', 'boo').filter('tags = ', 'baz')
    post = query.get()
    post.tags = []
    post.put()
    time.sleep(SDK_CONSISTENCY_WAIT)

    query = Post.all().filter('tags = ', 'boo').filter('tags = ', 'baz')
    self.assertEqual(query.count(), 0)

class TestRepeatedPropertiesHandler(webapp2.RequestHandler):
  def get(self):
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRepeatedProperties))
    result = unittest.TextTestRunner().run(suite)
    if not result.wasSuccessful():
      self.error(500)
      self.response.write(utils.format_errors(result))

class TestCompositeProjection(unittest.TestCase):
  def tearDown(self):
    posts = Post.all().run()
    for post in posts:
      post.delete()
    time.sleep(SDK_CONSISTENCY_WAIT)

  def test_value_with_delimiter(self):
    timestamp = datetime.datetime(2015, 1, 1)
    for _ in range(150):
      Post(tags=['boo'], date_added=timestamp).put()
      timestamp -= datetime.timedelta(seconds=1)
    time.sleep(SDK_CONSISTENCY_WAIT)

    query = Post.all(projection=['date_added']).filter('tags = ', 'boo')\
      .order('-date_added')
    for _ in query.run():
      pass

class TestCompositeProjectionHandler(webapp2.RequestHandler):
  def get(self):
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCompositeProjection))
    result = unittest.TextTestRunner().run(suite)
    if not result.wasSuccessful():
      self.error(500)
      self.response.write(utils.format_errors(result))

class LongTransactionRead(webapp2.RequestHandler):
  def get(self):
    entity_key = ndb.Key(TestModel, self.request.get('id'))

    @ndb.transactional
    def get_in_tx():
      entity = entity_key.get()
      time.sleep(3)

    get_in_tx()

  def post(self):
    TestModel(id=self.request.get('id')).put()

  def delete(self):
    entity_key = ndb.Key(TestModel, self.request.get('id'))
    entity_key.delete()

class ManageEntity(webapp2.RequestHandler):
  def post(self):
    id_ = base64.urlsafe_b64decode(self.request.get('id').encode('utf-8'))
    content = self.request.get('content')
    TestModel(id=id_, field=content).put()

  def get(self):
    id_ = base64.urlsafe_b64decode(self.request.get('id').encode('utf-8'))
    entity = ndb.Key(TestModel, id_).get()
    self.response.write(entity.field)

  def delete(self):
    id_ = base64.urlsafe_b64decode(self.request.get('id').encode('utf-8'))
    ndb.Key(TestModel, id_).delete()

class CursorWithRepeatedProp(webapp2.RequestHandler):
  TOTAL_ENTITIES = 5

  def serialize_key(self, key):
    return '{}:{}'.format(key.kind(), key.id())

  def get(self):
    query = User.query().\
      filter(User.brands == 'brand_{}'.format(self.TOTAL_ENTITIES))
    page, cursor, has_more = query.fetch_page(
      self.TOTAL_ENTITIES, keys_only=True, start_cursor=None)
    results = [self.serialize_key(key) for key in page]

    page, cursor, has_more = query.fetch_page(
      self.TOTAL_ENTITIES, keys_only=True, start_cursor=cursor)
    for key in page:
      result = self.serialize_key(key)
      if result in results:
        self.error(500)
        self.response.write('Duplicate result seen from cursor query')
        return

      results.append(result)

    json.dump(results, self.response)

  def post(self):
    for index in range(1, self.TOTAL_ENTITIES + 1):
      User(username='user_{}'.format(index),
           brands=['brand_0', 'brand_{}'.format(index)]).put()

  def delete(self):
    keys = User.query().fetch(keys_only=True)
    ndb.delete_multi(keys)

class TxInvalidation(webapp2.RequestHandler):
  def post(self):
    @ndb.transactional(retries=0)
    def get_and_put(key):
      key.get()
      # Give time for the client to make a concurrent request. The second
      # request should come between the get and put.
      time.sleep(1)
      TestModel(key=key, field='transactional').put()

    transactional = self.request.get('txn').lower() == 'true'
    entity_key = ndb.Key(TestModel, self.request.get('key'))
    if transactional:
      try:
        get_and_put(entity_key)
        response = {'txnSucceeded': True}
      except db.TransactionFailedError:
        response = {'txnSucceeded': False}
      self.response.write(json.dumps(response))
    else:
      TestModel(key=entity_key, field='outside transaction').put()

  def delete(self):
    ndb.Key(TestModel, self.request.get('key')).delete()

urls = [
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
  ('/python/datastore/composite_multiple', CompositeMultipleFiltersOnPropertyHandler),
  ('/python/datastore/concurrent_transactions', TestConcurrentTransactionHandler),
  ('/python/datastore/querying_after_failed_txn', TestQueryingAfterFailedTxnHandler),
  ('/python/datastore/query_pagination', TestQueryPaginationHandler),
  ('/python/datastore/cursor_queries', TestCursorQueriesHandler),
  ('/python/datastore/max_groups_in_txn', TestMaxGroupsInTxnHandler),
  ('/python/datastore/index_integrity', TestIndexIntegrityHandler),
  ('/python/datastore/index_versatility', IndexVersatilityHandler),
  ('/python/datastore/multiple_equality_filters', TestMultipleEqualityFiltersHandler),
  ('/python/datastore/cursor_with_zigzag_merge', TestCursorWithZigZagMergeHandler),
  ('/python/datastore/repeated_properties', TestRepeatedPropertiesHandler),
  ('/python/datastore/composite_projection', TestCompositeProjectionHandler),
  ('/python/datastore/long_tx_read', LongTransactionRead),
  ('/python/datastore/manage_entity', ManageEntity),
  ('/python/datastore/cursor_with_repeated_prop', CursorWithRepeatedProp),
  ('/python/datastore/tx_invalidation', TxInvalidation)
]
