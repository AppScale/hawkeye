import json
import time
import webapp2

from google.appengine.ext import ndb


SDK_CONSISTENCY_WAIT = .5

WARMUP_KEY = ndb.Key('WarmUpStatus', 'warmup-key')


class WarmUpStatus(ndb.Model):
  success = ndb.BooleanProperty()


class WarmUpHandler(webapp2.RequestHandler):
  """WarmUp handles the warmup request. It sets a value in the datastore so
  that we can check later that it was run.
  """

  def get(self):
      WarmUpStatus(success=True, key=WARMUP_KEY).put()
      # Return a successful response to indicate the logic completed.
      self.response.headers['Content-Type'] = 'text/plain'
      self.response.write('Warmup successful.')


class WarmUpTestHandler(webapp2.RequestHandler):
  """WarmupCheck checks whether the warmup was run by checking the datastore
  value that is set during warmup.
  """
  def get(self):
    success = WARMUP_KEY.get() is not None

    WARMUP_KEY.delete()
    time.sleep(SDK_CONSISTENCY_WAIT)
    json.dump({'success': success}, self.response)

# These are all all URL available for the module warmup
app = webapp2.WSGIApplication([
  ('/_ah/warmup', WarmUpHandler),
  ('/warmup_status', WarmUpTestHandler),
])
