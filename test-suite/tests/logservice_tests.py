import json
import urllib

from hawkeye_test_runner import HawkeyeTestSuite
from hawkeye_utils import HawkeyeTestCase


class FetchLogTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    requests = [['two logs are given', 'two are desired'],
                ['this is the first request', 'so expect it last']]
    for request in reversed(requests):
      payload = urllib.urlencode({'message': request}, doseq=True)
      self.http_post('/logserver', payload)

    response = self.http_get('/logserver?count={}'.format(len(requests)))
    self.assertEquals(response.status, 200)
    self.assertListEqual(requests, json.loads(response.payload))


def suite(lang):
  suite = HawkeyeTestSuite('Logservice Test Suite', 'logservice')

  if lang == 'python':
    suite.addTest(FetchLogTest())

  return suite
