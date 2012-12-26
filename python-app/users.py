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
    self.response.out.write(json.dumps(
        { 'user' : user.nickname(), 'email' : user.email() }))

class LoginURLHandler(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    self.response.headers['Content-Type'] = "application/json"
    if user:
      info = {
        'type' : 'logout',
        'url' : users.create_login_url("/python/users/")
      }

    else:
      info = {
        'type' : 'login',
        'url' : users.create_logout_url("/python/users/")
      }
    self.response.out.write(json.dumps(info))

application = webapp.WSGIApplication([
  ('/python/users/secure', AuthorizedAccessHandler),
  ('/python/users/home', LoginURLHandler),
], debug=True)

if __name__ == '__main__':
  wsgiref.handlers.CGIHandler().run(application)