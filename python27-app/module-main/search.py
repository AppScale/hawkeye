import json
import wsgiref

import webapp2

from google.appengine.api.search import search
from google.appengine.api.search.search import QueryOptions, ScoredDocument, Query
from google.appengine.ext import webapp


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
  if isinstance(document, ScoredDocument):
    document_dict["_sort_scores"] = document.sort_scores
  return document_dict


def parse_doc(raw_document):
  """
  Builds object of type search.Document from dict
  Only TextFields are supported for now
  :param raw_document: {<field_name>: <text_field_value>}
  :return: search.Document
  """
  return search.Document(
    doc_id=raw_document.get('id'),
    fields=[
      search.TextField(name, value)
      for name, value in raw_document.iteritems() if name != 'id'
    ])



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
    index = payload['index']
    query = payload['query']
    cursor = payload.get('cursor')
    limit = payload.get('limit', 20)
    index = search.Index(name=index)
    query_options = QueryOptions(limit=limit, cursor=cursor)
    result = index.search(Query(query, options=query_options))
    response = {'documents': [render_doc(document) for document in result],
                'cursor': result.cursor}
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(json.dumps(response))


class CleanUpHandler(webapp2.RequestHandler):

  def post(self):
    indexes = search.get_indexes()
    for index in indexes:
      doc_ids = index.get_range(ids_only=True)
      index.delete(doc_ids)


application = webapp.WSGIApplication([
  ('/python/search/put', PutDocumentsHandler),
  ('/python/search/get', GetDocumentHandler),
  ('/python/search/get-range', GetDocumentsRangeHandler),
  ('/python/search/search', SearchDocumentsHandler),
  ('/python/search/clean-up', CleanUpHandler),
], debug=True)

if __name__ == '__main__':
  wsgiref.handlers.CGIHandler().run(application)
