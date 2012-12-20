import json
from time import sleep
from unittest.suite import TestSuite
import uuid
from hawkeye_test_case import HawkeyeTestCase, HawkeyeConstants

__author__ = 'hiranya'

ndb_all_projects = {}
ndb_synapse_modules = {}

class NDBCleanupTest(HawkeyeTestCase):
  def runTest(self):
    response = self.http_delete('/ndb/project')
    self.assertEquals(response.status, 200)
    response = self.http_delete('/ndb/module')
    self.assertEquals(response.status, 200)

class SimpleKindAwareNDBInsertTest(HawkeyeTestCase):
  def runTest(self):
    global ndb_all_projects

    response = self.http_post('/ndb/project',
      'name={0}&description=Mediation Engine&rating=8&license=L1'.format(
        HawkeyeConstants.PROJECT_SYNAPSE))
    dict = json.loads(response.read())
    self.assertEquals(response.status, 201)
    self.assertTrue(dict['success'])
    project_id = dict['project_id']
    self.assertTrue(project_id is not None)
    ndb_all_projects[HawkeyeConstants.PROJECT_SYNAPSE] = project_id

    response = self.http_post('/ndb/project',
      'name={0}&description=XML Parser&rating=6&license=L1'.format(HawkeyeConstants.PROJECT_XERCES))
    dict = json.loads(response.read())
    self.assertEquals(response.status, 201)
    self.assertTrue(dict['success'])
    project_id = dict['project_id']
    self.assertTrue(project_id is not None)
    ndb_all_projects[HawkeyeConstants.PROJECT_XERCES] = project_id

    response = self.http_post('/ndb/project',
      'name={0}&description=MapReduce Framework&rating=10&license=L2'.format(
        HawkeyeConstants.PROJECT_HADOOP))
    dict = json.loads(response.read())
    self.assertEquals(response.status, 201)
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
    response = self.http_post('/ndb/module',
      'name={0}&description=Mediation Core&project_id={1}'.format(HawkeyeConstants.MOD_CORE,
        ndb_all_projects[HawkeyeConstants.PROJECT_SYNAPSE]))
    dict = json.loads(response.read())
    self.assertEquals(response.status, 201)
    self.assertTrue(dict['success'])
    module_id = dict['module_id']
    self.assertTrue(module_id is not None)
    ndb_synapse_modules[HawkeyeConstants.MOD_CORE] = module_id

    response = self.http_post('/ndb/module',
      'name={0}&description=NIO HTTP transport&project_id={1}'.format(HawkeyeConstants.MOD_NHTTP,
        ndb_all_projects[HawkeyeConstants.PROJECT_SYNAPSE]))
    dict = json.loads(response.read())
    self.assertEquals(response.status, 201)
    self.assertTrue(dict['success'])
    module_id = dict['module_id']
    self.assertTrue(module_id is not None)
    ndb_synapse_modules[HawkeyeConstants.MOD_NHTTP] = module_id

class SimpleKindAwareNDBQueryTest(HawkeyeTestCase):
  def runTest(self):
    project_list = self.assert_and_get_list('/ndb/project')
    for entry in project_list:
      response = self.http_get('/ndb/project?id={0}'.format(entry['project_id']))
      list = json.loads(response.read())
      dict = list[0]
      self.assertEquals(len(list), 1)
      self.assertEquals(dict['name'], entry['name'])

    module_list = self.assert_and_get_list('/ndb/module')
    for entry in module_list:
      response = self.http_get('/ndb/module?id={0}'.format(entry['module_id']))
      list = json.loads(response.read())
      dict = list[0]
      self.assertEquals(len(list), 1)
      self.assertEquals(dict['name'], entry['name'])

class SimpleNDBTransactionTest(HawkeyeTestCase):
  def runTest(self):
    key = str(uuid.uuid1())
    response = self.http_get('/ndb/transactions?key={0}&amount=1'.format(key))
    entity = json.loads(response.read())
    self.assertTrue(entity['success'])
    self.assertEquals(entity['counter'], 1)

    response = self.http_get('/ndb/transactions?key={0}&amount=1'.format(key))
    entity = json.loads(response.read())
    self.assertTrue(entity['success'])
    self.assertEquals(entity['counter'], 2)

    response = self.http_get('/ndb/transactions?key={0}&amount=3'.format(key))
    entity = json.loads(response.read())
    self.assertFalse(entity['success'])
    self.assertEquals(entity['counter'], 2)

class NDBCrossGroupTransactionTest(HawkeyeTestCase):
  def runTest(self):
    key = str(uuid.uuid1())
    response = self.http_get('/ndb/transactions?key={0}&amount=1&xg=true'.format(key))
    entity = json.loads(response.read())
    self.assertTrue(entity['success'])
    self.assertEquals(entity['counter'], 1)
    self.assertEquals(entity['backup'], 1)

    response = self.http_get('/ndb/transactions?key={0}&amount=1&xg=true'.format(key))
    entity = json.loads(response.read())
    self.assertTrue(entity['success'])
    self.assertEquals(entity['counter'], 2)
    self.assertEquals(entity['backup'], 2)

    response = self.http_get('/ndb/transactions?key={0}&amount=3&xg=true'.format(key))
    entity = json.loads(response.read())
    self.assertFalse(entity['success'])
    self.assertEquals(entity['counter'], 2)
    self.assertEquals(entity['backup'], 2)

def suite():
  suite = TestSuite()
  suite.addTest(NDBCleanupTest())
  suite.addTest(SimpleKindAwareNDBInsertTest())
  suite.addTest(KindAwareNDBInsertWithParentTest())
  suite.addTest(SimpleKindAwareNDBQueryTest())
  suite.addTest(SimpleNDBTransactionTest())
  suite.addTest(NDBCrossGroupTransactionTest())
  return suite