from hawkeye_utils import HawkeyeTestCase, HawkeyeConstants, HawkeyeTestSuite
import json
from time import sleep
import uuid

__author__ = 'hiranya'

ALL_PROJECTS = {}
SYNAPSE_MODULES = {}

class DataStoreCleanupTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_delete('/datastore/module')
    self.assertEquals(response.status, 200)
    response = self.http_delete('/datastore/project')
    self.assertEquals(response.status, 200)
    response = self.http_delete('/datastore/transactions')
    self.assertEquals(response.status, 200)

class SimpleKindAwareInsertTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_post('/datastore/project',
      'name={0}&description=Mediation Engine&rating=8&license=L1'.format(
        HawkeyeConstants.PROJECT_SYNAPSE))
    project_info = json.loads(response.payload)
    self.assertEquals(response.status, 201)
    self.assertTrue(project_info['success'])
    project_id = project_info['project_id']
    self.assertTrue(project_id is not None)
    ALL_PROJECTS[HawkeyeConstants.PROJECT_SYNAPSE] = project_id

    response = self.http_post('/datastore/project',
      'name={0}&description=XML Parser&rating=6&license=L1'.format(
        HawkeyeConstants.PROJECT_XERCES))
    project_info = json.loads(response.payload)
    self.assertEquals(response.status, 201)
    self.assertTrue(project_info['success'])
    project_id = project_info['project_id']
    self.assertTrue(project_id is not None)
    ALL_PROJECTS[HawkeyeConstants.PROJECT_XERCES] = project_id

    response = self.http_post('/datastore/project',
      'name={0}&description=MapReduce Framework&rating=10&license=L2'.format(
        HawkeyeConstants.PROJECT_HADOOP))
    project_info = json.loads(response.payload)
    self.assertEquals(response.status, 201)
    self.assertTrue(project_info['success'])
    project_id = project_info['project_id']
    self.assertTrue(project_id is not None)
    ALL_PROJECTS[HawkeyeConstants.PROJECT_HADOOP] = project_id

    # Allow some time to eventual consistency to run its course
    sleep(5)

class KindAwareInsertWithParentTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_post('/datastore/module',
      'name={0}&description=Mediation Core&project_id={1}'.format(
        HawkeyeConstants.MOD_CORE,
        ALL_PROJECTS[HawkeyeConstants.PROJECT_SYNAPSE]))
    mod_info = json.loads(response.payload)
    self.assertEquals(response.status, 201)
    self.assertTrue(mod_info['success'])
    module_id = mod_info['module_id']
    self.assertTrue(module_id is not None)
    SYNAPSE_MODULES[HawkeyeConstants.MOD_CORE] = module_id

    response = self.http_post('/datastore/module',
      'name={0}&description=NIO HTTP transport&project_id={1}'.format(
        HawkeyeConstants.MOD_NHTTP,
        ALL_PROJECTS[HawkeyeConstants.PROJECT_SYNAPSE]))
    mod_info = json.loads(response.payload)
    self.assertEquals(response.status, 201)
    self.assertTrue(mod_info['success'])
    module_id = mod_info['module_id']
    self.assertTrue(module_id is not None)
    SYNAPSE_MODULES[HawkeyeConstants.MOD_NHTTP] = module_id

class SimpleKindAwareQueryTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    project_list = self.assert_and_get_list('/datastore/project')
    for entry in project_list:
      response = self.http_get('/datastore/project?id={0}'.
        format(entry['project_id']))
      entity_list = json.loads(response.payload)
      project_info = entity_list[0]
      self.assertEquals(len(entity_list), 1)
      self.assertEquals(project_info['name'], entry['name'])

    module_list = self.assert_and_get_list('/datastore/module')
    for entry in module_list:
      response = self.http_get('/datastore/module?id={0}'.
        format(entry['module_id']))
      entity_list = json.loads(response.payload)
      mod_info = entity_list[0]
      self.assertEquals(len(entity_list), 1)
      self.assertEquals(mod_info['name'], entry['name'])

class AncestorQueryTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    entity_list = self.assert_and_get_list('/datastore/project_modules?' \
      'project_id={0}'.format(ALL_PROJECTS[HawkeyeConstants.PROJECT_SYNAPSE]))
    modules = []
    for entity in entity_list:
      if entity['type'] == 'module':
        modules.append(entity['name'])

    self.assertEquals(len(modules), 2)
    self.assertTrue(modules.index(HawkeyeConstants.MOD_CORE) != -1)
    self.assertTrue(modules.index(HawkeyeConstants.MOD_NHTTP) != -1)

class KindlessQueryTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    entity_list = self.assert_and_get_list(
      '/datastore/project_keys?comparator=gt&project_id={0}'.format(
        ALL_PROJECTS[HawkeyeConstants.PROJECT_SYNAPSE]))
    self.assertTrue(len(entity_list) == 3 or len(entity_list) == 4)
    for entity in entity_list:
      self.assertNotEquals(entity['name'], HawkeyeConstants.PROJECT_SYNAPSE)

    entity_list = self.assert_and_get_list(
      '/datastore/project_keys?comparator=ge&project_id={0}'.format(
        ALL_PROJECTS[HawkeyeConstants.PROJECT_SYNAPSE]))
    self.assertTrue(len(entity_list) == 4 or len(entity_list) == 5)
    project_seen = False
    for entity in entity_list:
      if entity['name'] == HawkeyeConstants.PROJECT_SYNAPSE:
        project_seen = True
        break
    self.assertTrue(project_seen)

class KindlessAncestorQueryTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    entity_list = self.assert_and_get_list(
      '/datastore/project_keys?ancestor=true&comparator=gt&project_id={0}'.
      format(ALL_PROJECTS[HawkeyeConstants.PROJECT_SYNAPSE]))
    self.assertTrue(len(entity_list) == 1 or len(entity_list) == 2)
    for entity in entity_list:
      self.assertNotEquals(entity['name'], HawkeyeConstants.PROJECT_SYNAPSE)
      self.assertNotEquals(entity['name'], HawkeyeConstants.PROJECT_XERCES)
      self.assertNotEquals(entity['name'], HawkeyeConstants.PROJECT_HADOOP)

    entity_list = self.assert_and_get_list(
      '/datastore/project_keys?ancestor=true&comparator=ge&project_id={0}'.
      format(ALL_PROJECTS[HawkeyeConstants.PROJECT_SYNAPSE]))
    self.assertTrue(len(entity_list) == 2 or len(entity_list) == 3)
    project_seen = False
    for entity in entity_list:
      self.assertNotEquals(entity['name'], HawkeyeConstants.PROJECT_XERCES)
      self.assertNotEquals(entity['name'], HawkeyeConstants.PROJECT_HADOOP)
      if entity['name'] == 'Synapse':
        project_seen = True
        break
    self.assertTrue(project_seen)

class QueryByKeyNameTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/datastore/entity_names?project_name={0}'.
      format(HawkeyeConstants.PROJECT_SYNAPSE))
    entity = json.loads(response.payload)
    self.assertEquals(entity['project_id'],
      ALL_PROJECTS[HawkeyeConstants.PROJECT_SYNAPSE])

    response = self.http_get('/datastore/entity_names?project_name={0}&' \
                             'module_name={1}'.
      format(HawkeyeConstants.PROJECT_SYNAPSE, HawkeyeConstants.MOD_CORE))
    entity = json.loads(response.payload)
    self.assertEquals(entity['module_id'],
      SYNAPSE_MODULES[HawkeyeConstants.MOD_CORE])

class SinglePropertyBasedQueryTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    entity_list = self.assert_and_get_list('/datastore/project_ratings?'
                                           'rating=10&comparator=eq')
    self.assertEquals(len(entity_list), 1)
    self.assertEquals(entity_list[0]['name'], HawkeyeConstants.PROJECT_HADOOP)

    entity_list = self.assert_and_get_list('/datastore/project_ratings?'
                                           'rating=6&comparator=gt')
    self.assertEquals(len(entity_list), 2)
    for entity in entity_list:
      self.assertNotEquals(entity['name'], HawkeyeConstants.PROJECT_XERCES)

    entity_list = self.assert_and_get_list('/datastore/project_ratings?'
                                           'rating=6&comparator=ge')
    self.assertEquals(len(entity_list), 3)

    entity_list = self.assert_and_get_list('/datastore/project_ratings?'
                                           'rating=8&comparator=lt')
    self.assertEquals(len(entity_list), 1)
    self.assertEquals(entity_list[0]['name'], HawkeyeConstants.PROJECT_XERCES)

    entity_list = self.assert_and_get_list('/datastore/project_ratings?'
                                           'rating=8&comparator=le')
    self.assertEquals(len(entity_list), 2)
    for entity in entity_list:
      self.assertNotEquals(entity['name'], HawkeyeConstants.PROJECT_HADOOP)

    entity_list = self.assert_and_get_list('/datastore/project_ratings?'
                                           'rating=8&comparator=ne')
    self.assertEquals(len(entity_list), 2)
    for entity in entity_list:
      self.assertNotEquals(entity['name'], HawkeyeConstants.PROJECT_SYNAPSE)

    try:
      self.assert_and_get_list('/datastore/project_ratings?'
                               'rating=5&comparator=le')
      self.fail('Returned an unexpected result')
    except AssertionError:
      pass

class OrderedResultQueryTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    entity_list = self.assert_and_get_list('/datastore/project_ratings?'
                                           'rating=6&comparator=ge&desc=true')
    self.assertEquals(len(entity_list), 3)
    last_rating = 100
    for entity in entity_list:
      self.assertTrue(entity['rating'], last_rating)
      last_rating = entity['rating']

class LimitedResultQueryTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    entity_list = self.assert_and_get_list('/datastore/project_ratings?'
                                           'rating=6&comparator=ge&limit=2')
    self.assertEquals(len(entity_list), 2)

    entity_list = self.assert_and_get_list('/datastore/project_ratings?rating=6'
                                           '&comparator=ge&limit=2&desc=true')
    self.assertEquals(len(entity_list), 2)
    last_rating = 100
    for entity in entity_list:
      self.assertTrue(entity['rating'], last_rating)
      last_rating = entity['rating']

class ProjectionQueryTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    entity_list = self.assert_and_get_list('/datastore/project_fields?'
                                           'fields=project_id,name')
    self.assertEquals(len(entity_list), 3)
    for entity in entity_list:
      self.assertTrue(not entity.has_key('rating') or
                      entity['rating'] is None)
      self.assertTrue(not entity.has_key('description') or
                      entity['description'] is None)
      self.assertTrue(entity['project_id'] is not None)
      self.assertTrue(entity['name'] is not None)

    entity_list = self.assert_and_get_list('/datastore/project_fields?'
                                           'fields=name,rating&rate_limit=8')
    self.assertEquals(len(entity_list), 2)
    for entity in entity_list:
      self.assertTrue(entity['rating'] is not None)
      self.assertTrue(not entity.has_key('description') or
                      entity['description'] is None)
      self.assertTrue(not entity.has_key('project_id') or
                      entity['project_id'] is None)
      self.assertTrue(entity['name'] is not None)
      self.assertNotEquals(entity['name'], HawkeyeConstants.PROJECT_XERCES)

class GQLProjectionQueryTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    entity_list = self.assert_and_get_list('/datastore/project_fields?'
                                           'fields=name,rating&gql=true')
    self.assertEquals(len(entity_list), 3)
    for entity in entity_list:
      self.assertTrue(entity['rating'] is not None)
      self.assertTrue(not entity.has_key('description') or
                      entity['description'] is None)
      self.assertTrue(not entity.has_key('project_id') or
                      entity['project_id'] is None)
      self.assertTrue(entity['name'] is not None)

class CompositeQueryTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    entity_list = self.assert_and_get_list('/datastore/project_filter?'
                                           'license=L1&rate_limit=5')
    self.assertEquals(len(entity_list), 2)
    for entity in entity_list:
      self.assertNotEquals(entity['name'], HawkeyeConstants.PROJECT_HADOOP)

    entity_list = self.assert_and_get_list('/datastore/project_filter?'
                                           'license=L1&rate_limit=8')
    self.assertEquals(len(entity_list), 1)
    self.assertEquals(entity_list[0]['name'], HawkeyeConstants.PROJECT_SYNAPSE)

    entity_list = self.assert_and_get_list('/datastore/project_filter?'
                                           'license=L2&rate_limit=5')
    self.assertEquals(len(entity_list), 1)
    self.assertEquals(entity_list[0]['name'], HawkeyeConstants.PROJECT_HADOOP)

class SimpleTransactionTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    key = str(uuid.uuid1())
    response = self.http_get('/datastore/transactions?' \
                                             'key={0}&amount=1'.format(key))
    entity = json.loads(response.payload)
    self.assertTrue(entity['success'])
    self.assertEquals(entity['counter'], 1)

    response = self.http_get('/datastore/transactions?' \
                                             'key={0}&amount=1'.format(key))
    entity = json.loads(response.payload)
    self.assertTrue(entity['success'])
    self.assertEquals(entity['counter'], 2)

    response = self.http_get('/datastore/transactions?' \
                                             'key={0}&amount=3'.format(key))
    entity = json.loads(response.payload)
    self.assertFalse(entity['success'])
    self.assertEquals(entity['counter'], 2)

class CrossGroupTransactionTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    key = str(uuid.uuid1())
    response = self.http_get('/datastore/transactions?' \
                             'key={0}&amount=1&xg=true'.format(key))
    entity = json.loads(response.payload)
    self.assertTrue(entity['success'])
    self.assertEquals(entity['counter'], 1)
    self.assertEquals(entity['backup'], 1)

    response = self.http_get('/datastore/transactions?' \
                             'key={0}&amount=1&xg=true'.format(key))
    entity = json.loads(response.payload)
    self.assertTrue(entity['success'])
    self.assertEquals(entity['counter'], 2)
    self.assertEquals(entity['backup'], 2)

    response = self.http_get('/datastore/transactions?' \
                             'key={0}&amount=3&xg=true'.format(key))
    entity = json.loads(response.payload)
    self.assertFalse(entity['success'])
    self.assertEquals(entity['counter'], 2)
    self.assertEquals(entity['backup'], 2)

class QueryCursorTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    project1 = self.assert_and_get_list('/datastore/project_cursor')
    project2 = self.assert_and_get_list('/datastore/project_cursor?' \
                                        'cursor={0}'.format(project1['next']))
    project3 = self.assert_and_get_list('/datastore/project_cursor?' \
                                        'cursor={0}'.format(project2['next']))
    projects = [ project1['project'], project2['project'], project3['project'] ]
    self.assertTrue(HawkeyeConstants.PROJECT_SYNAPSE in projects)
    self.assertTrue(HawkeyeConstants.PROJECT_XERCES in projects)
    self.assertTrue(HawkeyeConstants.PROJECT_HADOOP in projects)

    project4 = self.assert_and_get_list('/datastore/project_cursor?' \
                                        'cursor={0}'.format(project3['next']))
    self.assertTrue(project4['project'] is None)
    self.assertTrue(project4['next'] is None)

class JDOIntegrationTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_put('/datastore/jdo_project',
      'name=Cassandra&rating=10')
    self.assertEquals(response.status, 201)
    project_info = json.loads(response.payload)
    self.assertTrue(project_info['success'])
    project_id = project_info['project_id']

    response = self.http_get('/datastore/jdo_project?project_id=' + project_id)
    self.assertEquals(response.status, 200)
    project_info = json.loads(response.payload)
    self.assertEquals(project_info['name'], 'Cassandra')
    self.assertEquals(project_info['rating'], 10)

    response = self.http_post('/datastore/jdo_project',
      'project_id={0}&rating=9'.format(project_id))
    self.assertEquals(response.status, 200)

    response = self.http_get('/datastore/jdo_project?project_id=' + project_id)
    self.assertEquals(response.status, 200)
    project_info = json.loads(response.payload)
    self.assertEquals(project_info['name'], 'Cassandra')
    self.assertEquals(project_info['rating'], 9)

    response = self.http_delete('/datastore/jdo_project?project_id=' + project_id)
    self.assertEquals(response.status, 200)
    response = self.http_get('/datastore/jdo_project?project_id=' + project_id)
    self.assertEquals(response.status, 404)

class JPAIntegrationTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_put('/datastore/jpa_project',
      'name=Tomcat&rating=10')
    self.assertEquals(response.status, 201)
    project_info = json.loads(response.payload)
    self.assertTrue(project_info['success'])
    project_id = project_info['project_id']

    response = self.http_get('/datastore/jpa_project?project_id=' + project_id)
    self.assertEquals(response.status, 200)
    project_info = json.loads(response.payload)
    self.assertEquals(project_info['name'], 'Tomcat')
    self.assertEquals(project_info['rating'], 10)

    response = self.http_post('/datastore/jpa_project',
      'project_id={0}&rating=9'.format(project_id))
    self.assertEquals(response.status, 200)

    response = self.http_get('/datastore/jpa_project?project_id=' + project_id)
    self.assertEquals(response.status, 200)
    project_info = json.loads(response.payload)
    self.assertEquals(project_info['name'], 'Tomcat')
    self.assertEquals(project_info['rating'], 9)

    response = self.http_delete('/datastore/jpa_project?project_id=' + project_id)
    self.assertEquals(response.status, 200)
    response = self.http_get('/datastore/jpa_project?project_id=' + project_id)
    self.assertEquals(response.status, 404)

class ComplexQueryCursorTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/datastore/complex_cursor')
    self.assertEquals(response.status, 200)

class CountQueryTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response=self.http_get('/datastore/count_query')
    self.assertEquals(response.status, 200)

def suite(lang):
  suite = HawkeyeTestSuite('Datastore Test Suite', 'datastore')
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
  suite.addTest(SimpleTransactionTest())
  suite.addTest(CrossGroupTransactionTest())
  suite.addTest(QueryCursorTest())  
  suite.addTest(ComplexQueryCursorTest())
  suite.addTest(CountQueryTest())
  
  if lang == 'python':
    suite.addTest(GQLProjectionQueryTest())
  elif lang == 'java':
    suite.addTest(JDOIntegrationTest())
    suite.addTest(JPAIntegrationTest())
    

  return suite


