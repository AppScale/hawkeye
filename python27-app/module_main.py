import json

import webapp2

from google.appengine.api import taskqueue
from google.appengine.api.modules import (
  get_current_instance_id, get_current_module_name, get_current_version_name,
  get_default_version, get_modules, get_versions
)
from google.appengine.ext import ndb, deferred


class Entity(ndb.Model):
  module = ndb.StringProperty(indexed=False)
  version = ndb.StringProperty(indexed=False)


def render_entity(entity):
  if not entity:
    return None
  return {
    'id': entity.key.id(),
    'module': entity.module,
    'version': entity.version
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


class TaskCreateEntityHandler(webapp2.RequestHandler):
  """
  Adds entity creation task to default queue with specified (or missed) target.
  Depending on target, different module and version will be used,
  so different implementation if create_entity will be used and different
  entities will be created
  """
  def get(self):
    entity_id = self.request.get('id')
    queue = self.request.params.get('queue')
    target = self.request.params.get('target')
    task = taskqueue.Task(
      url='/modules/create-entity',
      target=target,
      method='GET',
      params={'id': entity_id})
    if queue:
      taskqueue.Queue(queue).add(task)
    else:
      taskqueue.Queue().add(task)


class CreateEntityHandler(webapp2.RequestHandler):
  """
  For testing purposes it's also expected to be invoked using task queue.
  """
  def get(self):
    entity_id = self.request.get('id')
    Entity(id=entity_id, module='default', version='main-v1').put()


class DeferredCreateEntityHandler(webapp2.RequestHandler):
  def get(self):
    entity_id = self.request.params.get('id')
    queue_name = self.request.params.get('queue')
    target = self.request.params.get('target')
    if queue_name:
      deferred.defer(deferred_create_entity, entity_id=entity_id,
                     _queue=queue_name, _target=target)
    else:
      deferred.defer(deferred_create_entity, entity_id=entity_id,
                     _target=target)


def deferred_create_entity(entity_id):
  Entity(id=entity_id, module=get_current_module_name(),
         version=get_current_version_name()).put()


class CleanUpHandler(webapp2.RequestHandler):
  def get(self):
    ndb.delete_multi(Entity.query().fetch(keys_only=True))


# URLs to be added to the main App (see main.py)
urls = [
  ('/modules/versions-details', GetVersionDetailsHandler),
  ('/modules/get-entity', GetEntityHandler),
  ('/modules/get-entities', GetEntitiesHandler),
  ('/modules/create-entity', CreateEntityHandler),
  ('/modules/add-task', TaskCreateEntityHandler),
  ('/modules/defer-task', DeferredCreateEntityHandler),
  ('/modules/clean-up', CleanUpHandler),
]
