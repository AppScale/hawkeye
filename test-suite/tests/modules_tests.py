import time
import uuid

from collections import OrderedDict

from hawkeye_test_runner import HawkeyeTestSuite, HawkeyeTestCase


class TestVersionDetails(HawkeyeTestCase):
  """
  Verifies if app can get info about module and version.
  """

  def test_default_module(self):
    response = self.app.get('/modules/versions-details', module='default')
    self.assertEquals(response.status_code, 200)
    actual = response.json()
    self.assertEqual(actual['modules'], ['default', 'module-a'])
    self.assertEqual(actual['current_module_versions'], ['1'])
    self.assertEqual(actual['default_version'], '1')
    self.assertEqual(actual['current_module'], 'default')
    self.assertEqual(actual['current_version'], '1')
    self.assertIsInstance(actual['current_instance_id'], basestring)

  def test_module_a(self):
    response = self.app.get('/modules/versions-details', module='module-a')
    self.assertEquals(response.status_code, 200)
    actual = response.json()
    self.assertEqual(actual['modules'], ['default', 'module-a'])
    self.assertEqual(actual['current_module_versions'], ['1'])
    self.assertEqual(actual['default_version'], '1')
    self.assertEqual(actual['current_module'], 'module-a')
    self.assertEqual(actual['current_version'], '1')
    self.assertIsInstance(actual['current_instance_id'], basestring)


class TestCreatingAndGettingEntity(HawkeyeTestCase):
  """
  Verifies if expected service handles request.
  """

  def test_default_module(self):
    entity_id = str(uuid.uuid4())
    # Create entity using default module
    self.app.get('/modules/create-entity', module='default',
                 params={'id': entity_id})

    # Fetch this entity using default module
    response = self.app.get('/modules/get-entity', module='default',
                            params={'id': entity_id})
    entity = response.json()['entity']
    self.assertEquals(entity, {
      'id': entity_id,
      'created_at_module': 'default',
      'created_at_version': '1'
    })

    # Fetch this entity using module-a
    response = self.app.get('/modules/get-entity', module='module-a',
                            params={'id': entity_id})
    entity = response.json()['entity']
    self.assertEquals(entity, {
      'id': entity_id,
      'created_at_module': 'default',
      'created_at_version': '1',
      'new_field': None
    })

  def test_module_a(self):
    entity_id = str(uuid.uuid4())
    # Create entity using default module
    self.app.get('/modules/create-entity', module='module-a',
                 params={'id': entity_id})

    # Fetch this entity using default module
    response = self.app.get('/modules/get-entity', module='default',
                            params={'id': entity_id})
    entity = response.json()['entity']
    self.assertEquals(entity, {
      'id': entity_id,
      'created_at_module': 'module-a',
      'created_at_version': '1'
    })

    # Fetch this entity using module-a
    response = self.app.get('/modules/get-entity', module='module-a',
                            params={'id': entity_id})
    entity = response.json()['entity']
    self.assertEquals(entity, {
      'id': entity_id,
      'created_at_module': 'module-a',
      'created_at_version': '1',
      'new_field': 'new'
    })


class TestTaskTargets(HawkeyeTestCase):
  """
  Verifies if tasks are handled by 
  """

  def setUp(self):
    self.entity_ids = OrderedDict([
      ('default-queue', str(uuid.uuid4())),
      ('queue-with-missed-target', str(uuid.uuid4())),
      ('queue-for-default', str(uuid.uuid4())),
      ('queue-for-module-a', str(uuid.uuid4())),
      ('target-default', str(uuid.uuid4())),
      ('target-module-a', str(uuid.uuid4())),
      ('deferred-default-queue', str(uuid.uuid4())),
      ('deferred-queue-with-missed-target', str(uuid.uuid4())),
      ('deferred-queue-for-default', str(uuid.uuid4())),
      ('deferred-queue-for-module-a', str(uuid.uuid4())),
      ('deferred-target-default', str(uuid.uuid4())),
      ('deferred-target-module-a', str(uuid.uuid4())),
    ])

    # Push entity-creation tasks to default queue
    self.app.get('/modules/add-task',
                 params={'id': self.entity_ids['default-queue']})

    # Push entity-creation tasks to other queues
    self.app.get('/modules/add-task',
                 params={'id': self.entity_ids['queue-with-missed-target'],
                         'queue': 'queue-with-missed-target'})
    self.app.get('/modules/add-task',
                 params={'id': self.entity_ids['queue-for-default'],
                         'queue': 'queue-for-default'})
    self.app.get('/modules/add-task',
                 params={'id': self.entity_ids['queue-for-module-a'],
                         'queue': 'queue-for-module-a'})

    # Push entity-creation tasks with specified targets
    self.app.get('/modules/add-task',
                 params={'id': self.entity_ids['target-default'],
                         'target': 'default'})
    self.app.get('/modules/add-task',
                 params={'id': self.entity_ids['target-module-a'],
                         'target': 'module-a'})

    # Defer entity-creation tasks to default queue
    self.app.get('/modules/defer-task',
                 params={'id': self.entity_ids['deferred-default-queue']})

    # Defer entity-creation tasks to other queues
    self.app.get('/modules/defer-task',
                 params={'id': self.entity_ids['deferred-queue-with-missed-target'],
                         'queue': 'queue-with-missed-target'})
    self.app.get('/modules/defer-task',
                 params={'id': self.entity_ids['deferred-queue-for-default'],
                         'queue': 'queue-for-default'})
    self.app.get('/modules/defer-task',
                 params={'id': self.entity_ids['deferred-queue-for-module-a'],
                         'queue': 'queue-for-module-a'})

    # Defer entity-creation tasks with specified targets
    self.app.get('/modules/defer-task',
                 params={'id': self.entity_ids['deferred-target-default'],
                         'target': 'default'})
    self.app.get('/modules/defer-task',
                 params={'id': self.entity_ids['deferred-target-module-a'],
                         'target': 'module-a'})

    time.sleep(2)

  def test_task_targets(self):
    response = self.app.get('/modules/get-entities',
                            params={'id': self.entity_ids.values()})
    entities = zip(self.entity_ids.keys(), response.json()['entities'])

    expectation = {
      'default-queue': 'default',
      'queue-with-missed-target': 'default',
      'queue-for-default': 'default',
      'queue-for-module-a': 'module-a',
      'target-default': 'default',
      'target-module-a': 'module-a',
      'deferred-default-queue': 'default',
      'deferred-queue-with-missed-target': 'default',
      'deferred-queue-for-default': 'default',
      'deferred-queue-for-module-a': 'module-a',
      'deferred-target-default': 'default',
      'deferred-target-module-a': 'module-a',
    }
    miss_match = []
    for entity_alias, entity in entities:
      created_at_module = entity.get('created_at_module') if entity else None
      if created_at_module != expectation[entity_alias]:
        miss_match.append((entity_alias, created_at_module))

    self.assertEqual(miss_match, [])

  def tearDown(self):
    self.app.get('/modules/clean')


def suite(lang, app):
  suite = HawkeyeTestSuite('Modules API Test Suite', 'services')
  suite.addTests(TestVersionDetails.all_cases(app))
  suite.addTests(TestCreatingAndGettingEntity.all_cases(app))
  suite.addTests(TestTaskTargets.all_cases(app))
  return suite

