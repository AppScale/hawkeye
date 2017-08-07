import json

import webapp2

from google.appengine.api import taskqueue
from google.appengine.api.modules import (
  get_current_instance_id, get_current_module_name, get_current_version_name,
  get_default_version, get_modules, get_versions
)
from google.appengine.ext import ndb, deferred


class Entity(ndb.Model):
  created_at_module = ndb.StringProperty(indexed=False)
  created_at_version = ndb.StringProperty(indexed=False)


def render_entity(entity):
  """ Generates dictionary containing information about entity.
  
  Args:
    entity: an instance of Entity or None
  Returns:
    a dict containing values of entity fields or None if entity is None
  """
  if not entity:
    return None
  return {
    'id': entity.key.id(),
    'created_at_module': entity.created_at_module,
    'created_at_version': entity.created_at_version
  }


class GetVersionDetailsHandler(webapp2.RequestHandler):
  """
  Returns information about current version of app
  as it's seen inside from app.
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
  Returns json representation of requested entity.
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
  Returns json representation of requested entities.
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
  Schedules task which will create an entity with specified ID.
  """
  def get(self):
    entity_id = self.request.get('id')
    queue = self.request.params.get('queue')
    target = self.request.params.get('target')

    if target:
      task = taskqueue.Task(
        url='/modules/create-entity',
        target=target,
        method='GET',
        params={'id': entity_id})
    else:
      task = taskqueue.Task(
        url='/modules/create-entity',
        method='GET',
        params={'id': entity_id})

    if queue:
      taskqueue.Queue(queue).add(task)
    else:
      taskqueue.Queue().add(task)


class CreateEntityHandler(webapp2.RequestHandler):
  """
  Creates an entity with specified ID and information
  about module and version where creation was done
  """
  def get(self):
    entity_id = self.request.get('id')
    Entity(id=entity_id, created_at_module='default',
           created_at_version='1').put()


class DeferredCreateEntityHandler(webapp2.RequestHandler):
  """
  Schedules deferred task which will create an entity with specified ID.
  """
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


class CleaningHandler(webapp2.RequestHandler):
  """
  Removes all entities of kind Entity
  """
  @staticmethod
  def get():
    ndb.delete_multi(Entity.query().fetch(keys_only=True))


def deferred_create_entity(entity_id):
  Entity(id=entity_id, created_at_module=get_current_module_name(),
         created_at_version=get_current_version_name()).put()

urls = [
  ('/modules/versions-details', GetVersionDetailsHandler),
  ('/modules/get-entity', GetEntityHandler),
  ('/modules/get-entities', GetEntitiesHandler),
  ('/modules/create-entity', CreateEntityHandler),
  ('/modules/add-task', TaskCreateEntityHandler),
  ('/modules/defer-task', DeferredCreateEntityHandler),
  ('/modules/clean', CleaningHandler),
]
