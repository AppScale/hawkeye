import os
import wsgiref
from google.appengine.ext import webapp
import webapp2

# Test import of pycrypto library.
import Crypto
from Crypto import Random

try:
  import json
except ImportError:
  import simplejson as json

class GetConfigEnvironmentVariableHandler(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = "application/json"

    if 'SHOULD_BE_BAZ' in os.environ:
      result = {
        "success" : True,
        "value" : os.environ['SHOULD_BE_BAZ']
      }
    else:
      result = {
        "success" : False,
        "value" : None
      }

    self.response.out.write(json.dumps(result))

class MirrorHandler(webapp2.RequestHandler):
  def repulse(self):
    response_dict = {
      'method': self.request.method,
      'scheme': self.request.scheme,
      'uri': self.request.uri
    }
    self.response.headers['Content-Type'] = 'application/json'
    self.response.write(json.dumps(response_dict))

  def get(self):
    self.repulse()

  def put(self):
    self.repulse()

  def post(self):
    self.repulse()

  def delete(self):
    self.repulse()

application = webapp.WSGIApplication([
  ('/python/env/var', GetConfigEnvironmentVariableHandler),
  ('/python/env/mirror', MirrorHandler),
], debug=True)

if __name__ == '__main__':
  wsgiref.handlers.CGIHandler().run(application)
