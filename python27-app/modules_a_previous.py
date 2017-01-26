import webapp2

from modules_main import GetVersionDetailsHandler, GetEntityHandler, Entity


class CreateEntityHandler(webapp2.RequestHandler):
  """
  For testing purposes it's also expected to be invoked using task queue.
  """
  def post(self):
    entity_id = self.request.POST.get("id")
    Entity(id=entity_id, module="module-a", version="v1").put()


# The first version of separate module "a"
app = webapp2.WSGIApplication([
  ('/python/modules/version-details', GetVersionDetailsHandler),
  ('/python/modules/get-entity', GetEntityHandler),
  ('/python/modules/create-entity', CreateEntityHandler),
])