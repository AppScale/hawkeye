from google.appengine.api.modules import (
  get_current_module_name, get_current_version_name
)

from module_a import Entity

def deferred_create_entity(entity_id):
  Entity(id=entity_id, created_at_module=get_current_module_name(),
         created_at_version=get_current_version_name()).put()
