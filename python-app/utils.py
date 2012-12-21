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