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
  new_field = ndb.StringProperty(indexed=False)


def render_entity(entity):
  if not entity:
    return None
  return {
    'id': entity.key.id(),
    'module': entity.module,
    'version': entity.version,
    'new_field': entity.new_field
  }


class GetEntityHandler(webapp2.RequestHandler):
  """
  This handler is implemented here and in modules_a_current.py
  (there Entity class has new field, so handler is also updated to include it).
  This implementation is also imported in modules_a_previous.py
  """
  def get(self):
    entity_id = self.request.get("id")
    entity = Entity.get_by_id(entity_id)
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps({
      'entity': render_entity(entity)
    }))


class GetEntitiesHandler(webapp2.RequestHandler):
  """
  This handler is implemented here and in modules_a_current.py
  (there Entity class has new field, so handler is also updated to include it).
  This implementation is also imported in modules_a_previous.py
  """
  def get(self):
    entity_ids = self.request.get_all("id")
    entities = ndb.get_multi([ndb.Key(Entity, id_) for id_ in entity_ids])
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps({
      'entities': [render_entity(entity) for entity in entities]
    }))


class CreateEntityHandler(webapp2.RequestHandler):
  """
  For testing purposes it's also expected to be invoked using task queue.
  """
  def get(self):
    entity_id = self.request.get("id")
    Entity(id=entity_id, module="module-a",
           version="v2", new_field="new").put()


# The second version of separate module "a"
app = webapp2.WSGIApplication([
  ('/python/modules/versions-details', GetVersionDetailsHandler),
  ('/python/modules/get-entity', GetEntityHandler),
  ('/python/modules/get-entities', GetEntitiesHandler),
  ('/python/modules/create-entity', CreateEntityHandler),
])