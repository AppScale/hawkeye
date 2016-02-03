import time

from google.appengine.ext import db

__author__ = 'hiranya'

class TaskCounter(db.Model):
  count = db.IntegerProperty(indexed=False)

def process(key):
  counter = TaskCounter.get_by_key_name(key)
  if counter is None:
    counter = TaskCounter(key_name=key, count=1)
  else:
    counter.count += 1
  counter.put()

def processEta(key, eta):
  actual = time.time()
  difference = float(actual) - float(eta)
  if difference < 0:
    difference = difference * -1
  success = 1
  #allow a buffer of 2 seconds
  if difference > 2:
    success = 0
  counter = TaskCounter(key_name=key, count=success)
  counter.put()

def format_errors(result):
  output = ''
  if len(result.errors) > 0:
    output += 'Errors:\n'
    for error in result.errors:
      if type(error) is tuple:
        for error_line in error:
          output += str(error_line).rstrip() + '\n'
      else:
        output += str(error)

  if len(result.failures) > 0:
    output += 'Failures:\n'
    for failure in result.failures:
      if type(failure) is tuple:
        for failure_line in failure:
          output += str(failure_line).rstrip() + '\n'
      else:
        output += str(failure)

  return output
