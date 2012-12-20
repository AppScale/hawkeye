import json
from time import sleep
import uuid
from hawkeye_utils import HawkeyeTestCase, HawkeyeConstants, HawkeyeTestSuite

__author__ = 'hiranya'

ndb_all_projects = {}
ndb_synapse_modules = {}

class NDBCleanupTest(HawkeyeTestCase):
  def runTest(self):
    status, headers, payload = self.http_delete('/ndb/project')
    self.assertEquals(status, 200)
    status, headers, payload = self.http_delete('/ndb/module')
    self.assertEquals(status, 200)
    status, headers, payload = self.http_delete('/ndb/transactions')
    self.assertEquals(status, 200)

class SimpleKindAwareNDBInsertTest(HawkeyeTestCase):
  def runTest(self):
    global ndb_all_projects

    status, headers, payload = self.http_post('/ndb/project',
      'name={0}&description=Mediation Engine&rating=8&license=L1'.format(
        HawkeyeConstants.PROJECT_SYNAPSE))
    dict = json.loads(payload)
    self.assertEquals(status, 201)
    self.assertTrue(dict['success'])
    project_id = dict['project_id']
    self.assertTrue(project_id is not None)
    ndb_all_projects[HawkeyeConstants.PROJECT_SYNAPSE] = project_id

    status, headers, payload = self.http_post('/ndb/project',
      'name={0}&description=XML Parser&rating=6&license=L1'.format(HawkeyeConstants.PROJECT_XERCES))
    dict = json.loads(payload)
    self.assertEquals(status, 201)
    self.assertTrue(dict['success'])
    project_id = dict['project_id']
    self.assertTrue(project_id is not None)
    ndb_all_projects[HawkeyeConstants.PROJECT_XERCES] = project_id

    status, headers, payload = self.http_post('/ndb/project',
      'name={0}&description=MapReduce Framework&rating=10&license=L2'.format(
        HawkeyeConstants.PROJECT_HADOOP))
    dict = json.loads(payload)
    self.assertEquals(status, 201)
    self.assertTrue(dict['success'])
    project_id = dict['project_id']
    self.assertTrue(project_id is not None)
    ndb_all_projects[HawkeyeConstants.PROJECT_HADOOP] = project_id

    # Allow some time to eventual consistency to run its course
    sleep(2)

class KindAwareNDBInsertWithParentTest(HawkeyeTestCase):
  def runTest(self):
    global ndb_all_projects
    global ndb_synapse_modules
    status, headers, payload = self.http_post('/ndb/module',
      'name={0}&description=Mediation Core&project_id={1}'.format(HawkeyeConstants.MOD_CORE,
        ndb_all_projects[HawkeyeConstants.PROJECT_SYNAPSE]))
    dict = json.loads(payload)
    self.assertEquals(status, 201)
    self.assertTrue(dict['success'])
    module_id = dict['module_id']
    self.assertTrue(module_id is not None)
    ndb_synapse_modules[HawkeyeConstants.MOD_CORE] = module_id

    status, headers, payload = self.http_post('/ndb/module',
      'name={0}&description=NIO HTTP transport&project_id={1}'.format(HawkeyeConstants.MOD_NHTTP,
        ndb_all_projects[HawkeyeConstants.PROJECT_SYNAPSE]))
    dict = json.loads(payload)
    self.assertEquals(status, 201)
    self.assertTrue(dict['success'])
    module_id = dict['module_id']
    self.assertTrue(module_id is not None)
    ndb_synapse_modules[HawkeyeConstants.MOD_NHTTP] = module_id

class SimpleKindAwareNDBQueryTest(HawkeyeTestCase):
  def runTest(self):
    project_list = self.assert_and_get_list('/ndb/project')
    for entry in project_list:
      status, headers, payload = self.http_get('/ndb/project?id={0}'.format(entry['project_id']))
      list = json.loads(payload)
      dict = list[0]
      self.assertEquals(len(list), 1)
      self.assertEquals(dict['name'], entry['name'])

    module_list = self.assert_and_get_list('/ndb/module')
    for entry in module_list:
      status, headers, payload = self.http_get('/ndb/module?id={0}'.format(entry['module_id']))
      list = json.loads(payload)
      dict = list[0]
      self.assertEquals(len(list), 1)
      self.assertEquals(dict['name'], entry['name'])

class NDBAncestorQueryTest(HawkeyeTestCase):
  def runTest(self):
    global all_projects
    entity_list = self.assert_and_get_list('/ndb/project_modules?project_id={0}'.format(
      ndb_all_projects[HawkeyeConstants.PROJECT_SYNAPSE]))
    modules = []
    for entity in entity_list:
      if entity['type'] == 'module':
        modules.append(entity['name'])

    self.assertEquals(len(modules), 2)
    self.assertTrue(modules.index(HawkeyeConstants.MOD_CORE) != -1)
    self.assertTrue(modules.index(HawkeyeConstants.MOD_NHTTP) != -1)

class NDBSinglePropertyBasedQueryTest(HawkeyeTestCase):
  def runTest(self):
    entity_list = self.assert_and_get_list('/ndb/project_ratings?rating=10&comparator=eq')
    self.assertEquals(len(entity_list), 1)
    self.assertEquals(entity_list[0]['name'], HawkeyeConstants.PROJECT_HADOOP)

    entity_list = self.assert_and_get_list('/ndb/project_ratings?rating=6&comparator=gt')
    self.assertEquals(len(entity_list), 2)
    for entity in entity_list:
      self.assertNotEquals(entity['name'], HawkeyeConstants.PROJECT_XERCES)

    entity_list = self.assert_and_get_list('/ndb/project_ratings?rating=6&comparator=ge')
    self.assertEquals(len(entity_list), 3)

    entity_list = self.assert_and_get_list('/ndb/project_ratings?rating=8&comparator=lt')
    self.assertEquals(len(entity_list), 1)
    self.assertEquals(entity_list[0]['name'], HawkeyeConstants.PROJECT_XERCES)

    entity_list = self.assert_and_get_list('/ndb/project_ratings?rating=8&comparator=le')
    self.assertEquals(len(entity_list), 2)
    for entity in entity_list:
      self.assertNotEquals(entity['name'], HawkeyeConstants.PROJECT_HADOOP)

    entity_list = self.assert_and_get_list('/ndb/project_ratings?rating=8&comparator=ne')
    self.assertEquals(len(entity_list), 2)
    for entity in entity_list:
      self.assertNotEquals(entity['name'], HawkeyeConstants.PROJECT_SYNAPSE)

    try:
      self.assert_and_get_list('/ndb/project_ratings?rating=5&comparator=le')
      self.fail('Returned an unexpected result')
    except AssertionError:
      pass

class NDBOrderedResultQueryTest(HawkeyeTestCase):
  def runTest(self):
    entity_list = self.assert_and_get_list('/ndb/project_ratings?rating=6&comparator=ge&desc=true')
    self.assertEquals(len(entity_list), 3)
    last_rating = 100
    for entity in entity_list:
      self.assertTrue(entity['rating'], last_rating)
      last_rating = entity['rating']

class NDBLimitedResultQueryTest(HawkeyeTestCase):
  def runTest(self):
    entity_list = self.assert_and_get_list('/ndb/project_ratings?rating=6&comparator=ge&limit=2')
    self.assertEquals(len(entity_list), 2)

    entity_list = self.assert_and_get_list('/ndb/project_ratings?rating=6&comparator=ge&limit=2&desc=true')
    self.assertEquals(len(entity_list), 2)
    last_rating = 100
    for entity in entity_list:
      self.assertTrue(entity['rating'], last_rating)
      last_rating = entity['rating']

class NDBProjectionQueryTest(HawkeyeTestCase):
  def runTest(self):
    entity_list = self.assert_and_get_list('/ndb/project_fields?fields=name,description')
    self.assertEquals(len(entity_list), 3)
    for entity in entity_list:
      self.assertTrue(entity['rating'] is None)
      self.assertTrue(entity['description'] is not None)
      self.assertTrue(entity['name'] is not None)

    entity_list = self.assert_and_get_list('/ndb/project_fields?fields=name,rating&rate_limit=8')
    self.assertEquals(len(entity_list), 2)
    for entity in entity_list:
      self.assertTrue(entity['rating'] is not None)
      self.assertTrue(entity['description'] is None)
      self.assertTrue(entity['name'] is not None)
      self.assertNotEquals(entity['name'], HawkeyeConstants.PROJECT_XERCES)

class NDBCompositeQueryTest(HawkeyeTestCase):
  def runTest(self):
    entity_list = self.assert_and_get_list('/ndb/project_filter?license=L1&rate_limit=5')
    self.assertEquals(len(entity_list), 2)
    for entity in entity_list:
      self.assertNotEquals(entity['name'], HawkeyeConstants.PROJECT_HADOOP)

    entity_list = self.assert_and_get_list('/ndb/project_filter?license=L1&rate_limit=8')
    self.assertEquals(len(entity_list), 1)
    self.assertEquals(entity_list[0]['name'], HawkeyeConstants.PROJECT_SYNAPSE)

    entity_list = self.assert_and_get_list('/ndb/project_filter?license=L2&rate_limit=5')
    self.assertEquals(len(entity_list), 1)
    self.assertEquals(entity_list[0]['name'], HawkeyeConstants.PROJECT_HADOOP)

class NDBGQLTest(HawkeyeTestCase):
  def runTest(self):
    entity_list = self.assert_and_get_list('/ndb/project_filter?license=L1&rate_limit=5&gql=true')
    self.assertEquals(len(entity_list), 2)
    for entity in entity_list:
      self.assertNotEquals(entity['name'], HawkeyeConstants.PROJECT_HADOOP)

    entity_list = self.assert_and_get_list('/ndb/project_filter?license=L1&rate_limit=8&gql=true')
    self.assertEquals(len(entity_list), 1)
    self.assertEquals(entity_list[0]['name'], HawkeyeConstants.PROJECT_SYNAPSE)

    entity_list = self.assert_and_get_list('/ndb/project_filter?license=L2&rate_limit=5&gql=true')
    self.assertEquals(len(entity_list), 1)
    self.assertEquals(entity_list[0]['name'], HawkeyeConstants.PROJECT_HADOOP)

class NDBInQueryTest(HawkeyeTestCase):
  def runTest(self):
    entity_list = self.assert_and_get_list('/ndb/project_license_filter?licenses=L1')
    self.assertEquals(len(entity_list), 2)
    for entity in entity_list:
      self.assertNotEquals(entity['name'], HawkeyeConstants.PROJECT_HADOOP)

    entity_list = self.assert_and_get_list('/ndb/project_license_filter?licenses=L2')
    self.assertEquals(len(entity_list), 1)
    for entity in entity_list:
      self.assertEquals(entity['name'], HawkeyeConstants.PROJECT_HADOOP)

    entity_list = self.assert_and_get_list('/ndb/project_license_filter?licenses=L1,L2')
    self.assertEquals(len(entity_list), 3)

    try:
      self.assert_and_get_list('/ndb/project_license_filter?licenses=L3,L4')
      self.fail('Unexpected response')
    except AssertionError:
      pass

class NDBCursorTest(HawkeyeTestCase):
  def runTest(self):
    project1 = self.assert_and_get_list('/ndb/project_cursor')
    project2 = self.assert_and_get_list('/ndb/project_cursor?cursor={0}'.format(project1['next']))
    project3 = self.assert_and_get_list('/ndb/project_cursor?cursor={0}'.format(project2['next']))
    projects = [ project1['project'], project2['project'], project3['project'] ]
    self.assertTrue(HawkeyeConstants.PROJECT_SYNAPSE in projects)
    self.assertTrue(HawkeyeConstants.PROJECT_XERCES in projects)
    self.assertTrue(HawkeyeConstants.PROJECT_HADOOP in projects)

    project4 = self.assert_and_get_list('/ndb/project_cursor?cursor={0}'.format(project3['next']))
    self.assertTrue(project4['project'] is None)
    self.assertTrue(project4['next'] is None)

class SimpleNDBTransactionTest(HawkeyeTestCase):
  def runTest(self):
    key = str(uuid.uuid1())
    status, headers, payload = self.http_get('/ndb/transactions?key={0}&amount=1'.format(key))
    entity = json.loads(payload)
    self.assertTrue(entity['success'])
    self.assertEquals(entity['counter'], 1)

    status, headers, payload = self.http_get('/ndb/transactions?key={0}&amount=1'.format(key))
    entity = json.loads(payload)
    self.assertTrue(entity['success'])
    self.assertEquals(entity['counter'], 2)

    status, headers, payload = self.http_get('/ndb/transactions?key={0}&amount=3'.format(key))
    entity = json.loads(payload)
    self.assertFalse(entity['success'])
    self.assertEquals(entity['counter'], 2)

class NDBCrossGroupTransactionTest(HawkeyeTestCase):
  def runTest(self):
    key = str(uuid.uuid1())
    status, headers, payload = self.http_get('/ndb/transactions?key={0}&amount=1&xg=true'.format(key))
    entity = json.loads(payload)
    self.assertTrue(entity['success'])
    self.assertEquals(entity['counter'], 1)
    self.assertEquals(entity['backup'], 1)

    status, headers, payload = self.http_get('/ndb/transactions?key={0}&amount=1&xg=true'.format(key))
    entity = json.loads(payload)
    self.assertTrue(entity['success'])
    self.assertEquals(entity['counter'], 2)
    self.assertEquals(entity['backup'], 2)

    status, headers, payload = self.http_get('/ndb/transactions?key={0}&amount=3&xg=true'.format(key))
    entity = json.loads(payload)
    self.assertFalse(entity['success'])
    self.assertEquals(entity['counter'], 2)
    self.assertEquals(entity['backup'], 2)

def suite():
  suite = HawkeyeTestSuite('NDB Test Suite')
  suite.addTest(NDBCleanupTest())
  suite.addTest(SimpleKindAwareNDBInsertTest())
  suite.addTest(KindAwareNDBInsertWithParentTest())
  suite.addTest(SimpleKindAwareNDBQueryTest())
  suite.addTest(NDBAncestorQueryTest())
  suite.addTest(NDBSinglePropertyBasedQueryTest())
  suite.addTest(NDBOrderedResultQueryTest())
  suite.addTest(NDBLimitedResultQueryTest())
  suite.addTest(NDBProjectionQueryTest())
  suite.addTest(NDBCompositeQueryTest())
  suite.addTest(NDBGQLTest())
  suite.addTest(NDBInQueryTest())
  suite.addTest(NDBCursorTest())
  suite.addTest(SimpleNDBTransactionTest())
  suite.addTest(NDBCrossGroupTransactionTest())
  return suite