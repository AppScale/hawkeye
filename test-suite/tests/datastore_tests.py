import json
from unittest.suite import TestSuite
from hawkeye_test_case import HawkeyeTestCase

__author__ = 'hiranya'

all_projects = {}
synapse_modules = {}

PROJECT_SYNAPSE = 'Synapse'
PROJECT_XERCES = 'Xerces'
PROJECT_HADOOP = 'Hadoop'

MOD_CORE = 'Core'
MOD_NHTTP = 'NHTTP'

class DataStoreCleanupTest(HawkeyeTestCase):
  def runTest(self):
    response = self.http_delete('/datastore/module')
    self.assertEquals(response.status, 200)
    response = self.http_delete('/datastore/project')
    self.assertEquals(response.status, 200)

class SimpleKindAwareInsertTest(HawkeyeTestCase):
  def runTest(self):
    global all_projects

    response = self.http_post('/datastore/project',
      'name={0}&description=Mediation Engine&rating=8&license=L1'.format(PROJECT_SYNAPSE))
    dict = json.loads(response.read())
    self.assertEquals(response.status, 201)
    self.assertTrue(dict['success'])
    project_id = dict['project_id']
    self.assertTrue(project_id is not None)
    all_projects[PROJECT_SYNAPSE] = project_id

    response = self.http_post('/datastore/project',
      'name={0}&description=XML Parser&rating=6&license=L1'.format(PROJECT_XERCES))
    dict = json.loads(response.read())
    self.assertEquals(response.status, 201)
    self.assertTrue(dict['success'])
    project_id = dict['project_id']
    self.assertTrue(project_id is not None)
    all_projects[PROJECT_XERCES] = project_id

    response = self.http_post('/datastore/project',
      'name={0}&description=MapReduce Framework&rating=10&license=L2'.format(PROJECT_HADOOP))
    dict = json.loads(response.read())
    self.assertEquals(response.status, 201)
    self.assertTrue(dict['success'])
    project_id = dict['project_id']
    self.assertTrue(project_id is not None)
    all_projects[PROJECT_HADOOP] = project_id

class KindAwareInsertWithParentTest(HawkeyeTestCase):
  def runTest(self):
    global all_projects
    global synapse_modules
    response = self.http_post('/datastore/module',
      'name={0}&description=Mediation Core&project_id={1}'.format(MOD_CORE, all_projects[PROJECT_SYNAPSE]))
    dict = json.loads(response.read())
    self.assertEquals(response.status, 201)
    self.assertTrue(dict['success'])
    module_id = dict['module_id']
    self.assertTrue(module_id is not None)
    synapse_modules[MOD_CORE] = module_id

    response = self.http_post('/datastore/module',
      'name={0}&description=NIO HTTP transport&project_id={1}'.format(MOD_NHTTP, all_projects[PROJECT_SYNAPSE]))
    dict = json.loads(response.read())
    self.assertEquals(response.status, 201)
    self.assertTrue(dict['success'])
    module_id = dict['module_id']
    self.assertTrue(module_id is not None)
    synapse_modules[MOD_NHTTP] = module_id

class SimpleKindAwareQueryTest(HawkeyeTestCase):
  def runTest(self):
    project_list = self.assert_and_get_list('/datastore/project')
    for entry in project_list:
      response = self.http_get('/datastore/project?id={0}'.format(entry['id']))
      list = json.loads(response.read())
      dict = list[0]
      self.assertEquals(len(list), 1)
      self.assertEquals(dict['name'], entry['name'])

    module_list = self.assert_and_get_list('/datastore/module')
    for entry in module_list:
      response = self.http_get('/datastore/module?id={0}'.format(entry['id']))
      list = json.loads(response.read())
      dict = list[0]
      self.assertEquals(len(list), 1)
      self.assertEquals(dict['name'], entry['name'])

class AncestorQueryTest(HawkeyeTestCase):
  def runTest(self):
    global all_projects
    entity_list = self.assert_and_get_list('/datastore/project_modules?project_id={0}'.format(all_projects[PROJECT_SYNAPSE]))
    modules = []
    for entity in entity_list:
      if entity['type'] == 'module':
        modules.append(entity['name'])

    self.assertEquals(len(modules), 2)
    self.assertTrue(modules.index(MOD_CORE) != -1)
    self.assertTrue(modules.index(MOD_NHTTP) != -1)

class KindlessQueryTest(HawkeyeTestCase):
  def runTest(self):
    entity_list = self.assert_and_get_list('/datastore/project_keys?comparator=' \
                                           'gt&project_id={0}'.format(all_projects[PROJECT_SYNAPSE]))
    self.assertTrue(len(entity_list) == 3 or len(entity_list) == 4)
    for entity in entity_list:
      self.assertNotEquals(entity['name'], PROJECT_SYNAPSE)

    entity_list = self.assert_and_get_list('/datastore/project_keys?comparator=' \
                                           'ge&project_id={0}'.format(all_projects[PROJECT_SYNAPSE]))
    self.assertTrue(len(entity_list) == 4 or len(entity_list) == 5)
    project_seen = False
    for entity in entity_list:
      if entity['name'] == PROJECT_SYNAPSE:
        project_seen = True
        break
    self.assertTrue(project_seen)

class KindlessAncestorQueryTest(HawkeyeTestCase):
  def runTest(self):
    entity_list = self.assert_and_get_list('/datastore/project_keys?ancestor=true&' \
                                           'comparator=gt&project_id={0}'.format(all_projects[PROJECT_SYNAPSE]))
    self.assertTrue(len(entity_list) == 1 or len(entity_list) == 2)
    for entity in entity_list:
      self.assertNotEquals(entity['name'], PROJECT_SYNAPSE)
      self.assertNotEquals(entity['name'], PROJECT_XERCES)
      self.assertNotEquals(entity['name'], PROJECT_HADOOP)

    entity_list = self.assert_and_get_list('/datastore/project_keys?ancestor=true&' \
                                           'comparator=ge&project_id={0}'.format(all_projects[PROJECT_SYNAPSE]))
    self.assertTrue(len(entity_list) == 2 or len(entity_list) == 3)
    project_seen = False
    for entity in entity_list:
      self.assertNotEquals(entity['name'], PROJECT_XERCES)
      self.assertNotEquals(entity['name'], PROJECT_HADOOP)
      if entity['name'] == 'Synapse':
        project_seen = True
        break
    self.assertTrue(project_seen)

class QueryByKeyNameTest(HawkeyeTestCase):
  def runTest(self):
    global synapse_modules

    response = self.http_get('/datastore/entity_names?project_name={0}'.format(PROJECT_SYNAPSE))
    entity = json.loads(response.read())
    self.assertEquals(entity['id'], all_projects[PROJECT_SYNAPSE])

    response = self.http_get('/datastore/entity_names?project_name={0}&module_name={1}'.format(
      PROJECT_SYNAPSE, MOD_CORE))
    entity = json.loads(response.read())
    self.assertEquals(entity['id'], synapse_modules[MOD_CORE])

class SinglePropertyBasedQueryTest(HawkeyeTestCase):
  def runTest(self):
    entity_list = self.assert_and_get_list('/datastore/project_ratings?rating=10&comparator=eq')
    self.assertEquals(len(entity_list), 1)
    self.assertEquals(entity_list[0]['name'], PROJECT_HADOOP)

    entity_list = self.assert_and_get_list('/datastore/project_ratings?rating=6&comparator=gt')
    self.assertEquals(len(entity_list), 2)
    for entity in entity_list:
      self.assertNotEquals(entity['name'], PROJECT_XERCES)

    entity_list = self.assert_and_get_list('/datastore/project_ratings?rating=6&comparator=ge')
    self.assertEquals(len(entity_list), 3)

    entity_list = self.assert_and_get_list('/datastore/project_ratings?rating=8&comparator=lt')
    self.assertEquals(len(entity_list), 1)
    self.assertEquals(entity_list[0]['name'], PROJECT_XERCES)

    entity_list = self.assert_and_get_list('/datastore/project_ratings?rating=8&comparator=le')
    self.assertEquals(len(entity_list), 2)
    for entity in entity_list:
      self.assertNotEquals(entity['name'], PROJECT_HADOOP)

    entity_list = self.assert_and_get_list('/datastore/project_ratings?rating=8&comparator=ne')
    self.assertEquals(len(entity_list), 2)
    for entity in entity_list:
      self.assertNotEquals(entity['name'], PROJECT_SYNAPSE)

    try:
      self.assert_and_get_list('/datastore/project_ratings?rating=5&comparator=le')
      self.fail('Returned an unexpected result')
    except AssertionError:
      pass

class OrderedResultQueryTest(HawkeyeTestCase):
  def runTest(self):
    entity_list = self.assert_and_get_list('/datastore/project_ratings?rating=6&comparator=ge&desc=true')
    self.assertEquals(len(entity_list), 3)
    last_rating = 100
    for entity in entity_list:
      self.assertTrue(entity['rating'], last_rating)
      last_rating = entity['rating']

class LimitedResultQueryTest(HawkeyeTestCase):
  def runTest(self):
    entity_list = self.assert_and_get_list('/datastore/project_ratings?rating=6&comparator=ge&limit=2')
    self.assertEquals(len(entity_list), 2)

    entity_list = self.assert_and_get_list('/datastore/project_ratings?rating=6&comparator=ge&limit=2&desc=true')
    self.assertEquals(len(entity_list), 2)
    last_rating = 100
    for entity in entity_list:
      self.assertTrue(entity['rating'], last_rating)
      last_rating = entity['rating']

class ProjectionQueryTest(HawkeyeTestCase):
  def runTest(self):
    entity_list = self.assert_and_get_list('/datastore/project_fields?fields=id,name')
    self.assertEquals(len(entity_list), 3)
    for entity in entity_list:
      self.assertTrue(entity['rating'] is None)
      self.assertTrue(entity['description'] is None)
      self.assertTrue(entity['id'] is not None)
      self.assertTrue(entity['name'] is not None)

    entity_list = self.assert_and_get_list('/datastore/project_fields?fields=name,rating&gql=true')
    self.assertEquals(len(entity_list), 3)
    for entity in entity_list:
      self.assertTrue(entity['rating'] is not None)
      self.assertTrue(entity['description'] is None)
      self.assertTrue(entity['id'] is None)
      self.assertTrue(entity['name'] is not None)

    entity_list = self.assert_and_get_list('/datastore/project_fields?fields=name,rating&rate_limit=8')
    self.assertEquals(len(entity_list), 2)
    for entity in entity_list:
      self.assertTrue(entity['rating'] is not None)
      self.assertTrue(entity['description'] is None)
      self.assertTrue(entity['id'] is None)
      self.assertTrue(entity['name'] is not None)
      self.assertNotEquals(entity['name'], PROJECT_XERCES)

class CompositeQueryTest(HawkeyeTestCase):
  def runTest(self):
    entity_list = self.assert_and_get_list('/datastore/project_filter?license=L1&rate_limit=5')
    self.assertEquals(len(entity_list), 2)
    for entity in entity_list:
      self.assertNotEquals(entity['name'], PROJECT_HADOOP)

    entity_list = self.assert_and_get_list('/datastore/project_filter?license=L1&rate_limit=8')
    self.assertEquals(len(entity_list), 1)
    self.assertEquals(entity['name'], PROJECT_SYNAPSE)

    entity_list = self.assert_and_get_list('/datastore/project_filter?license=L2&rate_limit=5')
    self.assertEquals(len(entity_list), 1)
    self.assertEquals(entity_list[0]['name'], PROJECT_HADOOP)

def suite():
  suite = TestSuite()
  suite.addTest(DataStoreCleanupTest())
  suite.addTest(SimpleKindAwareInsertTest())
  suite.addTest(KindAwareInsertWithParentTest())
  suite.addTest(SimpleKindAwareQueryTest())
  suite.addTest(AncestorQueryTest())
  suite.addTest(KindlessQueryTest())
  suite.addTest(KindlessAncestorQueryTest())
  suite.addTest(QueryByKeyNameTest())
  suite.addTest(SinglePropertyBasedQueryTest())
  suite.addTest(OrderedResultQueryTest())
  suite.addTest(LimitedResultQueryTest())
  suite.addTest(ProjectionQueryTest())
  suite.addTest(CompositeQueryTest())
  return suite


