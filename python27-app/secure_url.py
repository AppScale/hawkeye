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


application = webapp.WSGIApplication([
  ('/python/secure/always', AlwaysSecureHandler),
  ('/python/secure/never', NeverSecureHandler),
], debug=True)

if __name__ == '__main__':
  wsgiref.handlers.CGIHandler().run(application)