from hawkeye_utils import HawkeyeTestCase, HawkeyeTestSuite

__author__ = 'aleonov'

class GetDocumentTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_post('/search/get-doc', '{"index":"index-1","id":"1"}')
    self.assertEquals(response.status, 200)

def suite(lang):
  suite = HawkeyeTestSuite('Search API Test Suite', 'search')
  suite.addTest(GetDocumentTest())
  return suite
