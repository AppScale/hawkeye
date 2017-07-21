from hawkeye_test_runner import HawkeyeTestSuite, HawkeyeTestCase


class TestVersionDetails(HawkeyeTestCase):
  def test_default_module(self):
    response = self.app.get('/modules/version-details')
    self.assertEquals(response.status, 200)
    self.assertEquals(response.json(), {
      'modules': ['default', 'module-a'],
      'current_module_versions': ['main-v1'],
      'default_version': 'main-v1',
      'current_module': 'default',
      'current_version': 'main-v1',
    })

  def test_module_a(self):
    response = self.app.get('/modules/version-details',
                            module='module-a', version='v1')
    self.assertEquals(response.status, 200)
    self.assertEquals(response.json(), {
      'modules': ['default', 'module-a'],
      'current_module_versions': ['v1'],
      'default_version': 'v1',
      'current_module': 'module-a',
      'current_version': 'v1',
    })


class TestCreatingEntity(HawkeyeTestCase):
  def test_default_module(self):
    response = self.app.get('/modules/create-entity', )
    self.assertEquals(response.status, 200)
    self.assertEquals(response.json(), {
      'modules': ['default', 'module-a'],
      'current_module_versions': ['main-v1'],
      'default_version': 'main-v1',
      'current_module': 'default',
      'current_version': 'main-v1',
    })

  def test_module_a(self):
    response = self.app.get('/modules/version-details',
                            module='module-a', version='v1')
    self.assertEquals(response.status, 200)
    self.assertEquals(response.json(), {
      'modules': ['default', 'module-a'],
      'current_module_versions': ['v1'],
      'default_version': 'v1',
      'current_module': 'module-a',
      'current_version': 'v1',
    })


def suite(lang):
  suite = HawkeyeTestSuite('Modules API Test Suite', 'modules')
  suite.addTest(TestVersionDetails)
  return suite

