import json

from hawkeye_utils import HawkeyeTestCase, HawkeyeTestSuite


class SearchTestCase(HawkeyeTestCase):

  def tearDown(self):
    self.http_post('/search/clean-up', '')


class PutTest(SearchTestCase):

  def run_hawkeye_test(self):
    response = self.http_post(
      '/search/put',
      json.dumps({'index': 'index-1', 'document': [
        {
          'id': 'a',
          'text1': 'hello world',
          'text2': 'testing search api'
        },
        {
          'id': 'b',
          'anotherText': 'There is also a corresponding asynchronous method, '
                          'get_indexes_async(), which is identical except it '
                          'returns a future. To get the actual result, call '
                          'get_result() on the returned value; '
                          'that call will block.'},
      ]}))
    self.assertEquals(response.status, 200)


class GetTest(SearchTestCase):
  
  def run_hawkeye_test(self):
    response = self.http_post(
      '/search/get',
      json.dumps({'index': 'index-1', 'id': '1'}))
    self.assertEquals(response.status, 200)


class GetRangeTest(SearchTestCase):
  
  def run_hawkeye_test(self):
    response = self.http_post(
      '/search/get-range',
      json.dumps({'index': 'index-1', 'start_id': '1'}))
    self.assertEquals(response.status, 200)


class SearchTest(SearchTestCase):

  def run_hawkeye_test(self):
    response = self.http_post(
      '/search/search',
      json.dumps({'index': 'index-1', 'query': 'hello'}))
    self.assertEquals(response.status, 200)


def suite(lang):
  suite = HawkeyeTestSuite('Search API Test Suite', 'search')
  suite.addTest(PutTest())
  suite.addTest(GetTest())
  suite.addTest(GetRangeTest())
  suite.addTest(SearchTest())
  return suite
