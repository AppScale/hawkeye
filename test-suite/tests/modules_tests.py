import json
import hawkeye_test_case


class TestVersionDetails(hawkeye_test_case.HawkeyeTestCase):
  def test_1(self):
    response = self.app.get('/users/home')
    # TODO
    self.assertEquals(response.status, 200)
    url_info = json.loads(response.payload)
    self.assertEquals(url_info['type'], 'login')

def suite(lang):
  suite = HawkeyeTestSuite('Modules API Test Suite', 'modules')
  suite.addTest(LoginURLTest())
  return suite

