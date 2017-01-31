import application
from hawkeye_test_case import HawkeyeTestCase
from hawkeye_utils import HawkeyeTestSuite

DEFAULT_MODULE = "default"
MODULE_A = "module-a"
DEFAULT_VERSION = "1"
V1 = "v1"
V2 = "v2"


class TestVersionDetails(HawkeyeTestCase):
  def test_default_module_and_version(self):
    response = self.app.get('/modules/version_details')
    self.assertEquals(response.status, 200)
    self.assertEquals(response.json(), {
      'modules': application.DEFAULT_MODULE,
      'current_module_versions': DEFAULT_VERSION,
      'default_version': DEFAULT_VERSION,
      'current_module': DEFAULT_MODULE,
      'current_version': DEFAULT_VERSION,
    })

  def test_module_a_v1(self):
    response = self.app.get('/modules/version_details',
                            module=MODULE_A, version=V1)
    self.assertEquals(response.status, 200)
    self.assertEquals(response.json(), {
      'modules': application.DEFAULT_MODULE,
      'current_module_versions': V1,
      'default_version': V2,
      'current_module': MODULE_A,
      'current_version': V1,
    })

def suite(lang):
  suite = HawkeyeTestSuite('Modules API Test Suite', 'modules')
  suite.addTest(TestVersionDetails)
  return suite

