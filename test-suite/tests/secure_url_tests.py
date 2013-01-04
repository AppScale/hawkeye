from hawkeye_utils import HawkeyeTestCase, HawkeyeTestSuite

__author__ = 'hiranya'

class NeverSecureTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/secure/never', ssl=True)
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

    response = self.http_get(redirect_url, prepend_lang=False, ssl=True)
    self.assertEquals(response.status, 200)

def suite(lang):
  suite = HawkeyeTestSuite('Secure URL Test Suite', 'secure_url')
  if lang == 'python':
    suite.addTest(NeverSecureTest())
    suite.addTest(AlwaysSecureTest())
  return suite