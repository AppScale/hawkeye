from google.appengine.ext import db
import logging
import time, datetime

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

def process(key, eta):
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
