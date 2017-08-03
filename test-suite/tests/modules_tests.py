import time

from hawkeye_test_runner import HawkeyeTestSuite, HawkeyeTestCase


class TestVersionDetails(HawkeyeTestCase):
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
  def test_default_module(self):
    # Create entity using default module
    self.app.get('/modules/create-entity', module='default',
                 params={'id': 'created-in-default'})

    # Fetch this entity using default module
    response = self.app.get('/modules/get-entity', module='default',
                            params={'id': 'created-in-default'})
    self.assertEquals(response.json(), {
      'entity': {
        'id': 'created-in-default',
        'created_at_module': 'default',
        'created_at_version': '1'
      }})

    # Fetch this entity using module-a
    response = self.app.get('/modules/get-entity', module='module-a',
                            params={'id': 'created-in-default'})
    self.assertEquals(response.json(), {
      'entity': {
        'id': 'created-in-default',
        'created_at_module': 'default',
        'created_at_version': '1',
        'new_field': None
      }})

  def test_module_a(self):
    # Create entity using default module
    self.app.get('/modules/create-entity', module='module-a',
                 params={'id': 'created-in-module-a'})

    # Fetch this entity using default module
    response = self.app.get('/modules/get-entity', module='default',
                            params={'id': 'created-in-module-a'})
    self.assertEquals(response.json(), {
      'entity': {
        'id': 'created-in-module-a',
        'created_at_module': 'module-a',
        'created_at_version': '1'
      }})

    # Fetch this entity using module-a
    response = self.app.get('/modules/get-entity', module='module-a',
                            params={'id': 'created-in-module-a'})
    self.assertEquals(response.json(), {
      'entity': {
        'id': 'created-in-module-a',
        'created_at_module': 'module-a',
        'created_at_version': '1',
        'new_field': 'new'
      }})


class TestDefaultQueueAndTarget(HawkeyeTestCase):
  def test_default_module(self):
    # Push entity-creation task to default queue from default module
    self.app.get('/modules/add-task', module='default',
                 params={'id': 'created-in-default'})
    time.sleep(2)

    # Fetch this entity using module-a
    response = self.app.get('/modules/get-entity', module='module-a',
                            params={'id': 'created-in-default'})
    self.assertEquals(response.json(), {
      'entity': {
        'id': 'created-in-default',
        'created_at_module': 'default',
        'created_at_version': '1',
        'new_field': None
      }})

  def test_module_a(self):
    # Push entity-creation task to default queue from module-a
    self.app.get('/modules/create-entity', module='module-a',
                 params={'id': 'created-in-module-a'})
    time.sleep(2)

    # Fetch this entity using module-a
    response = self.app.get('/modules/get-entity', module='module-a',
                            params={'id': 'created-in-module-a'})
    self.assertEquals(response.json(), {
      'entity': {
        'id': 'created-in-module-a',
        'created_at_module': 'module-a',
        'created_at_version': '1',
        'new_field': 'new'
      }})


def suite(lang, app):
  suite = HawkeyeTestSuite('Modules API Test Suite', 'services')
  suite.addTests(TestVersionDetails.all_cases(app))
  suite.addTests(TestCreatingAndGettingEntity.all_cases(app))
  suite.addTests(TestTaskQueueTarget.all_cases(app))
  return suite

