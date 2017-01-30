import application
from hawkeye_test_case import HawkeyeTestCase
from hawkeye_utils import HawkeyeTestSuite


class TestVersionDetails(HawkeyeTestCase):
  def test_default_module_and_version(self):
    response = self.app.get('/modules/version_details')
    self.assertEquals(response.status, 200)
    self.assertEquals(response.json(), {
        'modules': application.DEFAULT_MODULE,
        'current_module_versions': 'v1',
        'default_version': 'v1',
        'current_module': 'default',
        'current_version': 'v1',
        'current_instance_id': '?'  # TODO: not none
    })

def suite(lang):
  suite = HawkeyeTestSuite('Modules API Test Suite', 'modules')
  suite.addTest(TestVersionDetails)
  return suite

