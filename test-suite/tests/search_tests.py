import json

from hawkeye_test_runner import HawkeyeTestCase, HawkeyeTestSuite


class SearchTestCase(HawkeyeTestCase):

  def tearDown(self):
    self.app.post('/python/search/clean-up','')


class PutTest(SearchTestCase):

  def test_search_put(self):
    response = self.app.post(
      '/python/search/put',
      json={"index": "index-1", "documents": [
        {
          "id": "a",
          "text1": "hello world",
          "text2": "testing search api and world"
        },
        {
          "id": "b",
          "anotherText": "There is also a corresponding asynchronous method, "
        },
        {
	  "id": "c",
          "text3": "This string also contains the word world and api"
        },
        {
          "id": "firstdate",
          "date_entered": "2018-12-12",
          "text4": "This is a test of the national broadcasting system"
        },
        {
          "id": "seconddate",
          "date_entered": "2019-04-04",
          "text5": "Who are the britons?"
        }
      ]})
    self.assertEquals(response.status_code, 200)

class GetTest(SearchTestCase):
  
  def test_search_get(self):
    response = self.app.post(
      '/python/search/get',
      json={"index": "index-1", "id": "a"})
    self.assertEquals(response.status_code, 200)


#class GetRangeTest(SearchTestCase):
#
#  def run_hawkeye_test(self):
#    response = self.http_post(
#      '/search/get-range',
#      json.dumps({'index': 'index-1', 'start_id': '1'}))
#    self.assertEquals(response.status, 200)
#
#
class SearchTest(SearchTestCase):

  def test_search_simple_query(self):
    response = self.app.post(
      '/python/search/search',
      json={"index": "index-1", "query": "hello"})
    self.assertEquals(response.status_code, 200)
    response_json = response.json()
    self.assertIn('documents', response_json)
    documents = response_json['documents']
    self.assertEqual(len(documents), 1)
    self.assertIn('text1',documents[0])
    self.assertIn('text2',documents[0])

  # Should have no result
  def test_search_query_AND_no_results(self):
    response = self.app.post(
      '/python/search/search',
      json={"index": "index-1", "query": "hello AND corresponding"})
    self.assertEquals(response.status_code, 200)
    self.assertIn('documents', response.json())
    self.assertEquals(len(response.json()['documents']), 0)

  def test_search_query_AND_two_results(self):
    response = self.app.post(
      '/python/search/search',
      json={"index": "index-1", "query": "world and api"})

    self.assertEquals(response.status_code, 200)
    self.assertIn('documents', response.json())
    documents = response.json()['documents']
    self.assertEquals(len(documents), 2)

  def test_search_query_OR(self):
    response = self.app.post(
      '/python/search/search',
      json={"index": "index-1", "query": "hello OR britons"})

    self.assertEquals(response.status_code, 200)
    self.assertIn('documents', response.json())
    documents = response.json()['documents']
    self.assertEquals(len(documents), 2)

  def test_search_query_date_global_equal(self):
    """
    Generic date entry in the query string
    """
    response = self.app.post(
      '/python/search/search',
      json={"index": "index-1", "query": "2018-12-12"})

    self.assertEquals(response.status_code, 200)
    self.assertIn('documents', response.json())
    documents = response.json()['documents']
    # Should only be one document
    self.assertEquals(len(documents), 1)
    doc = documents[0]
    # Make sure we got the right document back with that date.
    self.assertEquals(doc['date_entered'], '2018-12-12')
    self.assertEquals(doc['text4'], 'This is a test of the national broadcasting system')

  def test_search_query_date_equal_by_field(self):
    """
    Specify a field in the query to run a date query against
    """
    response = self.app.post(
      '/python/search/search',
      json={"index": "index-1", "query": "date_entered: 2019-04-04"})

    self.assertEquals(response.status_code, 200)
    self.assertIn('documents', response.json())
    documents = response.json()['documents']
    # Should only be one document
    self.assertEquals(len(documents), 1)
    doc = documents[0]
    # Make sure we got the right document back with that date.
    self.assertEquals(doc['date_entered'], '2019-04-04')
    self.assertEquals(doc['text5'], "Who are the britons?")

  def test_search_query_date_less_than(self):
    """
    Test query less than a certain date, should return 2 documents
    """
    response = self.app.post(
      '/python/search/search',
      json={"index": "index-1", "query": "date_entered < 2019-04-04"})

    self.assertEquals(response.status_code, 200)
    self.assertIn('documents', response.json())
    documents = response.json()['documents']
    # Should only be one document
    self.assertEquals(len(documents), 1)
    doc = documents[0]
    # Make sure we got the right document back with that date.
    self.assertEquals(doc['date_entered'], '2018-12-12')
    self.assertEquals(doc['text4'], 'This is a test of the national broadcasting system')

#
#
def suite(lang, app):
  suite = HawkeyeTestSuite('Search API Test Suite', 'search')
  suite.addTests(PutTest.all_cases(app))
  suite.addTests(GetTest.all_cases(app))
#  suite.addTests(GetRangeTest.all_cases(app))
  suite.addTests(SearchTest.all_cases(app))
  return suite
