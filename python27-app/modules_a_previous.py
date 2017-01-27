import webapp2

from modules_main import (
  Entity, GetEntitiesHandler, GetEntityHandler, GetVersionDetailsHandler
)


class CreateEntityHandler(webapp2.RequestHandler):
  """
  For testing purposes it's also expected to be invoked using task queue.
  """
  def get(self):
    entity_id = self.request.get("id")
    Entity(id=entity_id, module="module-a", version="v1").put()


# The first version of separate module "a"
app = webapp2.WSGIApplication([
  ('/python/modules/versions-details', GetVersionDetailsHandler),
  ('/python/modules/get-entity', GetEntityHandler),
  ('/python/modules/get-entities', GetEntitiesHandler),
  ('/python/modules/create-entity', CreateEntityHandler),
])