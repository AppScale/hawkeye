import json
from hawkeye_test_runner import HawkeyeTestSuite, DeprecatedHawkeyeTestCase


class GetConfigEnvironmentVariableTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/env/var')
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals('baz', entry_info['value'])

class RequestAPI(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    for scheme in ['http', 'https']:
      for method in ['GET', 'PUT', 'POST', 'DELETE']:
        path = '/python/env/mirror'
        url = self.app.build_url(path, https=scheme=='https')
        response = self.app.logged_request(method, path, https=scheme=='https')
        response_dict = response.json()

        self.assertEqual(response_dict['scheme'], scheme)
        self.assertEqual(response_dict['method'], method)
        self.assertEqual(response_dict['uri'], url)

def suite(lang, app):
  suite = HawkeyeTestSuite('Config Environment Variable Test Suite', 'env_var')
  suite.addTests(GetConfigEnvironmentVariableTest.all_cases(app))

  if lang == 'python':
    suite.addTests(RequestAPI.all_cases(app))
  return suite
