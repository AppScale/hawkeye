import uuid
import wsgiref
from google.appengine.api import images

try:
  import json
except ImportError:
  import simplejson as json

from google.appengine.ext import db, webapp
import webapp2

__author__ = 'hiranya'

class ProjectLogo(db.Model):
  project_id = db.StringProperty(required=True)
  picture = db.BlobProperty()

class ProjectLogoHandler(webapp2.RequestHandler):
  def get(self):
    project_id = self.request.get('project_id')
    metadata = self.request.get('metadata')
    resize = self.request.get('resize')
    rotate = self.request.get('rotate')
    transform = self.request.get('transform')
    query = db.GqlQuery("SELECT * FROM ProjectLogo WHERE "
                        "project_id = '%s'" % project_id)
    logo = query[0]
    if metadata is not None and metadata == 'true':
      if transform is not None and transform == 'true':
        logo_image = images.Image(logo.picture)
        if resize is not None and len(resize) > 0:
          logo_image.resize(width=int(resize))
        if rotate is not None and rotate == 'true':
          logo_image.rotate(90)
        logo_image.execute_transforms()
      else:
        self.response.headers['Content-Type'] = 'application/json'
        if resize is not None and len(resize) > 0:
          logo.picture = images.resize(logo.picture, width=int(resize))
        if rotate is not None and rotate == 'true':
          logo.picture = images.rotate(logo.picture, 90)
        logo_image = images.Image(logo.picture)

      image_data = {
        'height' : logo_image.height,
        'width' : logo_image.width,
        'format' : logo_image.format
      }
      self.response.out.write(json.dumps(image_data))
    else:
      self.response.headers['Content-Type'] = 'image/png'
      self.response.out.write(str(logo.picture))

  def post(self):
    project_id = str(uuid.uuid1())
    picture = images.resize(self.request.get('file'), 100)
    logo = ProjectLogo(project_id=project_id, picture=picture)
    logo.put()
    self.response.headers['Content-Type'] = 'application/json'
    self.response.set_status(201)
    self.response.out.write(
      json.dumps({ 'success' : True, 'project_id' : project_id }))

  def delete(self):
    db.delete(ProjectLogo.all())

urls = [
  ('/python/images/logo', ProjectLogoHandler),
]
