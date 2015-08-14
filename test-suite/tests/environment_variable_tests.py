import json
import ssl
import urllib2

import hawkeye_utils
from hawkeye_utils import HawkeyeTestCase, HawkeyeTestSuite

class GetConfigEnvironmentVariableTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/env/var')
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals('baz', entry_info['value'])

class RequestAPI(HawkeyeTestCase):
  def run_hawkeye_test(self):
    config = {
      'http': {
        'handler': urllib2.HTTPHandler,
        'port': hawkeye_utils.PORT
      },
      'https': {
        'handler': urllib2.HTTPSHandler,
        'port': hawkeye_utils.PORT - hawkeye_utils.SSL_PORT_OFFSET
      }
    }
    for scheme in ['http', 'https']:
      for method in ['GET', 'PUT', 'POST', 'DELETE']:
        url = '{}://{}:{}/python/env/mirror'.\
          format(scheme, hawkeye_utils.HOST, config[scheme]['port'])
        request = urllib2.Request(url)
        request.get_method = lambda: method

        if hasattr(ssl, '_create_unverified_context'):
          context = ssl._create_unverified_context()
          response = urllib2.urlopen(request, context=context)
        else:
          response = urllib2.urlopen(request)

        response_dict = json.load(response)

        self.assertEqual(response_dict['scheme'], scheme)
        self.assertEqual(response_dict['method'], method)
        self.assertEqual(response_dict['uri'], url)

def suite(lang):
  suite = HawkeyeTestSuite('Config Environment Variable Test Suite', 'env_var')
  suite.addTest(GetConfigEnvironmentVariableTest())

  if lang == 'python':
    suite.addTest(RequestAPI())
  return suite
