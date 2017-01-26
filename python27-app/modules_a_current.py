import json

import webapp2

from google.appengine.ext import ndb
from modules_main import GetVersionDetailsHandler


class Entity(ndb.Model):
  """
  New version of module-a has extended version of Entity model
  """
  module = ndb.StringProperty(indexed=False)
  version = ndb.StringProperty(indexed=False)
  new_field = ndb.StringProperty(default="new", indexed=False)


class GetEntityHandler(webapp2.RequestHandler):
  """
  New version of module-a has extended version of Entity model
  and /get-entity handler returns entity with new field
  """
  def get(self):
    entity_id = self.request.GET.get("id")
    entity = Entity.get_by_id(entity_id)
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps({
      'module': entity.module,
      'version': entity.version,
      'new_field': entity.new_field,
    }))


class CreateEntityHandler(webapp2.RequestHandler):
  """
  For testing purposes it's also expected to be invoked using task queue.
  """
  def post(self):
    entity_id = self.request.POST.get("id")
    Entity(id=entity_id, module="module-a", version="v2").put()


# The second version of separate module "a"
app = webapp2.WSGIApplication([
  ('/python/modules/version-details', GetVersionDetailsHandler),
  ('/python/modules/get-entity', GetEntityHandler),
  ('/python/modules/create-entity', CreateEntityHandler),
])