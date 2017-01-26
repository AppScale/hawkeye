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


class GetVersionDetailsHandler(webapp2.RequestHandler):
  """
  This handler is imported in all modules and versions.
  When it's invoked on different version and modules it should
  return different responses
  """
  def get(self):
    self.response.headers['Content-Type'] = "application/json"
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
  This handler is implemented here and in modules_a_current.py
  (there Entity class has new field, so handler is also updated to include it).
  This implementation is also imported in modules_a_previous.py
  """
  def get(self):
    entity_id = self.request.GET.get("id")
    entity = Entity.get_by_id(entity_id)
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps({
      'module': entity.module,
      'version': entity.version
    }))


class TaskCreateEntityHandler(webapp2.RequestHandler):
  """
  Adds entity creation task to default queue with specified (or missed) target.
  Depending on target, different module and version will be used,
  so different implementation if create_entity will be used and different
  entities will be created
  """
  def post(self):
    entity_id = self.request.POST.get("id")
    module = self.request.POST.get("module")
    version = self.request.POST.get("version")
    if module:
      if version:
        target = "{}.{}".format(version, module)
      else:
        target = module
    else:
      target = None
    taskqueue.add(
        url='/python/modules/create-entity',
        target=target,
        params={'entity_id': entity_id})


class CreateEntityHandler(webapp2.RequestHandler):
  """
  For testing purposes it's also expected to be invoked using task queue.
  """
  def post(self):
    entity_id = self.request.POST.get("id")
    Entity(id=entity_id, module="default", version="1").put()


class CleanUpHandler(webapp2.RequestHandler):
  def delete(self):
    ndb.delete_multi(Entity.query().fetch(keys_only=True))


# URLs to be added to the main App (see app.yaml)
urls = [
  ('/python/modules/versions-details', GetVersionDetailsHandler),
  ('/python/modules/get-entity', GetEntityHandler),
  ('/python/modules/create-entity', CreateEntityHandler),
  ('/python/modules/clean-up', CleanUpHandler),
]