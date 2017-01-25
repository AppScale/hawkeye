import wsgiref
from google.appengine.ext import webapp
import webapp2

try:
  import json
except ImportError:
  import simplejson as json

__author__ = 'hiranya'

class AlwaysSecureHandler(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps({ 'success' : True }))

class NeverSecureHandler(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps({ 'success' : True }))


urls = [
  ('/python/secure/always', AlwaysSecureHandler),
  ('/python/secure/never', NeverSecureHandler),
  ('/python/secure/always/regex1/regex2', AlwaysSecureHandler),
  ('/python/secure/never/regex1/regex2', NeverSecureHandler),
]
