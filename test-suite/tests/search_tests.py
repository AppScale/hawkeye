import time
import itertools
from collections import Counter

from hawkeye_test_runner import HawkeyeTestCase, HawkeyeTestSuite

# GAE uses eventual consistency for SearchAPI
CONSISTENCY_WAIT_TIME = 0.5

field_lookup = ["id", "title", "author", "price"]
facet_lookup = ["type", "format", "publisher", "rating"]

# List of (fields, facets) tuples
# fields: id, title, author, price
# facets: type, format, publisher, rating
faceted_docs = [
  (("1", "IT", "Stephen King", 9.99), ("horror", "paperback", "viking press", 5)),
  (("2", "IT", "Stephen King", 9.99), ("horror", "digital", "viking press", 5)),
  (("3", "Ready Player One", "Ernest Cline", 19.99), ("science-fiction", "hardcover", "crown publishers", 4)),
  (("4", "Swan Song", "Robert McCammon", 5.99), ("horror", "paperback", "simon and schuster", 3)),
  (("5", "Swan Song", "Robert McCammon", 29.99), ("horror", "hardcover", "simon and schuster", 3)),
  (("6", "Leviathan Wakes", "James S.A Corey", 11.99), ("science-fiction", "digital", "orbit books", 1)),
  (("7", "The Terror", "Dan Simmons", 12.99), ("fiction", "paperback", "little, brown and company", 2)),
  (("8", "The Last Stand of the Tin Can Soldiers", "James D. Hornfischer", 13.99), ("non-fiction", "paperback", "bantam", 1)),
  (("9", "Wizard and Glass", "Stephen King", 19.99), ("science-fiction", "hardcover", "viking press", 5)),
  (("10", "East of Eden", "John Steinbeck", 5.99), ("fiction", "paperback", "viking press", 5)),
  (("11", "American Ulysses", "Ronald C. White", 14.99), ("non-fiction", "hardcover", "random house", 4))
]

# Index constants to avoid magic numbers in the test cases.
FIELDS = 0
FACETS = 1

FIELD_ID = 0
FIELD_TITLE = 1
FIELD_AUTHOR = 2
FIELD_PRICE = 3
FACET_TYPE = 0
FACET_FORMAT = 1
FACET_PUB = 2
FACET_RATING = 3

# Index of facet result values: (value, count, refinement_token)
FACET_RES_VALUE = 0
FACET_RES_COUNT = 1
FACET_RES_TOKEN = 2


def construct_faceted_dict(index_name, docs_info):
  """ Constructs a document dictionary with facets similar to 'default_documents' below
  but does so in a way that makes it easier to add books for faceted test cases
  :param index_name: name of index to add documents to
  :param docs_info: list of docs which contain a field, facet tuple
  :return: dict with an index field and document field
  """
  documents = []

  # loop through docs and construct a dictionary
  # that will get passed to the application
  for field_values, facet_values in docs_info:
    fields = []
    facets = []

    # build the fields
    for index, field_value in enumerate(field_values):
      # Skip the "id" used only for the document
      if index == FIELD_ID:
        continue
      fields.append({
        "name": field_lookup[index],
        "type": "text" if isinstance(field_value, str) else "number",
        "value": field_value
      })

    # build the facets
    for index, facet_value in enumerate(facet_values):
      facets.append({
        "name": facet_lookup[index],
        "type": "atom" if isinstance(facet_value, str) else "number",
        "value": facet_value
      })

    # Attach the doc
    doc = {"id": field_values[FIELD_ID], "fields": fields, "facets": facets}
    documents.append(doc)
  return {"index": index_name, "documents": documents}


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


class SearchTestCase(HawkeyeTestCase):
  # Documents that will need to be deleted from the index
  document_ids = {"index": "index-1",
                  "document_ids": [doc["id"] for doc
                                   in default_documents["documents"]]}

  def tearDown(self):
    """
    Tear down of the test will remove all documents from the index
    and clear the index_schema
    """
    self.app.post("/python/search/clean-up", json=self.document_ids)


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
    self.assertIn("text1", documents[0])
    self.assertIn("text2", documents[0])

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
    self.assertEquals(doc["text4"],
                      "This is a test of the national broadcasting system")

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
    self.assertEquals(doc["text4"],
                      "This is a test of the national broadcasting system")

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
    self.assertEquals(doc["meaning_of_life"], 42.0)

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
    self.assertEquals(doc["meaning_of_life"], 42.0)

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
    self.assertEquals(doc["meaning_of_life"], 42.0)

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

    docs = [doc["id"] for doc in documents]
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

    docs = [doc["id"] for doc in documents]
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

    docs = [doc["id"] for doc in documents]
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

    docs = [doc["id"] for doc in documents]
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


class FacetedSearch(SearchTestCase):
  # Faceted documents, these belong to the 'books' index.
  faceted_doc_ids = {"index": "books",
                     "document_ids": [doc_info[FIELDS][FIELD_ID] for doc_info
                                      in faceted_docs]}

  # Gather some stats on the list of books as a whole.
  facet_stats = {}
  for facet_name in facet_lookup:
    facet_stats[facet_name] = Counter()

  facet_lists = [doc_info[FACETS] for doc_info in faceted_docs]
  for facet_list in facet_lists:
    for index, facet_value in enumerate(facet_list):
      facet_stats[facet_lookup[index]][facet_value] += 1

  def setUp(self):
    self.app.post("/python/search/put",
                  json=construct_faceted_dict("books", faceted_docs))
    time.sleep(CONSISTENCY_WAIT_TIME)

  def tearDown(self):
    """
    Remove faceted documents
    """
    self.app.post("/python/search/clean-up", json=self.faceted_doc_ids)

  def test_automatic_facet_discovery_all_documents(self):
    """
    This query will return all of the documents
    """
    response = self.app.post(
      "/python/search/search",
      json={"index": "books",
            "query": "price > 5",
            "auto_discover_facet_count": 5,
            }
    )
    self.assertEquals(response.status_code, 200)
    self.assertIn("documents", response.json())
    self.assertIn("facets", response.json())

    documents = response.json()["documents"]

    # Should get back all documents
    self.assertEquals(len(documents), len(faceted_docs))

    facets = response.json()["facets"]
    # List of facets should match the length of our lookup list
    self.assertEquals(len(facets), len(facet_lookup))

    #
    # Verify the facet values and counts.
    #
    # When verifying we construct a string of the name,value, and count
    # to make it easier to see what facet is causing the assertion:
    # type-science_fiction-5
    # format-paperback-3
    #
    for facet in facets:
      facet_name = facet["name"]

      # Number facet values come back in a range, which makes life difficult.
      if facet_name == 'rating':
        # We know the rating scale is 1-5 so the value returned for all
        # documents should be: [1.0, 5.0)-10. 10 being the # of facets (docs)
        v = facet["values"][0]  # only one value to get...
        expected = "[1.0,5.0)-{}".format(len(faceted_docs))
        actual = "{}-{}".format(v[FACET_RES_VALUE], v[FACET_RES_COUNT])
        self.assertEquals(actual, expected)
        continue

      self.assertIn(facet_name, facet_lookup)
      self.assertIn(facet_name, self.facet_stats)

      # Iterate through the values for the facets
      # they should match the stats we gathered from faceted_docs.
      values = facet["values"]
      for value in values:
        label, count, _ = value  # tuple of (label, count, facet_refinement)
        actual = (facet_name, label, count)

        expected_count = self.facet_stats[facet_name][label]
        expected = (facet_name, label, expected_count)
        self.assertEquals(actual, expected)

  def test_automatic_facet_discovery_priced_above_15(self):
    """
    This query will return approximately 3 results
    Note: The checks on the results aren't currently dynamic.
          If you add a book that is > 15 the facets will change.
    """
    response = self.app.post(
      "/python/search/search",
      json={"index": "books",
            "query": "price > 15",
            "auto_discover_facet_count": 5,
            }
    )
    self.assertEquals(response.status_code, 200)
    self.assertIn("documents", response.json())
    self.assertIn("facets", response.json())

    documents = response.json()["documents"]

    # Should get back all documents
    self.assertEquals(len(documents), 3)

    document_titles = [doc["title"] for doc in documents]
    document_titles.sort()

    # should be: Ready Player One, Swan Song, Wizard and Glass
    expected_titles = [unicode(doc_info[FIELDS][FIELD_TITLE])
                       for doc_info in faceted_docs
                       if doc_info[FIELDS][FIELD_PRICE] > 15]
    expected_titles.sort()

    self.assertEquals(document_titles, expected_titles)

    facets = response.json()["facets"]
    self.assertEquals(len(facets), len(facet_lookup))

    # Should be a count of 3 for format: hardcover
    # Should be a count of 2 for type: science-fiction
    #                      1 for type: horror
    # Should be 3 publishers
    # 'crown publishers', 'simon and schuster', 'viking press'

    #
    # TODO These assertion checks should be dynamic.
    #
    for facet in facets:
      if facet["name"] == "format":
        values = facet["values"][0]
        self.assertEquals(values[FACET_RES_VALUE], 'hardcover')
        self.assertEquals(values[FACET_RES_COUNT], 3)
      elif facet["name"] == "type":
        values = facet["values"]
        for value in values:
          if value[FACET_RES_VALUE] == 'science-fiction':
            self.assertEquals(value[FACET_RES_COUNT], 2)
          elif value[0] == 'horror':
            self.assertEquals(value[FACET_RES_COUNT], 1)
      elif facet["name"] == "publisher":
        self.assertEquals(len(facet["values"]), 3)

  def test_automatic_facet_refine_by_paperback_from_all_documents(self):
    """
    This query will return all of the results, and supply facet refinements
    that we'll use to refine the query down by paperback.

    This test is dynamic in that it finds the number of paperback books
    and verifies the titles from the faceted_docs global list.
    """
    response = self.app.post(
      "/python/search/search",
      json={"index": "books",
            "query": "price > 5",
            "auto_discover_facet_count": 5,
            }
    )
    self.assertEquals(response.status_code, 200)
    self.assertIn("documents", response.json())
    self.assertIn("facets", response.json())

    facets = response.json()["facets"]

    # Facet names should match the length of our lookup list
    self.assertEquals(len(facets), len(facet_lookup))

    # refine by format:paperback
    formats = [facet for facet in facets if facet["name"] == "format"]
    self.assertEquals(len(formats), 1)

    book_format = formats.pop()

    # Gather the list of refinement tokens to pass to the query
    refinements = [
      facet_tuple[FACET_RES_TOKEN]
      for facet_tuple in book_format['values']
      if facet_tuple[FACET_RES_VALUE] in ['paperback']
    ]
    self.assertEquals(len(refinements), 1)

    # Run the search again, with refinements.
    second_response = self.app.post(
      "/python/search/search",
      json={"index": "books",
            "query": "price > 5",
            "facet_refinements": refinements
            }
    )
    self.assertEquals(second_response.status_code, 200)
    self.assertIn("documents", response.json())
    self.assertIn("facets", response.json())

    second_documents = second_response.json()["documents"]
    actual_titles = [doc["title"] for doc in second_documents]
    actual_titles.sort()

    expected_titles = [unicode(doc_info[FIELDS][FIELD_TITLE])
                       for doc_info in faceted_docs
                       if doc_info[FACETS][FACET_FORMAT] == "paperback"]
    expected_titles.sort()

    self.assertEqual(actual_titles, expected_titles)

  def test_automatic_facet_refine_by_paperback_or_digital_from_all_documents(self):
    """
    This query will return all of the results, and supply facet refinements
    that we'll use to refine the query down by paperback or digital.

    This is testing the OR of similar facets.

    This test is dynamic in that it finds the number of paperback
    and digital books from the faceted_docs global list.
    """
    response = self.app.post(
      "/python/search/search",
      json={"index": "books",
            "query": "price > 5",
            "auto_discover_facet_count": 5,
            }
    )
    self.assertEquals(response.status_code, 200)
    self.assertIn("documents", response.json())
    self.assertIn("facets", response.json())

    facets = response.json()["facets"]

    # Facet names should match the length of our lookup list
    self.assertEquals(len(facets), len(facet_lookup))

    # refine by format:paperback
    formats = [facet for facet in facets if facet["name"] == "format"]
    self.assertEquals(len(formats), 1)
    book_format = formats.pop()

    refinements = [
      facet_tuple[FACET_RES_TOKEN]
      for facet_tuple in book_format['values']
      if facet_tuple[FACET_RES_VALUE] in ['paperback', 'digital']
    ]
    self.assertEquals(len(refinements), 2)

    second_response = self.app.post(
      "/python/search/search",
      json={"index": "books",
            "query": "price > 5",
            "facet_refinements": refinements
            }
    )
    self.assertEquals(second_response.status_code, 200)
    self.assertIn("documents", response.json())
    self.assertIn("facets", response.json())

    second_documents = second_response.json()["documents"]
    actual_titles = [doc["title"] for doc in second_documents]
    actual_titles.sort()

    # paperback and digital
    expected_titles = [
      unicode(doc_info[FIELDS][FIELD_TITLE])
      for doc_info in faceted_docs
      if doc_info[FACETS][FACET_FORMAT] in ["paperback", "digital"]
    ]
    expected_titles.sort()

    self.assertEqual(actual_titles, expected_titles)

  def test_automatic_facet_refine_by_paperback_or_digital_and_non_fiction_from_all_documents(self):
    """
    This query will return all of the results, and supply facet refinements
    that we'll use to refine the query down.

    This is testing the OR of similar facets, and the AND
    of a different facet using 'type' and 'format'.

    This test is dynamic in that it finds the number of paperback,digital books
    and for type: non-fiction and verifies the titles from the global
    faceted_docs list. Currently there should only be one book that matches.
    """
    response = self.app.post(
      "/python/search/search",
      json={"index": "books",
            "query": "price > 5",
            "auto_discover_facet_count": 5,
            }
    )
    self.assertEquals(response.status_code, 200)
    self.assertIn("documents", response.json())
    self.assertIn("facets", response.json())

    facets = response.json()["facets"]

    # Facet names should match the length of our lookup list
    self.assertEquals(len(facets), len(facet_lookup))

    #
    # refine by format:paperback, format: digital
    #
    formats = [facet for facet in facets if facet["name"] == "format"]
    book_format = formats.pop()

    format_refinements = [
      facet_tuple[FACET_RES_TOKEN]
      for facet_tuple in book_format['values']
      if facet_tuple[FACET_RES_VALUE] in ['paperback', 'digital']
    ]

    #
    # Get the 'non-fiction' refinement token
    #
    book_type = [facet for facet in facets if facet["name"] == "type"]
    book_type = book_type.pop()

    type_refinements = [
      facet_tuple[FACET_RES_TOKEN]
      for facet_tuple in book_type['values']
      if facet_tuple[FACET_RES_VALUE] in ['non-fiction']
    ]

    # combine the refinement token lists
    refinements = list(itertools.chain(format_refinements,
                                       type_refinements))
    second_response = self.app.post(
      "/python/search/search",
      json={"index": "books",
            "query": "price > 5",
            "facet_refinements": refinements
            }
    )
    self.assertEquals(second_response.status_code, 200)
    self.assertIn("documents", response.json())
    self.assertIn("facets", response.json())

    second_documents = second_response.json()["documents"]
    actual_titles = [doc["title"] for doc in second_documents]
    actual_titles.sort()

    # paperback or digital and 'non-fiction' titles.
    expected_titles = [
      unicode(doc_info[FIELDS][FIELD_TITLE])
      for doc_info in faceted_docs
      if doc_info[FACETS][FACET_FORMAT] in ["paperback", "digital"]
      and doc_info[FACETS][FACET_TYPE] in ['non-fiction']
    ]
    expected_titles.sort()

    self.assertEqual(actual_titles, expected_titles)

  def test_select_facet_by_name_all_documents(self):
    """
    Perform a query and request specific facets by name: 'type'

    Verify that the facet is returned and values/counts match
    what we calculated in facet_stats.
    """
    response = self.app.post(
      "/python/search/search",
      json={"index": "books",
            "query": "price > 5",
            "facet_simple_requests": ["type"]
            }
    )
    self.assertEquals(response.status_code, 200)
    self.assertIn("documents", response.json())
    self.assertIn("facets", response.json())

    facets = response.json()["facets"]

    # We've only asked for one facet
    self.assertEqual(len(facets), 1)

    # no longer a list
    facet = facets.pop()
    actual_values = [facet_tuple[FACET_RES_VALUE]
                     for facet_tuple in facet["values"]]
    actual_values.sort()

    expected_values = [unicode(value) for value
                       in self.facet_stats['type'].keys()]
    expected_values.sort()

    self.assertEqual(actual_values, expected_values)

    #
    # Compare strings of 'value'-'count' to make it easier to see
    # incorrect facets.
    #
    value_counts = [
      (facet_tuple[FACET_RES_VALUE], facet_tuple[FACET_RES_COUNT])
      for facet_tuple in facet["values"]
    ]
    for value, count in value_counts:
      actual = "{}-{}".format(value, count)
      expected = "{}-{}".format(value, self.facet_stats["type"][value])
      self.assertEqual(actual, expected)

  def test_select_facet_by_name_value_all_documents(self):
    """
    Perform a query and request specific facets and values
    facet: type
    value: horror

    Should only return one facet, and one facet value.
    The count should match our facet_stats.
    """
    response = self.app.post(
      "/python/search/search",
      json={"index": "books",
            "query": "price > 5",
            "facet_requests": [{"name": "type",
                               "values": ["horror"]}
                               ]
            }
    )
    self.assertEquals(response.status_code, 200)
    self.assertIn("documents", response.json())
    self.assertIn("facets", response.json())

    facets = response.json()["facets"]

    # We've only asked for one facet
    self.assertEqual(len(facets), 1)

    # Verify the returned values, should match what we
    # asked for: type:horror
    facet = facets.pop()
    self.assertEqual(facet["name"], "type")

    actual_values = [facet_tuple[FACET_RES_VALUE]
                     for facet_tuple in facet["values"]]
    actual_values.sort()

    # expected is hard coded since we asked for type:horror
    expected_values = [u'horror']

    self.assertEqual(actual_values, expected_values)

    # verify the count matches
    self.assertEqual(facet["values"][0][FACET_RES_COUNT],
                     self.facet_stats['type']['horror'])

  def test_select_facet_rating_by_name_all_documents(self):
    """
    Perform a query and request specific number facet

    Since our rating scale is 1-5 we know the range will be: [1.0, 5.0)

    facet: rating
    value: a range [1.0, 5.0) and count: # of books in list
    """
    response = self.app.post(
      "/python/search/search",
      json={"index": "books",
            "query": "price > 5",
            "facet_simple_requests": ["rating"]
            }
    )
    self.assertEquals(response.status_code, 200)
    self.assertIn("documents", response.json())
    self.assertIn("facets", response.json())

    facets = response.json()["facets"]

    # We've only asked for one facet
    self.assertEqual(len(facets), 1)

    facet = facets.pop()
    actual_value = "{}-{}".format(facet["values"][0][FACET_RES_VALUE],
                                  facet["values"][0][FACET_RES_COUNT])

    expected_value = u"[1.0,5.0)-{}".format(len(faceted_docs))
    self.assertEqual(actual_value, expected_value)

  def test_select_facet_rating_by_range_all_documents(self):
    """
    Perform a query and request specific facet by range

    pass a facet request for the 'rating' facet starting at 4 ending at 6
    """
    response = self.app.post(
      "/python/search/search",
      json={"index": "books",
            "query": "price > 5",
            "facet_requests": [{"name": "rating",
                                "ranges": [{"start": 4, "end": 6}]}
                               ]
            }
    )
    self.assertEquals(response.status_code, 200)
    self.assertIn("documents", response.json())
    self.assertIn("facets", response.json())

    facets = response.json()["facets"]

    # We've only asked for one facet
    self.assertEqual(len(facets), 1)

    facet = facets.pop()

    # This should match the expected title count below
    facet_rating_document_count = facet["values"][0][FACET_RES_COUNT]

    refinements = [facet["values"][0][FACET_RES_TOKEN]]

    # Make the second query with refinements.
    second_response = self.app.post(
      "/python/search/search",
      json={"index": "books",
            "query": "price > 5",
            "facet_refinements": refinements
            }
    )
    self.assertEquals(second_response.status_code, 200)
    self.assertIn("documents", response.json())
    self.assertIn("facets", response.json())

    second_documents = second_response.json()["documents"]
    actual_titles = [doc["title"] for doc in second_documents]
    actual_titles.sort()

    expected_titles = [
      unicode(doc_info[FIELDS][FIELD_TITLE])
      for doc_info in faceted_docs
      if float(4) <= float(doc_info[FACETS][FACET_RATING]) < float(6)
    ]
    expected_titles.sort()

    # Verify the document titles
    self.assertEqual(actual_titles, expected_titles)

    # Verify the number of documents returned in the facet request
    self.assertEqual(facet_rating_document_count, len(expected_titles))

  def test_facet_options_all_documents(self):
    """
    Set the discover_facet_limit and value limit to 1 and make sure
    that results are limited to 1 each.
    """
    response = self.app.post(
      "/python/search/search",
      json={"index": "books",
            "query": "price > 5",
            "auto_discover_facet_count": 1,
            "facet_auto_detect_limit": 1
            }
    )
    self.assertEquals(response.status_code, 200)
    self.assertIn("documents", response.json())
    self.assertIn("facets", response.json())

    facets = response.json()["facets"]

    # We've only asked for one facet
    self.assertEqual(len(facets), 1)

    facet = facets.pop()

    self.assertIn(facet["name"], facet_lookup)

    self.assertEqual(len(facet["values"]), 1)

    # Find the facet value column in faceted_docs.
    # assertion above would have fired if the name wasn't in the lookup
    # so we don't need to try/except here.
    idx = facet_lookup.index(facet["name"])

    facet_value = facet["values"][0][FACET_RES_VALUE]

    # all possible values for the facet
    expected_values = {doc_info[FACETS][idx] for doc_info in faceted_docs}

    # Check that the facet value is correct
    self.assertIn(facet_value, expected_values)
    # TODO: this test fails, but it's not critical at the moment.


def suite(lang, app):
  test_suite = HawkeyeTestSuite("Search API Test Suite", "search")
  if lang != 'python':
    return test_suite

  test_suite.addTests(PutTest.all_cases(app))
  test_suite.addTests(GetTest.all_cases(app))
  test_suite.addTests(GetRangeTest.all_cases(app))
  test_suite.addTests(SearchTest.all_cases(app))
  test_suite.addTests(FacetedSearch.all_cases(app))
  return test_suite
