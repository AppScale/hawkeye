import json

import webapp2
from google.appengine.ext import ndb
from google.appengine.api.modules import (
  get_current_instance_id, get_current_module_name, get_current_version_name,
  get_default_version, get_modules, get_versions
)


class Entity(ndb.Model):
  """
  module-a has extended version of Entity model
  """
  created_at_module = ndb.StringProperty(indexed=False)
  created_at_version = ndb.StringProperty(indexed=False)
  new_field = ndb.StringProperty(indexed=False)


def render_entity(entity):
  if not entity:
    return None
  return {
    'id': entity.key.id(),
    'created_at_module': entity.created_at_module,
    'created_at_version': entity.created_at_version,
    'new_field': entity.new_field
  }


class GetVersionDetailsHandler(webapp2.RequestHandler):
  """
  This handler is imported in all modules and versions.
  When it's invoked on different version and modules it should
  return different responses
  """
  def get(self):
    self.response.headers['Content-Type'] = 'application/json'
    current_module = get_current_module_name()
    self.response.out.write(json.dumps({
      'modules': get_modules(),
      'current_module_versions': get_versions(current_module),
      'default_version': get_default_version(current_module),
      'current_module': current_module,
      'current_version': get_current_version_name(),
      'current_instance_id': get_current_instance_id()
    }))


class GetEntityHandler(webapp2.RequestHandler):
  """
  This handler is implemented here and in module_a.py
  (there Entity class has new field, so handler is also updated to include it).
  This implementation is also imported in modules_a_previous.py
  """
  def get(self):
    entity_id = self.request.get('id')
    entity = Entity.get_by_id(entity_id)
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(json.dumps({
      'entity': render_entity(entity)
    }))


class GetEntitiesHandler(webapp2.RequestHandler):
  """
  This handler is implemented here and in module_a.py
  (there Entity class has new field, so handler is also updated to include it).
  This implementation is also imported in modules_a_previous.py
  """
  def get(self):
    entity_ids = self.request.get_all('id')
    entities = ndb.get_multi([ndb.Key(Entity, id_) for id_ in entity_ids])
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(json.dumps({
      'entities': [render_entity(entity) for entity in entities]
    }))


class CreateEntityHandler(webapp2.RequestHandler):
  """
  For testing purposes it's also expected to be invoked using task queue.
  """
  def get(self):
    entity_id = self.request.get('id')
    Entity(id=entity_id, created_at_module='module-a',
           created_at_version='1', new_field='new').put()


# The second version of separate module 'a'
app = webapp2.WSGIApplication([
  ('/modules/versions-details', GetVersionDetailsHandler),
  ('/modules/get-entity', GetEntityHandler),
  ('/modules/get-entities', GetEntitiesHandler),
  ('/modules/create-entity', CreateEntityHandler),
])


# This import helps to run deferred task using service-a
import module_main
