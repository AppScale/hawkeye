import json
import logging
import webapp2

from google.appengine.api import logservice
from itertools import islice


class LogServiceHandler(webapp2.RequestHandler):
  def get(self):
    count = int(self.request.get('count'))
    logs = logservice.fetch(include_app_logs=True)
    entries = []
    for entry in islice(logs, count):
      entries.append([log.message for log in entry.app_logs])
    json.dump(entries, self.response)

  def post(self):
    messages = self.request.get_all('message')
    for message in messages:
      logging.info(message)


urls = [
  ('/python/logserver', LogServiceHandler)
]
