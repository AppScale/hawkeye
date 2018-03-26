import os
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
    env_vars = {key: os.environ[key] for key in os.environ
                if isinstance(os.environ[key], basestring)}

    json.dump(env_vars, self.response)

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

urls = [
  ('/python/env/var', GetConfigEnvironmentVariableHandler),
  ('/python/env/mirror', MirrorHandler),
]
