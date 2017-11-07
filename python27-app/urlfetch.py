import base64
import webapp2

from google.appengine.api import urlfetch


class FetchURL(webapp2.RequestHandler):
  def get(self):
    encoded_url = str(self.request.get('url'))
    url = base64.urlsafe_b64decode(encoded_url)
    validate = self.request.get('validate').lower() == 'true'
    urlfetch.fetch(url, validate_certificate=validate)


urls = [('/python/urlfetch', FetchURL)]
