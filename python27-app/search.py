import webapp2
import wsgiref

from google.appengine.ext import webapp
from google.appengine.api.search import search

try:
  import json
except ImportError:
  import simplejson as json


class GetDocumentHandler(webapp2.RequestHandler):

  def post(self):
    payload = json.loads(self.request.body)
    index = payload['index']
    doc_id = payload['id']
    result = search.Index(name=index).get(doc_id)
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps({'result': [str(item) for item in result]}))


application = webapp.WSGIApplication([
  ('/python/search/get-doc', GetDocumentHandler),
], debug=True)

if __name__ == '__main__':
  wsgiref.handlers.CGIHandler().run(application)
