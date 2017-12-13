import json
import urllib

from hawkeye_test_runner import DeprecatedHawkeyeTestCase, HawkeyeTestSuite


class FetchLogTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    requests = [['two logs are given', 'two are desired'],
                ['this is the first request', 'so expect it last']]
    for request in reversed(requests):
      payload = urllib.urlencode({'message': request}, doseq=True)
      self.http_post('/logserver', payload)

    response = self.http_get('/logserver?count={}'.format(len(requests)))
    self.assertEquals(response.status, 200)
    self.assertListEqual(requests, json.loads(response.payload))

class AutoFlushLogTest(DeprecatedHawkeyeTestCase):
  """ This test is to make sure that wee don't get duplicate log entries from
  autoflushing."""
  def run_hawkeye_test(self):
    # The log threshold for flushing is 50 so we make it 51 so that it will
    # autoflush.
    log_lines = 51
    request = ["request line {}".format(i) for i in range(log_lines)]

    payload = urllib.urlencode({'message': request}, doseq=True)
    self.http_post('/logserver', payload)

    response = self.http_get('/logserver?count=1')
    self.assertEquals(response.status, 200)
    results = json.loads(response.payload)

    self.assertListEqual(results[0], request)


def suite(lang, app):
  suite = HawkeyeTestSuite('Logservice Test Suite', 'logservice')

  if lang == 'python':
    suite.addTests(FetchLogTest.all_cases(app))
    suite.addTests(AutoFlushLogTest.all_cases(app))

  return suite
