import json
import datetime

from hawkeye_test_runner import HawkeyeTestCase, HawkeyeTestSuite

default_documents = {"index": "index-1",
                     "documents": [
                       {
                         "id": "a",
                         "fields": [ {"name":"text1",
                                      "type":"text",
                                      "lang":"en",
                                      "value": "hello world"},
                                     {"name":"text2",
                                      "lang":"en",
                                      "value":"testing search api and world",
                                      "type":"text"
                                     },
                         ]
                       },
                       {
                         "id": "b",
                         "fields": [ {"name":"anotherText",
                                      "value":"There is also a corresponding asynchronous method, ",
                                      "type":"text"}
                         ]
                       },
                       {
	                 "id": "c",
                         "fields": [ {"name":"text3",
                                      "value":"This string also contains the word world and api",
                                      "type":"text"},
                         ]
                       },
                       {
                         "id": "firstdate",
                         "fields": [ {"name":"date_entered",
                                      "type":'date',
                                      "value":"2018-12-12"},
                                     {"name":"text4",
                                      "value":"This is a test of the national broadcasting system",
                                      "type":"text"},
                         ]
                       },
                       {
                         "id": "seconddate",
                         "fields": [ {"name": "date_entered",
                                      "value": "2019-04-04",
                                      "type": "date"},
                                     {"name": "text5",
                                      "value": "Who are the britons?",
                                      "type": "text"},
                         ]
                       },
                     ]}

# Documents that will need to be deleted
document_ids = {'index':'index-1',
                'document_ids': [i["id"]
                                 for i in
                                 default_documents['documents']]}

class SearchTestCase(HawkeyeTestCase):

  def tearDown(self):
    self.app.post('/python/search/clean-up',
                  json=document_ids)

class PutTest(SearchTestCase):
  def test_search_put(self):
    response = self.app.post(
      '/python/search/put',
      json=default_documents)
    self.assertEquals(response.status_code, 200)

class GetTest(SearchTestCase):
  def setUp(self):
    self.app.post('/python/search/put',
                  json=default_documents)
  
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
  def setUp(self):
    self.app.post('/python/search/put',
                  json=default_documents)

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

    # Documents 'a' and 'c' should be in the results as they
    # both have 'api, world' in the content
    ids = [doc['id'] for doc in documents]
    self.assertIn('a', ids)
    self.assertIn('c', ids)

  def test_search_query_OR(self):
    response = self.app.post(
      '/python/search/search',
      json={"index": "index-1", "query": "hello OR britons"})

    self.assertEquals(response.status_code, 200)
    self.assertIn('documents', response.json())
    documents = response.json()['documents']
    self.assertEquals(len(documents), 2)

    ids = [doc['id'] for doc in documents]
    self.assertIn('a', ids)
    self.assertIn('seconddate', ids)

  def test_search_query_date_global_equal(self):
    """
    Generic date entry in the query string
    """
    response = self.app.post(
      '/python/search/search',
      json={"index": "index-1", "query": "2018"})

    self.assertEquals(response.status_code, 200)
    self.assertIn('documents', response.json())
    documents = response.json()['documents']
    # Should only be one document
    self.assertEquals(len(documents), 1)
    doc = documents[0]
    # Make sure we got the right document back with that date.
    self.assertEquals(doc['date_entered'],"2018-12-12T00:00:00")
    self.assertEquals(doc['text4'], 'This is a test of the national broadcasting system')

  def test_search_query_date_equal_by_field(self):
    """
    Specify a field in the query to run a date query against
    """
    response = self.app.post(
      '/python/search/search',
      json={"index": "index-1", "query": "date_entered: 2019"})

    self.assertEquals(response.status_code, 200)
    self.assertIn('documents', response.json())
    documents = response.json()['documents']
    # Should only be one document
    self.assertEquals(len(documents), 1)
    doc = documents[0]
    # Make sure we got the right document back with that date.
    self.assertEquals(doc['date_entered'], '2019-04-04T00:00:00')
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
