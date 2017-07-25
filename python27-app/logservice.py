import json
import logging
import os
import webapp2

from google.appengine.api import logservice
from itertools import islice


class CheckFinishedHandler(webapp2.RequestHandler):
  def get(self):
    request_id = self.request.get('id')
    logs = list(logservice.fetch(request_ids=[request_id]))

    if not logs or not logs[0].finished:
      finished = False
    else:
      finished = True

    json.dump({'finished': finished}, self.response)


class PutHandler(webapp2.RequestHandler):
  def post(self):
    messages = self.request.get_all('message')
    for message in messages:
      logging.info(message)

    json.dump({'request_id': os.environ.get('REQUEST_LOG_ID')}, self.response)


class QueryHandler(webapp2.RequestHandler):
  def get(self):
    count = int(self.request.get('count'))
    logs = logservice.fetch(include_app_logs=True)
    entries = []
    for entry in islice(logs, count):
      entries.append([log.message for log in entry.app_logs])
    json.dump(entries, self.response)


urls = [
  ('/python/logserver/is_finished', CheckFinishedHandler),
  ('/python/logserver/put', PutHandler),
  ('/python/logserver/query', QueryHandler)
]
