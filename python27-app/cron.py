try:
  import json
except ImportError:
  import simplejson as json

from google.appengine.ext import webapp, db
import uuid
import webapp2
import wsgiref
import datetime
import logging
import time

class CronObj(db.Model):
  last_update = db.DateTimeProperty()

class CronHandler(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = "application/json"
    query = self.request.get('query')
    if query is None or query == '':
      # This request is coming from crontab, update timestamp 
      cron_obj = CronObj(key_name='cron_key')
      cron_obj.last_update = datetime.datetime.now()
      cron_obj.put()
    else:
      # Hawkeye is querying value
      cron_key = db.Key.from_path('CronObj', 'cron_key')
      cron_obj = db.get(cron_key)
      if cron_obj is None:
        self.response.set_status(404)
      else:
        if self.is_valid_timestamp(cron_obj.last_update):
          self.response.set_status(200)  
        else:
          self.response.set_status(404)
     

  def is_valid_timestamp(self, last_update):
    time_now = datetime.datetime.now()
    time_delta = time_now - last_update
    seconds = time_delta.seconds
    if seconds > 61:
      return False        
    else:
      return True
 

application = webapp.WSGIApplication([
  ('/python/cron', CronHandler),
], debug=True)

if __name__ == '__main__':
  wsgiref.handlers.CGIHandler().run(application)
