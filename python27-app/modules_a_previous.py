import webapp2

from modules_main import (
  Entity, GetEntitiesHandler, GetEntityHandler, GetVersionDetailsHandler
)


class CreateEntityHandler(webapp2.RequestHandler):
  """
  For testing purposes it's also expected to be invoked using task queue.
  """
  def get(self):
    entity_id = self.request.get('id')
    Entity(id=entity_id, module='module-a', version='v1').put()


# The first version of separate module "a"
app = webapp2.WSGIApplication([
  ('/modules/versions-details', GetVersionDetailsHandler),
  ('/modules/get-entity', GetEntityHandler),
  ('/modules/get-entities', GetEntitiesHandler),
  ('/modules/create-entity', CreateEntityHandler),
])