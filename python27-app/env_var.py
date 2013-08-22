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

__author__ = 'chris'

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

application = webapp.WSGIApplication([
  ('/python/env_var', GetConfigEnvironmentVariableHandler),
], debug=True)

if __name__ == '__main__':
  wsgiref.handlers.CGIHandler().run(application)
