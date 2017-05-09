import base64
import urllib

from hawkeye_utils import HawkeyeTestCase
from hawkeye_test_runner import HawkeyeTestSuite


class CertificateValidation(HawkeyeTestCase):
  def run_hawkeye_test(self):
    good_cert = 'https://redmine.appscale.com/'
    bad_cert = 'https://ocd.appscale.com:8080/'

    vars = {'url': base64.urlsafe_b64encode(good_cert), 'validate': 'false'}
    response = self.http_get('/urlfetch?{}'.format(urllib.urlencode(vars)))
    self.assertEqual(response.status, 200)

    vars = {'url': base64.urlsafe_b64encode(good_cert), 'validate': 'true'}
    response = self.http_get('/urlfetch?{}'.format(urllib.urlencode(vars)))
    self.assertEqual(response.status, 200)

    vars = {'url': base64.urlsafe_b64encode(bad_cert), 'validate': 'false'}
    response = self.http_get('/urlfetch?{}'.format(urllib.urlencode(vars)))
    self.assertEqual(response.status, 200)

    vars = {'url': base64.urlsafe_b64encode(bad_cert), 'validate': 'true'}
    response = self.http_get('/urlfetch?{}'.format(urllib.urlencode(vars)))
    self.assertEqual(response.status, 500)


def suite(lang):
  suite = HawkeyeTestSuite('URLFetch Suite', 'urlfetch')
  if lang == 'python':
    suite.addTest(CertificateValidation())
  return suite
