try:
  import json
except ImportError:
  import simplejson as json

from google.appengine.api import logservice
from google.appengine.api.logservice import InvalidArgumentError
from google.appengine.ext import webapp
import webapp2
import wsgiref
import logging


class LogServiceHandler(webapp2.RequestHandler):

  def get(self):
    logging.info("LogServiceHandler called")
    dump = {}
    log_message1 = "log message 1"
    logservice.write(log_message1)
    log_message2 = "log message 2"
    logservice.write(log_message2)
    dump['logs'] = [log_message1, log_message2]
    self.response.headers['Content-Type'] = "application/json"
    try:
      fetched_logs = logservice.fetch()
      dump['fetched_logs'] = fetched_logs
      if len(fetched_logs) != 2:
        dump['fetched'] = "incorrect count of fetched logs"
        logging.info(json.dumps(dump))
        self.response.set_status(404)
      else:
        request_ids = []
        start_times = []
        end_times = []
        offsets = []
        version_ids = []
        for log in fetched_logs:
          start_times.append(log.start_time)
          end_times.append(log.end_time)
          offsets.append(log.offset)
          version_ids.append(log.version_id)
          request_ids.append(log.request_id)

      fetched_logs = logservice.fetch(request_ids=request_ids)
      if len(fetched_logs) != 2:
        dump['fetched_by_req_id'] = "incorrect count"
        logging.info(json.dumps(dump))
        self.response.set_status(404)
      else:
        got_all_req_ids = True
        for log in fetched_logs:
          if log.request_id not in request_ids:
            got_all_req_ids = False
        if not got_all_req_ids:
          dump['got_all_req_ids'] = False
          logging.info(json.dumps(dump))
          self.response.set_status(404)
        else:
         self.response.set_status(200)

    except InvalidArgumentError:
      logging.info(json.dumps(dump))
      self.response.set_status(404)
    except NameError:
      logging.info(json.dumps(dump))
      self.response.set_status(404)

application = webapp.WSGIApplication([
  ('/python/logserver', LogServiceHandler),
], debug=True)

if __name__ == '__main__':
  wsgiref.handlers.CGIHandler().run(application)
