import time

from hawkeye_test_runner import HawkeyeTestCase, HawkeyeTestSuite

# GAE uses eventual consistency for SearchAPI
CONSISTENCY_WAIT_TIME = 0.5

default_documents = {
  "index": "index-1",
  "documents": [
    {
      "id": "a",
      "fields": [{"name": "text1",
                  "type": "text",
                  "lang": "en",
                  "value": "hello world"},
                 {"name": "text2",
                  "lang": "en",
                  "value": "testing search api and world",
                  "type": "text"}]
    },
    {
      "id": "b",
      "fields": [{"name": "anotherText",
                  "value": "There is also a corresponding asynchronous method, ",
                  "type": "text"}]
    },
    {
      "id": "c",
      "fields": [{"name": "text3",
                  "value": "This string also contains the word world and api",
                  "type": "text"}]
    },
    {
      "id": "firstdate",
      "fields": [{"name": "date_entered",
                  "type": "date",
                  "value": "2018-12-12"},
                 {"name": "text4",
                  "value": "This is a test of the national broadcasting system",
                  "type": "text"}]
    },
    {
      "id": "seconddate",
      "fields": [{"name": "date_entered",
                  "value": "2019-04-04",
                  "type": "date"},
                 {"name": "text5",
                  "value": "Who are the britons?",
                  "type": "text"}]
    },
    {
      "id": "importantnumbers",
      "fields": [{"name": "meaning_of_life",
                  "value": 42,
                  "type": "number"},
                 {"name": "holyhandgrenadecount",
                  "value": 3,
                  "type": "number"}]
    },
    {
      "id": "numbers",
      "fields": [{"name": "meeting_timeout",
                  "value": 15,
                  "type": "number"},
                 {"name": "fiveisrightout",
                  "value": 5,
                  "type": "number"},
                 {"name": "hourly_rate",
                  "value": 4,
                  "type": "number"}]
    },
    {
      "id": "numbers2",
      "fields": [{"name": "meeting_timeout",
                  "value": 35,
                  "type": "number"},
                 {"name": "hourly_rate",
                  "value": 2,
                  "type": "number"}]
    },
    {
      "id": "multivalue",
      "fields": [{"name": "mfield",
                  "value": "stringfield1",
                  "type": "text"},
                 {"name": "mfield",
                  "value": "stringfield2",
                  "type": "text"},
                 {"name": "mfield",
                  "value": 22,
                  "type": "number"}]
    }
  ]
}

# Documents that will need to be deleted from the index
document_ids = {"index": "index-1",
                "document_ids": [i["id"]
                                 for i in
                                 default_documents["documents"]]}


class SearchTestCase(HawkeyeTestCase):

  def tearDown(self):
    """
    Tear down of the test will remove all documents from the index
    and clear the index_schema
    """
    self.app.post("/python/search/clean-up", json=document_ids)


class PutTest(SearchTestCase):

  def test_search_put(self):
    response = self.app.post("/python/search/put", json=default_documents)
    self.assertEquals(response.status_code, 200)

    # Account for 'eventual consistency' of the SearchAPI
    # by allowing time for the document to propagate through
    # the system
    time.sleep(CONSISTENCY_WAIT_TIME)


class GetTest(SearchTestCase):

  def setUp(self):
    self.app.post("/python/search/put", json=default_documents)
    time.sleep(CONSISTENCY_WAIT_TIME)

  def test_search_get(self):
    response = self.app.post(
      "/python/search/get",
      json={"index": "index-1", "id": "a"}
    )
    self.assertEquals(response.status_code, 200)

    doc = response.json()["document"]
    self.assertEquals("a", doc["id"])
    self.assertIn("text1", doc)
    self.assertIn("text2", doc)


class GetRangeTest(SearchTestCase):

  def setUp(self):
    self.app.post("/python/search/put", json=default_documents)
    time.sleep(CONSISTENCY_WAIT_TIME)

  def test_get_range_three_documents_from_a(self):
    """
    Range request starting at the first document "a".
    Should get "a" "b" "c"
    Note: It isn't clear what "first" implies in GAE...
          It looks as though 'first' implies the
          first document id in *sorted* order.
    """
    response = self.app.post(
      "/python/search/get-range",
      json={"index": "index-1", "start_id": "a", "limit": 3}
    )
    self.assertEquals(response.status_code, 200)

    documents = response.json()["documents"]
    self.assertEquals(len(documents), 3)

    ids = [doc["id"] for doc in documents]
    self.assertIn("a", ids)
    self.assertIn("b", ids)
    self.assertIn("c", ids)

  def test_get_range_three_documents_from_c(self):
    """
    Range request starting at the first document "c".
    Should get "c" "firstdate" "importantnumbers"
    """
    response = self.app.post(
      "/python/search/get-range",
      json={"index": "index-1", "start_id": "c", "limit": 3}
    )
    self.assertEquals(response.status_code, 200)

    documents = response.json()["documents"]
    self.assertEquals(len(documents), 3)

    ids = [doc["id"] for doc in documents]
    self.assertIn("c", ids)
    self.assertIn("firstdate", ids)
    self.assertIn("importantnumbers", ids)

  def test_get_range_all_documents(self):
    """
    Range request, set limit to 100, should get all documents back
    """
    response = self.app.post(
      "/python/search/get-range",
      json={"index": "index-1", "start_id": "a", "limit": 100}
    )
    self.assertEquals(response.status_code, 200)

    documents = response.json()["documents"]
    self.assertEquals(len(documents), len(default_documents["documents"]))


class SearchTest(SearchTestCase):

  def setUp(self):
    self.app.post("/python/search/put", json=default_documents)
    time.sleep(CONSISTENCY_WAIT_TIME)

  def test_search_simple_query(self):
    """
    Test a simple global query with one keyword
    """
    response = self.app.post(
      "/python/search/search",
      json={"index": "index-1", "query": "hello"}
    )
    self.assertEquals(response.status_code, 200)
    response_json = response.json()
    self.assertIn("documents", response_json)
    documents = response_json["documents"]
    self.assertEqual(len(documents), 1)
    self.assertIn("text1",documents[0])
    self.assertIn("text2",documents[0])

  def test_search_query_AND_no_results(self):
    """
    Query using AND that should result in no documents
    """
    response = self.app.post(
      "/python/search/search",
      json={"index": "index-1", "query": "hello AND corresponding"}
    )

    self.assertEquals(response.status_code, 200)
    self.assertIn("documents", response.json())
    self.assertEquals(len(response.json()["documents"]), 0)

  def test_search_query_AND_two_results(self):
    """
    Query using AND that should result in multiple documents
    """
    response = self.app.post(
        "/python/search/search",
        json={"index": "index-1", "query": "world AND api"}
    )

    self.assertEquals(response.status_code, 200)
    self.assertIn("documents", response.json())
    documents = response.json()["documents"]
    self.assertEquals(len(documents), 2)

    # Documents "a" and "c" should be in the results as they
    # both have "api, world" in the content
    ids = [doc["id"] for doc in documents]
    self.assertIn("a", ids)
    self.assertIn("c", ids)

  def test_search_query_implicit_AND_two_results(self):
    """
    Implicit AND query that should result in multiple documents
    """
    response = self.app.post(
      "/python/search/search",
      json={"index": "index-1", "query": "world api"}
    )

    self.assertEquals(response.status_code, 200)
    self.assertIn("documents", response.json())
    documents = response.json()["documents"]
    self.assertEquals(len(documents), 2)

    # Documents "a" and "c" should be in the results as they
    # both have "api, world" in the content
    ids = [doc["id"] for doc in documents]
    self.assertIn("a", ids)
    self.assertIn("c", ids)
    
  def test_search_query_OR(self):
    """
    OR query that should result in 2 documents
    """
    response = self.app.post(
      "/python/search/search",
      json={"index": "index-1", "query": "hello OR britons"}
    )

    self.assertEquals(response.status_code, 200)
    self.assertIn("documents", response.json())
    documents = response.json()["documents"]
    self.assertEquals(len(documents), 2)

    ids = [doc["id"] for doc in documents]
    self.assertIn("a", ids)
    self.assertIn("seconddate", ids)

  def test_search_query_date_global_equal(self):
    """
    Date query without field name
    """
    response = self.app.post(
      "/python/search/search",
      json={"index": "index-1", "query": "2018-12-12"}
    )

    self.assertEquals(response.status_code, 200)
    self.assertIn("documents", response.json())
    documents = response.json()["documents"]
    # Should only be one document
    self.assertEquals(len(documents), 1)
    doc = documents[0]
    # Make sure we got the right document back with that date.
    self.assertEquals(doc["date_entered"], "2018-12-12 00:00:00")
    self.assertEquals(doc["text4"], "This is a test of the national broadcasting system")

  def test_search_query_date_equal_by_field(self):
    """
    Date query by field name
    """
    response = self.app.post(
      "/python/search/search",
      json={"index": "index-1", "query": "date_entered: 2019-04-04"}
    )
    self.assertEquals(response.status_code, 200)
    self.assertIn("documents", response.json())

    documents = response.json()["documents"]
    self.assertEquals(len(documents), 1)

    doc = documents[0]
    self.assertEquals(doc["date_entered"], "2019-04-04 00:00:00")
    self.assertEquals(doc["text5"], "Who are the britons?")

  def test_search_query_date_less_than(self):
    """
    Date less than query
    """
    response = self.app.post(
      "/python/search/search",
      json={"index": "index-1", "query": "date_entered < 2019-04-04"}
    )
    self.assertEquals(response.status_code, 200)
    self.assertIn("documents", response.json())

    documents = response.json()["documents"]
    self.assertEquals(len(documents), 1)

    doc = documents[0]
    self.assertEquals(doc["date_entered"], "2018-12-12 00:00:00")
    self.assertEquals(doc["text4"], "This is a test of the national broadcasting system")

  def test_search_query_number_by_field_equal(self):
    """
    Number query where number is equal, specified by '='
    """
    response = self.app.post(
      "/python/search/search",
      json={"index": "index-1", "query": "meaning_of_life = 42"}
    )
    self.assertEquals(response.status_code, 200)
    self.assertIn("documents", response.json())

    documents = response.json()["documents"]
    self.assertEquals(len(documents), 1)

    doc = documents[0]
    self.assertEquals(doc["id"], "importantnumbers")
    self.assertEquals(doc["meaning_of_life"], u'42.0')

  def test_search_query_number_by_field_equal_colon(self):
    """
    Number query where number is equal, specified by colon
    """
    response = self.app.post(
      "/python/search/search",
      json={"index": "index-1", "query": "meaning_of_life: 42"}
    )
    self.assertEquals(response.status_code, 200)
    self.assertIn("documents", response.json())

    documents = response.json()["documents"]
    self.assertEquals(len(documents), 1)

    doc = documents[0]
    self.assertEquals(doc["id"], "importantnumbers")
    self.assertEquals(doc["meaning_of_life"], u'42.0')

  def test_search_query_number_less_than(self):
    """
    Number query for meaning_of_life less than 50
    """
    response = self.app.post(
      "/python/search/search",
      json={"index": "index-1", "query": "meaning_of_life < 50"}
    )
    self.assertEquals(response.status_code, 200)
    self.assertIn("documents", response.json())

    documents = response.json()["documents"]
    self.assertEquals(len(documents), 1)

    doc = documents[0]
    self.assertEquals(doc["id"], "importantnumbers")
    self.assertEquals(doc["meaning_of_life"], u'42.0')

  def test_search_query_number_less_than_no_results(self):
    """
    Number query for meaning_of_life less than 42 (no docs)
    """
    response = self.app.post(
      "/python/search/search",
      json={"index": "index-1", "query": "meaning_of_life < 42"}
    )
    self.assertEquals(response.status_code, 200)
    self.assertIn("documents", response.json())

    documents = response.json()["documents"]
    self.assertEquals(len(documents), 0)

  def test_search_query_number_less_than_equal(self):
    """
    Number query for hourly_rate <= 4
    """
    response = self.app.post(
      "/python/search/search",
      json={"index": "index-1", "query": "hourly_rate <=4"}
    )
    self.assertEquals(response.status_code, 200)
    self.assertIn("documents", response.json())

    documents = response.json()["documents"]
    self.assertEquals(len(documents), 2)

    docs = [i["id"] for i in documents]
    self.assertIn("numbers", docs)
    self.assertIn("numbers2", docs)

  def test_search_query_number_greater_than_equal_equality(self):
    """
    Number query for hourly_rate >= 4, 4 being an exact equality match
    """
    response = self.app.post(
      "/python/search/search",
      json={"index": "index-1", "query": "hourly_rate >= 4"}
    )
    self.assertEquals(response.status_code, 200)
    self.assertIn("documents", response.json())

    documents = response.json()["documents"]
    self.assertEquals(len(documents), 1)

    docs = [i["id"] for i in documents]
    self.assertIn("numbers", docs)

  def test_search_query_number_greater_than_equal_one(self):
    """
    Number query for hourly_rate >= 3 - should return 1 doc
    """
    response = self.app.post(
      "/python/search/search",
      json={"index": "index-1", "query": "hourly_rate >= 3"}
    )
    self.assertEquals(response.status_code, 200)
    self.assertIn("documents", response.json())

    documents = response.json()["documents"]
    self.assertEquals(len(documents), 1)

    docs = [i["id"] for i in documents]
    self.assertIn("numbers", docs)

  def test_search_query_number_greater_than_equal_two(self):
    """
    Number query for hourly_rate >= 2 - should return 2 docs
    """
    response = self.app.post(
      "/python/search/search",
      json={"index": "index-1", "query": "hourly_rate >= 2"}
    )
    self.assertEquals(response.status_code, 200)
    self.assertIn("documents", response.json())

    documents = response.json()["documents"]
    self.assertEquals(len(documents), 2)

    docs = [i["id"] for i in documents]
    self.assertIn("numbers", docs)
    self.assertIn("numbers2", docs)

  def test_search_query_multivalue_fields_first_value(self):
    """
    Multivalue field test match on first value
    """
    response = self.app.post(
      "/python/search/search",
      json={"index": "index-1", "query": "mfield: stringfield1"}
    )
    self.assertEquals(response.status_code, 200)
    self.assertIn("documents", response.json())

    documents = response.json()["documents"]
    self.assertEquals(len(documents), 1)

    doc = documents[0]
    self.assertEquals("multivalue", doc["id"])

  def test_search_query_multivalue_fields_second_value(self):
    """
    Multivalue field test match on second value
    """
    response = self.app.post(
      "/python/search/search",
      json={"index": "index-1", "query": "mfield: stringfield2"}
    )
    self.assertEquals(response.status_code, 200)
    self.assertIn("documents", response.json())

    documents = response.json()["documents"]
    self.assertEquals(len(documents), 1)

    doc = documents[0]
    self.assertEquals("multivalue", doc["id"])

  def test_search_query_multivalue_fields_third_value(self):
    """
    Multivalue field test match on third value, different type
    """
    response = self.app.post(
      "/python/search/search",
      json={"index": "index-1", "query": "mfield: 22"}
    )
    self.assertEquals(response.status_code, 200)
    self.assertIn("documents", response.json())

    documents = response.json()["documents"]
    self.assertEquals(len(documents), 1)

    doc = documents[0]
    self.assertEquals("multivalue", doc["id"])

  def test_search_query_multivalue_fields_string_no_results(self):
    """
    Multivalue field test no match on string
    """
    response = self.app.post(
      "/python/search/search",
      json={"index": "index-1", "query": "mfield: notfound"}
    )
    self.assertEquals(response.status_code, 200)
    self.assertIn("documents", response.json())

    documents = response.json()["documents"]
    self.assertEquals(len(documents), 0)

  def test_search_query_multivalue_fields_number_no_results(self):
    """
    Multivalue field test no match on number
    """
    response = self.app.post(
      "/python/search/search",
      json={"index": "index-1", "query": "mfield: 10000"}
    )
    self.assertEquals(response.status_code, 200)
    self.assertIn("documents", response.json())

    documents = response.json()["documents"]
    self.assertEquals(len(documents), 0)


def suite(lang, app):
  suite = HawkeyeTestSuite("Search API Test Suite", "search")
  suite.addTests(PutTest.all_cases(app))
  suite.addTests(GetTest.all_cases(app))
  suite.addTests(GetRangeTest.all_cases(app))
  suite.addTests(SearchTest.all_cases(app))
  return suite
