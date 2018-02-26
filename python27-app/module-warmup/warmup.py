import json
import time
import webapp2

from google.appengine.ext import ndb


SDK_CONSISTENCY_WAIT = .5


class WarmUpStatus(ndb.Model):
  success = ndb.BooleanProperty()


class WarmUpHandler(webapp2.RequestHandler):
  """WarmUp handles the warmup request. It sets a value in the datastore so
  that we can check later that it was run.
  """

  def get(self):
      WarmUpStatus(success=True).put()
      # Return a successful response to indicate the logic completed.
      self.response.headers['Content-Type'] = 'text/plain'
      self.response.write('Warmup successful.')


class WarmUpTestHandler(webapp2.RequestHandler):
  """WarmupCheck checks whether the warmup was run by checking the datastore
  value that is set during warmup.
  """
  def get(self):
    query = WarmUpStatus.query()
    success = all(status.success for status in query)

    keys = WarmUpStatus.query().fetch(keys_only=True)
    ndb.delete_multi(keys)
    time.sleep(SDK_CONSISTENCY_WAIT)
    json.dump({'success': success}, self.response)

# These are all all URL available for the module warmup
app = webapp2.WSGIApplication([
  ('/_ah/warmup', WarmUpHandler),
  ('/warmup_status', WarmUpTestHandler),
])
