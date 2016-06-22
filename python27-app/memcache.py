try:
  import json
except ImportError:
  import simplejson as json

from google.appengine.api import memcache
from google.appengine.ext import webapp
import webapp2
import wsgiref
import logging
import uuid
__author__ = 'hiranya'

class MemcacheHandler(webapp2.RequestHandler):

  def get(self):
    key = self.request.get('key')
    value = memcache.get(key)
    self.response.headers['Content-Type'] = "application/json"
    if value is not None:
      self.response.out.write(json.dumps({ 'value' : value }))
    else:
      self.response.set_status(404)

  def post(self):
    key = self.request.get('key')
    value = self.request.get('value')
    update = self.request.get('update')
    timeout = self.request.get('timeout')
    if timeout is None or len(timeout) == 0:
      timeout = 3600
    self.response.headers['Content-Type'] = "application/json"
    if update is not None and update == 'true':
      response = memcache.set(key, value, int(timeout))
    else:
      response = memcache.add(key, value, int(timeout))

    if response:
      self.response.out.write(json.dumps({ 'success' : True }))
    else:
      self.response.out.write(json.dumps({ 'success' : False }))

  def delete(self):
    key = self.request.get('key')
    self.response.headers['Content-Type'] = "application/json"
    if memcache.delete(key):
      self.response.out.write(json.dumps({ 'success' : True }))
    else:
      self.response.out.write(json.dumps({ 'success' : False }))

class MemcacheIncrHandler(webapp2.RequestHandler):

  def post(self):
    key = self.request.get('key')
    delta = self.request.get('delta')
    initval = self.request.get('initial')
    postincrval = -1000
    if not initval:
      initval = 0
    if long(delta) > 0:
      postincrval = memcache.incr(key, long(delta), None, long(initval))
    else:
      postincrval = memcache.decr(key, -long(delta), None, long(initval))
    self.response.headers['Content-Type'] = "application/json"
    self.response.set_status(200)
    self.response.out.write(
      json.dumps({ 'success' : True, 'value' : postincrval }))

  def get(self):
    key = self.request.get('key')
    value = self.request.get('value')
    response = memcache.set(key, long(value), 3600)
    self.response.headers['Content-Type'] = "application/json"
    if response:
      self.response.out.write(json.dumps({ 'success' : True }))
    else:
      self.response.out.write(json.dumps({ 'success' : False }))

class MemcacheMultiKeyHandler(webapp2.RequestHandler):

  def get(self):
    keys = self.request.get('keys')
    values = memcache.get_multi(keys.split(','))
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps(values))

  def post(self):
    keys = self.request.get('keys')
    values = self.request.get('values')
    update = self.request.get('update')
    timeout = self.request.get('timeout')
    if timeout is None or len(timeout) == 0:
      timeout = 3600
    self.response.headers['Content-Type'] = "application/json"
    mapping = dict(zip(keys.split(','), values.split(',')))

    if update is not None and update == 'true':
      response = memcache.set_multi(mapping, int(timeout))
    else:
      response = memcache.add_multi(mapping, int(timeout))

    if not response:
      self.response.out.write(json.dumps({ 'success' : True }))
    else:
      self.response.out.write(
        json.dumps({ 'success' : False, 'failed_keys' : response }))

  def delete(self):
    keys = self.request.get('keys')
    self.response.headers['Content-Type'] = "application/json"
    if memcache.delete_multi(keys.split(',')):
      self.response.out.write(json.dumps({ 'success' : True }))
    else:
      self.response.out.write(json.dumps({ 'success' : False }))

class MemcacheCasHandler(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = "application/json"
    key = str(uuid.uuid1())
    timeout = 36000
    client = memcache.Client()
    
    memcache.set(key, 1, int(timeout))
    gets_val = client.gets(key)
    if client.cas(key, 2) == False:
      self.response.out.write(json.dumps({ 'success' : False , 'error':\
       'cas returned False, should have returned True'}))
    
    else:
      gets_val = client.gets(key)
      memcache.set(key, 1, int(timeout))
      if client.cas(key, 2):
        self.response.out.write(json.dumps({ 'success' : False, 'error':\
          'cas returned True, should have returned False'}))
      else:
        self.response.out.write(json.dumps({ 'success' : True}))
    

application = webapp.WSGIApplication([
  ('/python/memcache', MemcacheHandler),
  ('/python/memcache/multi', MemcacheMultiKeyHandler),
  ('/python/memcache/incr', MemcacheIncrHandler),
  ('/python/memcache/cas', MemcacheCasHandler),
], debug=True)

if __name__ == '__main__':
  wsgiref.handlers.CGIHandler().run(application)
