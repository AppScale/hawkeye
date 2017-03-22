import json
import ssl
import urllib2
import urlparse
from hawkeye_utils import HawkeyeTestCase, HawkeyeTestSuite
import hawkeye_utils

FILE_UPLOADS = {}

FILE1 = 'file1.txt'
FILE2 = 'file2.txt'
FILE3 = 'file3.txt'

FILE1_DATA = 'FILE UPLOAD CONTENT'
FILE2_DATA = 'AppScale Rocks!!!'
FILE3_DATA = 'ASYNC FILE UPLOAD CONTENT'

class FetchLogTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/logserver')
    print(response.body)
    self.assertEquals(response.status, 200)


def suite(lang):
  suite = HawkeyeTestSuite('Logservice Test Suite', 'logservice')
  suite.addTest(FetchLogTest())
  return suite
