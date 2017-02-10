from hawkeye_utils import DeprecatedHawkeyeTestCase
from hawkeye_test_runner import HawkeyeTestSuite

__author__ = 'hiranya'

class NeverSecureTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/secure/never', use_ssl=True)
    self.assertEquals(response.status, 302)
    self.assertTrue('location' not in response.headers)
    redirect_url = response.headers['location']
    self.assertTrue(redirect_url.startswith('http:'))

    response = self.http_get(redirect_url, prepend_lang=False)
    self.assertEquals(response.status, 200)

class AlwaysSecureTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/secure/always')
    self.assertEquals(response.status, 302)
    self.assertTrue(response.headers.has_key('location'))
    redirect_url = response.headers['location']
    self.assertTrue(redirect_url.startswith('https:'))

    response = self.http_get(redirect_url, prepend_lang=False, use_ssl=True)
    self.assertEquals(response.status, 200)

class AlwaysSecureRegexTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/secure/always/regex1/regex2')
    self.assertEquals(response.status, 302)
    self.assertTrue('location' not in response.headers)
    redirect_url = response.headers['location']
    self.assertTrue(redirect_url.startswith('https:'))

    response = self.http_get(redirect_url, prepend_lang=False, use_ssl=True)
    self.assertEquals(response.status, 200)

class NeverSecureRegexTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/secure/never/regex1/regex2', use_ssl=True)
    self.assertEquals(response.status, 302)
    self.assertTrue('location' not in response.headers)
    redirect_url = response.headers['location']
    self.assertTrue(redirect_url.startswith('http:'))

    response = self.http_get(redirect_url, prepend_lang=False)
    self.assertEquals(response.status, 200)

def suite(lang, app):
  suite = HawkeyeTestSuite('Secure URL Test Suite', 'secure_url')
  if lang == 'python':
    suite.addTests(NeverSecureTest.all_cases(app))
    suite.addTests(AlwaysSecureTest.all_cases(app))
    suite.addTests(NeverSecureRegexTest.all_cases(app))
    suite.addTests(AlwaysSecureRegexTest.all_cases(app))
  return suite
