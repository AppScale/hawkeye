import wsgiref
from google.appengine.api import users
from google.appengine.ext import webapp

try:
  import json
except ImportError:
  import simplejson as json
import webapp2

__author__ = 'hiranya'

class AuthorizedAccessHandler(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps({ 'user' : user.nickname(), 'email' : user.email() }))

application = webapp.WSGIApplication([
  ('/python/users/secure', AuthorizedAccessHandler),
], debug=True)

if __name__ == '__main__':
  wsgiref.handlers.CGIHandler().run(application)