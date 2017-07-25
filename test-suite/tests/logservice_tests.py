import json
import urllib

from hawkeye_test_runner import DeprecatedHawkeyeTestCase, HawkeyeTestSuite


class FinishedRequestTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    payload = urllib.urlencode({'message': 'foo'})
    response = self.http_post('/logserver/put', payload)
    request_id = json.loads(response.payload)['request_id']

    # Ensure the request was marked as being finished.
    response = self.http_get('/logserver/is_finished?id={}'.format(request_id))
    self.assertEquals(response.status, 200)
    self.assertTrue(json.loads(response.payload)['finished'])

    # Make sure non-existent requests are marked as not finished.
    response = self.http_get('/logserver/is_finished?id={}'.format('no-id'))
    self.assertEqual(response.status, 200)
    self.assertFalse(json.loads(response.payload)['finished'])


class QueryLogsTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    requests = [['two logs are given', 'two are desired'],
                ['this is the first request', 'so expect it last']]
    for request in reversed(requests):
      payload = urllib.urlencode({'message': request}, doseq=True)
      self.http_post('/logserver/put', payload)

    response = self.http_get('/logserver/query?count={}'.format(len(requests)))
    self.assertEquals(response.status, 200)
    self.assertListEqual(requests, json.loads(response.payload))


def suite(lang, app):
  suite = HawkeyeTestSuite('Logservice Test Suite', 'logservice')

  if lang == 'python':
    suite.addTests(FinishedRequestTest.all_cases(app))
    suite.addTests(QueryLogsTest.all_cases(app))

  return suite
