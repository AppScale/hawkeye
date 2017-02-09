from hawkeye_utils import DeprecatedHawkeyeTestCase, HawkeyeConstants
from hawkeye_test_runner import HawkeyeTestSuite
import json
from time import sleep
import uuid

__author__ = 'hiranya'

NDB_ALL_PROJECTS = {}
NDB_SYNAPSE_MODULES = {}

class NDBCleanupTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_delete('/ndb/project')
    self.assertEquals(response.status, 200)
    response = self.http_delete('/ndb/module')
    self.assertEquals(response.status, 200)
    response = self.http_delete('/ndb/transactions')
    self.assertEquals(response.status, 200)

class SimpleKindAwareNDBInsertTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_post('/ndb/project',
      'name={0}&description=Mediation Engine&rating=8&license=L1'.format(
        HawkeyeConstants.PROJECT_SYNAPSE))
    project_info = json.loads(response.payload)
    self.assertEquals(response.status, 201)
    self.assertTrue(project_info['success'])
    project_id = project_info['project_id']
    self.assertTrue(project_id is not None)
    NDB_ALL_PROJECTS[HawkeyeConstants.PROJECT_SYNAPSE] = project_id

    response = self.http_post('/ndb/project',
      'name={0}&description=XML Parser&rating=6&license=L1'.format(
        HawkeyeConstants.PROJECT_XERCES))
    project_info = json.loads(response.payload)
    self.assertEquals(response.status, 201)
    self.assertTrue(project_info['success'])
    project_id = project_info['project_id']
    self.assertTrue(project_id is not None)
    NDB_ALL_PROJECTS[HawkeyeConstants.PROJECT_XERCES] = project_id

    response = self.http_post('/ndb/project',
      'name={0}&description=MapReduce Framework&rating=10&license=L2'.format(
        HawkeyeConstants.PROJECT_HADOOP))
    project_info = json.loads(response.payload)
    self.assertEquals(response.status, 201)
    self.assertTrue(project_info['success'])
    project_id = project_info['project_id']
    self.assertTrue(project_id is not None)
    NDB_ALL_PROJECTS[HawkeyeConstants.PROJECT_HADOOP] = project_id

    # Allow some time to eventual consistency to run its course
    sleep(2)

class KindAwareNDBInsertWithParentTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_post('/ndb/module',
      'name={0}&description=Mediation Core&project_id={1}'.format(
        HawkeyeConstants.MOD_CORE,
        NDB_ALL_PROJECTS[HawkeyeConstants.PROJECT_SYNAPSE]))
    mod_info = json.loads(response.payload)
    self.assertEquals(response.status, 201)
    self.assertTrue(mod_info['success'])
    module_id = mod_info['module_id']
    self.assertTrue(module_id is not None)
    NDB_SYNAPSE_MODULES[HawkeyeConstants.MOD_CORE] = module_id

    response = self.http_post('/ndb/module',
      'name={0}&description=NIO HTTP transport&project_id={1}'.format(
        HawkeyeConstants.MOD_NHTTP,
        NDB_ALL_PROJECTS[HawkeyeConstants.PROJECT_SYNAPSE]))
    mod_info = json.loads(response.payload)
    self.assertEquals(response.status, 201)
    self.assertTrue(mod_info['success'])
    module_id = mod_info['module_id']
    self.assertTrue(module_id is not None)
    NDB_SYNAPSE_MODULES[HawkeyeConstants.MOD_NHTTP] = module_id

class SimpleKindAwareNDBQueryTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    project_list = self.assert_and_get_list('/ndb/project')
    for entry in project_list:
      response = self.http_get('/ndb/project?id={0}'.
        format(entry['project_id']))
      list = json.loads(response.payload)
      project_info = list[0]
      self.assertEquals(len(list), 1)
      self.assertEquals(project_info['name'], entry['name'])

    module_list = self.assert_and_get_list('/ndb/module')
    for entry in module_list:
      response = self.http_get('/ndb/module?id={0}'.
        format(entry['module_id']))
      list = json.loads(response.payload)
      project_info = list[0]
      self.assertEquals(len(list), 1)
      self.assertEquals(project_info['name'], entry['name'])

class NDBAncestorQueryTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    entity_list = self.assert_and_get_list('/ndb/project_modules?' \
      'project_id={0}'.format(NDB_ALL_PROJECTS[HawkeyeConstants.PROJECT_SYNAPSE]))
    modules = []
    for entity in entity_list:
      if entity['type'] == 'module':
        modules.append(entity['name'])

    self.assertEquals(len(modules), 2)
    self.assertTrue(modules.index(HawkeyeConstants.MOD_CORE) != -1)
    self.assertTrue(modules.index(HawkeyeConstants.MOD_NHTTP) != -1)

class NDBSinglePropertyBasedQueryTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    entity_list = self.assert_and_get_list('/ndb/project_ratings?rating=10&'
                                           'comparator=eq')
    self.assertEquals(len(entity_list), 1)
    self.assertEquals(entity_list[0]['name'], HawkeyeConstants.PROJECT_HADOOP)

    entity_list = self.assert_and_get_list('/ndb/project_ratings?rating=6&'
                                           'comparator=gt')
    self.assertEquals(len(entity_list), 2)
    for entity in entity_list:
      self.assertNotEquals(entity['name'], HawkeyeConstants.PROJECT_XERCES)

    entity_list = self.assert_and_get_list('/ndb/project_ratings?rating=6&'
                                           'comparator=ge')
    self.assertEquals(len(entity_list), 3)

    entity_list = self.assert_and_get_list('/ndb/project_ratings?rating=8&'
                                           'comparator=lt')
    self.assertEquals(len(entity_list), 1)
    self.assertEquals(entity_list[0]['name'], HawkeyeConstants.PROJECT_XERCES)

    entity_list = self.assert_and_get_list('/ndb/project_ratings?rating=8&'
                                           'comparator=le')
    self.assertEquals(len(entity_list), 2)
    for entity in entity_list:
      self.assertNotEquals(entity['name'], HawkeyeConstants.PROJECT_HADOOP)

    entity_list = self.assert_and_get_list('/ndb/project_ratings?rating=8&'
                                           'comparator=ne')
    self.assertEquals(len(entity_list), 2)
    for entity in entity_list:
      self.assertNotEquals(entity['name'], HawkeyeConstants.PROJECT_SYNAPSE)

    try:
      self.assert_and_get_list('/ndb/project_ratings?rating=5&comparator=le')
      self.fail('Returned an unexpected result')
    except AssertionError:
      pass

class NDBOrderedResultQueryTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    entity_list = self.assert_and_get_list('/ndb/project_ratings?rating=6&'
                                           'comparator=ge&desc=true')
    self.assertEquals(len(entity_list), 3)
    last_rating = 100
    for entity in entity_list:
      self.assertTrue(entity['rating'], last_rating)
      last_rating = entity['rating']

class NDBLimitedResultQueryTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    entity_list = self.assert_and_get_list('/ndb/project_ratings?rating=6&'
                                           'comparator=ge&limit=2')
    self.assertEquals(len(entity_list), 2)

    entity_list = self.assert_and_get_list('/ndb/project_ratings?rating=6&'
                                           'comparator=ge&limit=2&desc=true')
    self.assertEquals(len(entity_list), 2)
    last_rating = 100
    for entity in entity_list:
      self.assertTrue(entity['rating'], last_rating)
      last_rating = entity['rating']

class NDBProjectionQueryTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    entity_list = self.assert_and_get_list('/ndb/project_fields?'
                                           'fields=name,description')
    self.assertEquals(len(entity_list), 3)
    for entity in entity_list:
      self.assertTrue(entity['rating'] is None)
      self.assertTrue(entity['description'] is not None)
      self.assertTrue(entity['name'] is not None)

    entity_list = self.assert_and_get_list('/ndb/project_fields?'
                                           'fields=name,rating&rate_limit=8')
    self.assertEquals(len(entity_list), 2)
    for entity in entity_list:
      self.assertTrue(entity['rating'] is not None)
      self.assertTrue(entity['description'] is None)
      self.assertTrue(entity['name'] is not None)
      self.assertNotEquals(entity['name'], HawkeyeConstants.PROJECT_XERCES)

class NDBCompositeQueryTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    entity_list = self.assert_and_get_list('/ndb/project_filter?'
                                           'license=L1&rate_limit=5')
    self.assertEquals(len(entity_list), 2)
    for entity in entity_list:
      self.assertNotEquals(entity['name'], HawkeyeConstants.PROJECT_HADOOP)

    entity_list = self.assert_and_get_list('/ndb/project_filter?'
                                           'license=L1&rate_limit=8')
    self.assertEquals(len(entity_list), 1)
    self.assertEquals(entity_list[0]['name'], HawkeyeConstants.PROJECT_SYNAPSE)

    entity_list = self.assert_and_get_list('/ndb/project_filter?'
                                           'license=L2&rate_limit=5')
    self.assertEquals(len(entity_list), 1)
    self.assertEquals(entity_list[0]['name'], HawkeyeConstants.PROJECT_HADOOP)

class NDBGQLTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    entity_list = self.assert_and_get_list('/ndb/project_filter?'
                                           'license=L1&rate_limit=5&gql=true')
    self.assertEquals(len(entity_list), 2)
    for entity in entity_list:
      self.assertNotEquals(entity['name'], HawkeyeConstants.PROJECT_HADOOP)

    entity_list = self.assert_and_get_list('/ndb/project_filter?'
                                           'license=L1&rate_limit=8&gql=true')
    self.assertEquals(len(entity_list), 1)
    self.assertEquals(entity_list[0]['name'], HawkeyeConstants.PROJECT_SYNAPSE)

    entity_list = self.assert_and_get_list('/ndb/project_filter?'
                                           'license=L2&rate_limit=5&gql=true')
    self.assertEquals(len(entity_list), 1)
    self.assertEquals(entity_list[0]['name'], HawkeyeConstants.PROJECT_HADOOP)

class NDBInQueryTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    entity_list = self.assert_and_get_list('/ndb/project_license_filter?'
                                           'licenses=L1')
    self.assertEquals(len(entity_list), 2)
    for entity in entity_list:
      self.assertNotEquals(entity['name'], HawkeyeConstants.PROJECT_HADOOP)

    entity_list = self.assert_and_get_list('/ndb/project_license_filter?'
                                           'licenses=L2')
    self.assertEquals(len(entity_list), 1)
    for entity in entity_list:
      self.assertEquals(entity['name'], HawkeyeConstants.PROJECT_HADOOP)

    entity_list = self.assert_and_get_list('/ndb/project_license_filter?'
                                           'licenses=L1,L2')
    self.assertEquals(len(entity_list), 3)

    try:
      self.assert_and_get_list('/ndb/project_license_filter?licenses=L3,L4')
      self.fail('Unexpected response')
    except AssertionError:
      pass

class NDBCursorTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    project1 = self.assert_and_get_list('/ndb/project_cursor')
    project2 = self.assert_and_get_list('/ndb/project_cursor?cursor={0}'.
      format(project1['next']))
    project3 = self.assert_and_get_list('/ndb/project_cursor?cursor={0}'.
      format(project2['next']))
    projects = [ project1['project'], project2['project'], project3['project'] ]
    self.assertTrue(HawkeyeConstants.PROJECT_SYNAPSE in projects)
    self.assertTrue(HawkeyeConstants.PROJECT_XERCES in projects)
    self.assertTrue(HawkeyeConstants.PROJECT_HADOOP in projects)

    project4 = self.assert_and_get_list('/ndb/project_cursor?cursor={0}'.
      format(project3['next']))
    self.assertTrue(project4['project'] is None)
    self.assertTrue(project4['next'] is None)

class SimpleNDBTransactionTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    key = str(uuid.uuid1())
    response = self.http_get('/ndb/transactions?' \
                                             'key={0}&amount=1'.format(key))
    self.assertEquals(response.status, 200)
    entity = json.loads(response.payload)
    self.assertTrue(entity['success'])
    self.assertEquals(entity['counter'], 1)

    response = self.http_get('/ndb/transactions?' \
                                             'key={0}&amount=1'.format(key))
    self.assertEquals(response.status, 200)
    entity = json.loads(response.payload)
    self.assertTrue(entity['success'])
    self.assertEquals(entity['counter'], 2)

    response = self.http_get('/ndb/transactions?' \
                                             'key={0}&amount=3'.format(key))
    self.assertEquals(response.status, 200)
    entity = json.loads(response.payload)
    self.assertFalse(entity['success'])
    self.assertEquals(entity['counter'], 2)

class NDBCrossGroupTransactionTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    key = str(uuid.uuid1())
    response = self.http_get('/ndb/transactions?' \
                                        'key={0}&amount=1&xg=true'.format(key))
    self.assertEquals(response.status, 200)
    entity = json.loads(response.payload)
    self.assertTrue(entity['success'])
    self.assertEquals(entity['counter'], 1)
    self.assertEquals(entity['backup'], 1)

    response = self.http_get('/ndb/transactions?' \
                                        'key={0}&amount=1&xg=true'.format(key))
    self.assertEquals(response.status, 200)
    entity = json.loads(response.payload)
    self.assertTrue(entity['success'])
    self.assertEquals(entity['counter'], 2)
    self.assertEquals(entity['backup'], 2)

    response = self.http_get('/ndb/transactions?' \
                                        'key={0}&amount=3&xg=true'.format(key))
    self.assertEquals(response.status, 200)
    entity = json.loads(response.payload)
    self.assertFalse(entity['success'])
    self.assertEquals(entity['counter'], 2)
    self.assertEquals(entity['backup'], 2)

def suite(lang, app):
  suite = HawkeyeTestSuite('NDB Test Suite', 'ndb')
  if lang != 'python':
    return suite
  suite.addTest(NDBCleanupTest(app))
  suite.addTest(SimpleKindAwareNDBInsertTest(app))
  suite.addTest(KindAwareNDBInsertWithParentTest(app))
  suite.addTest(SimpleKindAwareNDBQueryTest(app))
  suite.addTest(NDBAncestorQueryTest(app))
  suite.addTest(NDBSinglePropertyBasedQueryTest(app))
  suite.addTest(NDBOrderedResultQueryTest(app))
  suite.addTest(NDBLimitedResultQueryTest(app))
  suite.addTest(NDBProjectionQueryTest(app))
  suite.addTest(NDBCompositeQueryTest(app))
  suite.addTest(NDBGQLTest(app))
  suite.addTest(NDBInQueryTest(app))
  suite.addTest(NDBCursorTest(app))
  suite.addTest(SimpleNDBTransactionTest(app))
  suite.addTest(NDBCrossGroupTransactionTest(app))
  return suite