import json
from hawkeye_utils import HawkeyeTestCase, HawkeyeTestSuite

__author__ = 'chris'

class GetConfigEnvironmentVariableTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/env_var')
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals('baz', entry_info['value'])

def suite(lang):
  suite = HawkeyeTestSuite('Config Environment Variable Test Suite', 'env_var')
  suite.addTest(GetConfigEnvironmentVariableTest())
  return suite
