import requests
from hawkeye_test_runner import (HawkeyeTestCase, HawkeyeTestSuite,
                                 DeprecatedHawkeyeTestCase)

__author__ = 'hiranya'

class NeverSecureTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/secure/never', use_ssl=True)
    self.assertEquals(response.status, 302)
    self.assertTrue('location' in response.headers)
    redirect_url = response.headers['location']
    self.assertTrue(redirect_url.startswith('http:'))

    response = requests.get(redirect_url)
    self.assertEquals(response.status_code, 200)

class AlwaysSecureTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/secure/always')
    self.assertEquals(response.status, 302)
    self.assertTrue('location' in response.headers)
    redirect_url = response.headers['location']
    self.assertTrue(redirect_url.startswith('https:'))

    response = requests.get(redirect_url, verify=False)
    self.assertEquals(response.status_code, 200)

class AlwaysSecureRegexTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/secure/always/regex1/regex2')
    self.assertEquals(response.status, 302)
    self.assertTrue('location' in response.headers)
    redirect_url = response.headers['location']
    self.assertTrue(redirect_url.startswith('https:'))

    response = requests.get(redirect_url, verify=False)
    self.assertEquals(response.status_code, 200)

class NeverSecureRegexTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/secure/never/regex1/regex2', use_ssl=True)
    self.assertEquals(response.status, 302)
    self.assertTrue('location' in response.headers)
    redirect_url = response.headers['location']
    self.assertTrue(redirect_url.startswith('http:'))

    response = requests.get(redirect_url)
    self.assertEquals(response.status_code, 200)

class HandlerOrderTest(HawkeyeTestCase):
  def test_handler_order(self):
    handlers = {
      '/{lang}/security-1/permissive-1': 'either',
      '/{lang}/security-1/permissive-2': 'always',
      '/{lang}/security-2/permissive-1': 'either',
      '/{lang}/security-2/permissive-2': 'never',
      '/{lang}/security-3/https-only-1': 'always',
      '/{lang}/security-3/https-only-2': 'either',
      '/{lang}/security-4/http-only-1': 'never',
      '/{lang}/security-4/http-only-2': 'either'
    }

    for url, secure in handlers.items():
      response = self.app.get(url, https=False)
      if secure in ('either', 'never'):
        self.assertEqual(response.status_code, 200)
      else:
        self.assertEqual(response.status_code, 302)

      response = self.app.get(url, https=True)
      if secure in ('either', 'always'):
        self.assertEqual(response.status_code, 200)
      else:
        self.assertEqual(response.status_code, 302)


def suite(lang, app):
  suite = HawkeyeTestSuite('Secure URL Test Suite', 'secure_url')
  if lang == 'python':
    suite.addTests(NeverSecureTest.all_cases(app))
    suite.addTests(AlwaysSecureTest.all_cases(app))
    suite.addTests(NeverSecureRegexTest.all_cases(app))
    suite.addTests(AlwaysSecureRegexTest.all_cases(app))
    suite.addTests(HandlerOrderTest.all_cases(app))

  return suite
