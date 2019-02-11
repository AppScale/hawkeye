import json
import datetime
import logging
import wsgiref

import webapp2

from google.appengine.api.search import search
from google.appengine.api.search.search import QueryOptions, ScoredDocument, Query
from google.appengine.api.search.search import FacetRange, FacetOptions, FacetRequest
from google.appengine.ext import webapp


field_type_dict = {'text': search.TextField,
                   'html': search.HtmlField,
                   'atom': search.AtomField,
                   'number': search.NumberField,
                   'date': search.DateField}

facet_type_dict = {'atom': search.AtomFacet,
                   'number': search.NumberFacet}

def get_facet(facet_name):
  return facet_type_dict[facet_name]

def get_field(field_name):
  return field_type_dict[field_name]

def render_doc(document):
  """
  Generates JSON-compatible object from object of type search.Document
  All fields are expected to be TextField for now
  :param document: document to render
  :type document: search.Document
  :return: dict {<field_name>: <string_repr_of_value>}
  """
  if not document:
    return None
  document_dict = {
    field.name: unicode(field.value) for field in document.fields
  }

  # Pull over document id as it isn't included in fields.
  document_dict['id'] = document.doc_id

  if isinstance(document, ScoredDocument):
    document_dict["_sort_scores"] = document.sort_scores
  return document_dict

def render_facet(facet):
  """
  Generates JSON_compatible object from search.Facet
  :param facet:
  :return: dict {
  """
  return {"name": facet.name,
          "values": [(i.label, i.count, i.refinement_token)
                     for i in facet.values]}

def parse_doc(raw_document):
  """
  Builds object of type search.Document from dict
  Only TextFields are supported for now
  :param raw_document: {<field_name>: <text_field_value>}
  :return: search.Document
  """
  fields = []
  facets = []

  # make sure fields exists?
  for f in raw_document.get('fields'):

    field = get_field(f['type'])       # get class by simple name: text,atom
    if f['type'] in ['text','html']:
      # text/html has a lang field, lang should be a two character
      # specifier as required by the sdk.
      fields.append(field(f['name'],
                          f['value'],
                          f['lang'] if 'lang' in f else 'en'))
    elif f['type'] == 'date':
      # for date field we need to convert to a datetime
      fields.append(field(f['name'],
                    datetime.datetime.strptime(f['value'], '%Y-%m-%d')))
    else:
      # All other fields just have a name/value pair.
      fields.append(field(f['name'],
                          f['value']))

  # Construct the document facets
  for fa in raw_document.get('facets', []):
    field = get_facet(fa['type'])
    facets.append(field(fa['name'], fa['value']))

  # Do we need to check if facets are empty?
  return search.Document(
    doc_id=raw_document.get('id'),
    fields=fields,
    facets=facets
  )


class PutDocumentsHandler(webapp2.RequestHandler):

  def post(self):
    payload = json.loads(self.request.body)
    index = payload['index']
    raw_documents = payload['documents']
    documents = [parse_doc(raw_doc) for raw_doc in raw_documents]
    put_results = search.Index(name=index).put(documents)
    response = {'document_ids': [result.id for result in put_results]}
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(json.dumps(response))


class GetDocumentHandler(webapp2.RequestHandler):

  def post(self):
    payload = json.loads(self.request.body)
    index = payload['index']
    doc_id = payload['id']
    document = search.Index(name=index).get(doc_id)
    response = {'document': render_doc(document)}
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(json.dumps(response))


class GetDocumentsRangeHandler(webapp2.RequestHandler):

  def post(self):
    payload = json.loads(self.request.body)
    index = payload['index']
    start_id = payload['start_id']
    limit = payload.get('limit')
    index = search.Index(name=index)
    documents = index.get_range(start_id=start_id, limit=limit)
    response = {'documents': [render_doc(document) for document in documents]}
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(json.dumps(response))


class SearchDocumentsHandler(webapp2.RequestHandler):

  def post(self):
    payload = json.loads(self.request.body)

    # Pull out generic search releated options
    index = payload['index']
    query = payload['query']
    cursor = payload.get('cursor')
    limit = payload.get('limit', 20)

    # Pull out facet related options
    auto_discover_facet_count = payload.get('auto_discover_facet_count')
    facet_byname_refinements = payload.get('facet_simple_requests', [])
    raw_facet_requests = payload.get('facet_requests', [])
    facet_refinements = payload.get('facet_refinements', [])
    facet_auto_detect_limit = payload.get('facet_auto_detect_limit')

    # Construct facet options if auto_discover_facet_count is passed
    #
    facet_options = None
    if auto_discover_facet_count:
      facet_options = FacetOptions(
        discovery_limit=auto_discover_facet_count,
        discovery_value_limit=facet_auto_detect_limit
      )

    # Construct
    facet_requests = []
    for raw_facet_request in raw_facet_requests:
      facet_name = raw_facet_request['name']
      value_limit = raw_facet_request.get('value_limit', 10)

      # Note: it is an error to pass both 'values' and 'ranges'
      # for a FacetRequest()
      values = raw_facet_request.get('values')

      ranges = [
        FacetRange(start=range_.get('start'), end=range_.get('end'))
        for range_ in raw_facet_request.get('ranges', [])
      ] or None

      facet_request = FacetRequest(name=facet_name, value_limit=value_limit,
                                   values=values, ranges=ranges)
      facet_requests.append(facet_request)

    index = search.Index(name=index)
    query_options = QueryOptions(limit=limit, cursor=cursor)

    # Allows by name only requests, overwrites whatever was
    # constructed just above..but they should be mutally exclusive.
    if len(facet_byname_refinements) > 0:
      facet_requests = facet_byname_refinements

    query = Query(
      query,
      options=query_options,
      enable_facet_discovery=bool(auto_discover_facet_count),
      return_facets=facet_requests or None,
      facet_refinements=facet_refinements or None,
      facet_options=facet_options
    )
    result = index.search(query)
    logging.info('\nResults:\n    {}'
                 .format('\n    '.join(repr(doc) for doc in result)))
    logging.info('\nFacets:\n    {}'
                 .format('\n    '.join(repr(facet) for facet in result.facets)))
    response = {'documents': [render_doc(document) for document in result],
                'cursor': result.cursor,
                'facets': [render_facet(facet) for facet in result.facets]}
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(json.dumps(response))


class CleanUpHandler(webapp2.RequestHandler):

  def post(self):
    payload = json.loads(self.request.body)
    document_ids = payload['document_ids']
    index = payload['index']
    idx = search.Index(name=index)

    idx.delete(document_ids)
    idx.delete_schema()

urls = [
  ('/python/search/put', PutDocumentsHandler),
  ('/python/search/get', GetDocumentHandler),
  ('/python/search/get-range', GetDocumentsRangeHandler),
  ('/python/search/search', SearchDocumentsHandler),
  ('/python/search/clean-up', CleanUpHandler),
]
