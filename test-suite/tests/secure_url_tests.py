from hawkeye_utils import HawkeyeTestCase, HawkeyeTestSuite

__author__ = 'hiranya'

class NeverSecureTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/secure/never', use_ssl=True)
    self.assertEquals(response.status, 302)
    self.assertTrue(response.headers.has_key('location'))
    redirect_url = response.headers['location']
    self.assertTrue(redirect_url.startswith('http:'))

    response = self.http_get(redirect_url, prepend_lang=False)
    self.assertEquals(response.status, 200)

class AlwaysSecureTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/secure/always')
    self.assertEquals(response.status, 302)
    self.assertTrue(response.headers.has_key('location'))
    redirect_url = response.headers['location']
    self.assertTrue(redirect_url.startswith('https:'))

    response = self.http_get(redirect_url, prepend_lang=False, use_ssl=True)
    self.assertEquals(response.status, 200)

class AlwaysSecureRegexTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/secure/always/regex1/regex2')
    self.assertEquals(response.status, 302)
    self.assertTrue(response.headers.has_key('location'))
    redirect_url = response.headers['location']
    self.assertTrue(redirect_url.startswith('https:'))

    response = self.http_get(redirect_url, prepend_lang=False, use_ssl=True)
    self.assertEquals(response.status, 200)

class NeverSecureRegexTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/secure/never/regex1/regex2', use_ssl=True)
    self.assertEquals(response.status, 302)
    self.assertTrue(response.headers.has_key('location'))
    redirect_url = response.headers['location']
    self.assertTrue(redirect_url.startswith('http:'))

    response = self.http_get(redirect_url, prepend_lang=False)
    self.assertEquals(response.status, 200)

def suite(lang):
  suite = HawkeyeTestSuite('Secure URL Test Suite', 'secure_url')
  if lang == 'python':
    suite.addTest(NeverSecureTest())
    suite.addTest(AlwaysSecureTest())
    suite.addTest(NeverSecureRegexTest())
    suite.addTest(AlwaysSecureRegexTest())
  return suite
