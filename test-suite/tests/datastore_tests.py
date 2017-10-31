import json
import Queue
import ssl
import time
import urllib
import urllib2
import uuid
from threading import Thread
from time import sleep

from hawkeye_test_runner import HawkeyeTestSuite, DeprecatedHawkeyeTestCase
from hawkeye_utils import HawkeyeConstants

__author__ = 'hiranya'

ALL_PROJECTS = {}
SYNAPSE_MODULES = {}

class DataStoreCleanupTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_delete('/datastore/module')
    self.assertEquals(response.status, 200)
    response = self.http_delete('/datastore/project')
    self.assertEquals(response.status, 200)
    response = self.http_delete('/datastore/transactions')
    self.assertEquals(response.status, 200)

class SimpleKindAwareInsertTest(DeprecatedHawkeyeTestCase):
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

class KindAwareInsertWithParentTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_post('/datastore/module',
      'name={0}&description=A Mediation Core&project_id={1}'.format(
        HawkeyeConstants.MOD_CORE,
        ALL_PROJECTS[HawkeyeConstants.PROJECT_SYNAPSE]))
    mod_info = json.loads(response.payload)
    self.assertEquals(response.status, 201)
    self.assertTrue(mod_info['success'])
    module_id = mod_info['module_id']
    self.assertTrue(module_id is not None)
    SYNAPSE_MODULES[HawkeyeConstants.MOD_CORE] = module_id

    response = self.http_post('/datastore/module',
      'name={0}&description=Z NIO HTTP transport&project_id={1}'.format(
        HawkeyeConstants.MOD_NHTTP,
        ALL_PROJECTS[HawkeyeConstants.PROJECT_SYNAPSE]))
    mod_info = json.loads(response.payload)
    self.assertEquals(response.status, 201)
    self.assertTrue(mod_info['success'])
    module_id = mod_info['module_id']
    self.assertTrue(module_id is not None)
    SYNAPSE_MODULES[HawkeyeConstants.MOD_NHTTP] = module_id

class SimpleKindAwareQueryTest(DeprecatedHawkeyeTestCase):
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

class ZigZagQueryTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/datastore/zigzag')
    self.assertEquals(response.status, 200)

class AncestorQueryTest(DeprecatedHawkeyeTestCase):
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

class OrderedKindAncestorQueryTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    entity_list = self.assert_and_get_list('/datastore/project_modules?' \
      'project_id={0}&order=module_id'.format(\
                    ALL_PROJECTS[HawkeyeConstants.PROJECT_SYNAPSE]))
    modules = []
    for entity in entity_list:
      if entity['type'] == 'module':
        modules.append(entity['name'])

    entity_list = self.assert_and_get_list('/datastore/project_modules?' \
      'project_id={0}&order=description'.format(\
                    ALL_PROJECTS[HawkeyeConstants.PROJECT_SYNAPSE]))
    modules = []
    for entity in entity_list:
      if entity['type'] == 'module':
        modules.append(entity['name'])

    entity_list = self.assert_and_get_list('/datastore/project_modules?' \
      'project_id={0}&order=name'.format(\
                    ALL_PROJECTS[HawkeyeConstants.PROJECT_SYNAPSE]))
    modules = []
    for entity in entity_list:
      if entity['type'] == 'module':
        modules.append(entity['name'])
    self.assertEquals(len(modules), 2)
    self.assertTrue(modules.index(HawkeyeConstants.MOD_CORE) != -1)
    self.assertTrue(modules.index(HawkeyeConstants.MOD_NHTTP) != -1)


class KindlessQueryTest(DeprecatedHawkeyeTestCase):
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

class KindlessAncestorQueryTest(DeprecatedHawkeyeTestCase):
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

class QueryByKeyNameTest(DeprecatedHawkeyeTestCase):
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

class SinglePropertyBasedQueryTest(DeprecatedHawkeyeTestCase):
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

class OrderedResultQueryTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    entity_list = self.assert_and_get_list('/datastore/project_ratings?'
                                           'rating=6&comparator=ge&desc=true')
    self.assertEquals(len(entity_list), 3)
    last_rating = 100
    for entity in entity_list:
      self.assertTrue(entity['rating'], last_rating)
      last_rating = entity['rating']

class LimitedResultQueryTest(DeprecatedHawkeyeTestCase):
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

class ProjectionQueryTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    entity_list = self.assert_and_get_list('/datastore/project_fields?'
                                           'fields=project_id,name')
    self.assertEquals(len(entity_list), 3)
    for entity in entity_list:
      self.assertTrue(entity.get('rating') is None)
      self.assertTrue(entity.get('description') is None)
      self.assertTrue(entity['project_id'] is not None)
      self.assertTrue(entity['name'] is not None)

    entity_list = self.assert_and_get_list('/datastore/project_fields?'
                                           'fields=name,rating&rate_limit=8')
    self.assertEquals(len(entity_list), 2)
    for entity in entity_list:
      self.assertTrue(entity['rating'] is not None)
      self.assertTrue(entity.get('description') is None)
      self.assertTrue(entity.get('project_id') is None)
      self.assertTrue(entity['name'] is not None)
      self.assertNotEquals(entity['name'], HawkeyeConstants.PROJECT_XERCES)

class GQLProjectionQueryTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    entity_list = self.assert_and_get_list('/datastore/project_fields?'
                                           'fields=name,rating&gql=true')
    self.assertEquals(len(entity_list), 3)
    for entity in entity_list:
      self.assertTrue(entity['rating'] is not None)
      self.assertTrue(entity.get('description') is None)
      self.assertTrue(entity.get('project_id') is None)
      self.assertTrue(entity['name'] is not None)

class CompositeQueryTest(DeprecatedHawkeyeTestCase):
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

class SimpleTransactionTest(DeprecatedHawkeyeTestCase):
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

class CrossGroupTransactionTest(DeprecatedHawkeyeTestCase):
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

class QueryCursorTest(DeprecatedHawkeyeTestCase):
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

class JDOIntegrationTest(DeprecatedHawkeyeTestCase):
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

class JPAIntegrationTest(DeprecatedHawkeyeTestCase):
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

class ComplexQueryCursorTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/datastore/complex_cursor')
    self.assertEquals(response.status, 200)

class CountQueryTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/datastore/count_query')
    self.assertEquals(response.status, 200)

class CompositeMultiple(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/datastore/composite_multiple')
    self.assertEquals(response.status, 200)

class ConcurrentTransactionTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/datastore/concurrent_transactions')
    self.assertEquals(response.status, 200)

class QueryingAfterFailedTxn(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/datastore/querying_after_failed_txn')
    self.assertEquals(response.status, 200)

class QueryPagination(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/datastore/query_pagination')
    self.assertEquals(response.status, 200)

class MaxGroupsInTxn(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/datastore/max_groups_in_txn')
    self.assertEquals(response.status, 200)

class IndexIntegrity(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/datastore/index_integrity')
    self.assertEquals(response.status, 200)

class MultipleEqualityFilters(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/datastore/multiple_equality_filters')
    self.assertEquals(response.status, 200)

class CursorWithZigzagMerge(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/datastore/cursor_with_zigzag_merge')
    self.assertEquals(response.status, 200)

class RepeatedProperties(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/datastore/repeated_properties')
    self.assertEquals(response.status, 200)

class CompositeProjection(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/datastore/composite_projection')
    self.assertEquals(response.status, 200)

class CursorQueries(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/datastore/cursor_queries')
    self.assertEquals(response.status, 200)

class IndexVersatility(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/datastore/index_versatility')
    self.assertEquals(response.status, 200)

class JavaProjectionQueryTest(DeprecatedHawkeyeTestCase):
  def tearDown(self):
    self.http_delete('/datastore/projection_query')

  def run_hawkeye_test(self):
    response = self.http_post('/datastore/projection_query', '')
    self.assertEquals(response.status, 200)
    response = self.http_get('/datastore/projection_query')

class QueryLimitTest(DeprecatedHawkeyeTestCase):
  def tearDown(self):
    self.http_delete('/datastore/limit_test')

  def run_hawkeye_test(self):
    response = self.http_get('/datastore/limit_test')
    self.assertEquals(response.status, 200)

class LongTxRead(DeprecatedHawkeyeTestCase):
  ID = 'long-tx-test'
  RESPONSES = Queue.Queue()

  def tearDown(self):
    self.http_delete('/datastore/long_tx_read?id={}'.format(self.ID))

  def setUp(self):
    self.http_post('/datastore/long_tx_read', 'id={}'.format(self.ID))

  def run_hawkeye_test(self):
    def fetch_succeeded(url):
      try:
        urllib2.urlopen(url)
        self.RESPONSES.put(True)
      except urllib2.HTTPError:
        self.RESPONSES.put(False)

    url = self.app.build_url(
      '/python/datastore/long_tx_read?id={}'.format(self.ID), https=False
    )
    thread1 = Thread(target=fetch_succeeded, args=(url,))
    thread2 = Thread(target=fetch_succeeded, args=(url,))

    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    self.assertTrue(self.RESPONSES.get())
    self.assertTrue(self.RESPONSES.get())

class CursorWithRepeatedProp(DeprecatedHawkeyeTestCase):
  def tearDown(self):
    self.http_delete('/datastore/cursor_with_repeated_prop')

  def setUp(self):
    # Insert entities to query.
    self.http_post('/datastore/cursor_with_repeated_prop', payload='')

  def run_hawkeye_test(self):
    response = self.http_get('/datastore/cursor_with_repeated_prop')
    self.assertEqual(response.status, 200)
    results = json.loads(response.payload)
    self.assertEqual(len(results), 1)

class TxInvalidation(DeprecatedHawkeyeTestCase):
  KEY = 'tx-invalidation-test'
  RESPONSE = None

  def tearDown(self):
    self.http_delete('/datastore/tx_invalidation?key={}'.format(self.KEY))

  def run_hawkeye_test(self):
    context = ssl._create_unverified_context()

    def tx_succeeded(url, payload):
      response = urllib2.urlopen(url, payload, context=context)
      self.RESPONSE = response.read()

    url = self.app.build_url('/python/datastore/tx_invalidation')

    tx_payload = urllib.urlencode({'key': self.KEY, 'txn': True})
    thread = Thread(target=tx_succeeded, args=(url, tx_payload))
    thread.start()

    # The tx_payload request sleeps for 1 second between a get and put inside
    # a transaction. This smaller sleep aims to run a put (from the
    # non_tx_payload request) between those two calls.
    time.sleep(.5)

    non_tx_payload = urllib.urlencode({'key': self.KEY, 'txn': False})
    urllib2.urlopen(url, non_tx_payload, context=context)

    thread.join()
    response = json.loads(self.RESPONSE)
    # The first transaction should be invalidated by the concurrent put.
    self.assertFalse(response['txnSucceeded'])

def suite(lang, app):
  suite = HawkeyeTestSuite('Datastore Test Suite', 'datastore')
  suite.addTests(DataStoreCleanupTest.all_cases(app))
  suite.addTests(SimpleKindAwareInsertTest.all_cases(app))
  suite.addTests(KindAwareInsertWithParentTest.all_cases(app))
  suite.addTests(SimpleKindAwareQueryTest.all_cases(app))
  suite.addTests(AncestorQueryTest.all_cases(app))
  suite.addTests(OrderedKindAncestorQueryTest.all_cases(app))
  suite.addTests(KindlessQueryTest.all_cases(app))
  suite.addTests(KindlessAncestorQueryTest.all_cases(app))
  suite.addTests(QueryByKeyNameTest.all_cases(app))
  suite.addTests(SinglePropertyBasedQueryTest.all_cases(app))
  suite.addTests(OrderedResultQueryTest.all_cases(app))
  suite.addTests(LimitedResultQueryTest.all_cases(app))
  suite.addTests(ProjectionQueryTest.all_cases(app))
  suite.addTests(CompositeQueryTest.all_cases(app))
  suite.addTests(SimpleTransactionTest.all_cases(app))
  suite.addTests(CrossGroupTransactionTest.all_cases(app))
  suite.addTests(QueryCursorTest.all_cases(app))
  suite.addTests(ComplexQueryCursorTest.all_cases(app))
  suite.addTests(CountQueryTest.all_cases(app))
  suite.addTests(IndexVersatility.all_cases(app))

  if lang == 'python':
    suite.addTests(ZigZagQueryTest.all_cases(app))
    suite.addTests(CompositeMultiple.all_cases(app))
    suite.addTests(GQLProjectionQueryTest.all_cases(app))
    suite.addTests(ConcurrentTransactionTest.all_cases(app))
    suite.addTests(QueryingAfterFailedTxn.all_cases(app))
    suite.addTests(QueryPagination.all_cases(app))
    suite.addTests(MaxGroupsInTxn.all_cases(app))
    suite.addTests(IndexIntegrity.all_cases(app))
    suite.addTests(MultipleEqualityFilters.all_cases(app))
    suite.addTests(CursorWithZigzagMerge.all_cases(app))
    suite.addTests(RepeatedProperties.all_cases(app))
    suite.addTests(CompositeProjection.all_cases(app))
    suite.addTests(CursorQueries.all_cases(app))
    suite.addTests(LongTxRead.all_cases(app))
    suite.addTests(CursorWithRepeatedProp.all_cases(app))
    suite.addTests(TxInvalidation.all_cases(app))
  elif lang == 'java':
    suite.addTests(JDOIntegrationTest.all_cases(app))
    suite.addTests(JPAIntegrationTest.all_cases(app))
    suite.addTests(JavaProjectionQueryTest.all_cases(app))
    suite.addTests(QueryLimitTest.all_cases(app))

  return suite
