import urllib
import wsgiref
from google.appengine.ext import webapp, blobstore
from google.appengine.ext.blobstore.blobstore import BlobInfo
from google.appengine.ext.webapp import blobstore_handlers
import webapp2

try:
  import json
except ImportError:
  import simplejson as json

__author__ = 'hiranya'

def serialize(blob_info):
  if isinstance(blob_info, BlobInfo):
    return { 'file' : blob_info.filename, 'size' : blob_info.size }

class MainHandler(webapp2.RequestHandler):
  def get(self):
    async = self.request.get('async')
    if async is not None and async == 'true':
      upload_url_rpc = blobstore.create_upload_url_async('/python/blobstore/upload')
      upload_url = upload_url_rpc.get_result()
    else:
      upload_url = blobstore.create_upload_url('/python/blobstore/upload')
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps({ 'url' : upload_url }))

class BlobQueryHandler(webapp2.RequestHandler):
  def get(self):
    key = self.request.get('key')
    fetch_data= self.request.get('data')
    if fetch_data is not None and fetch_data == 'true':
      start = self.request.get('start')
      end = self.request.get('end')
      async = self.request.get('async')
      if async is not None and async == 'true':
        data_rpc = blobstore.fetch_data_async(key, int(start), int(end))
        data = data_rpc.get_result()
      else:
        data = blobstore.fetch_data(key, int(start), int(end))
      if data is not None:
        self.response.out.write(data)
      else:
        self.response.set_status(404)
    else:
      file_name = self.request.get('file')
      size = self.request.get('size')
      if file_name is not None and len(file_name) > 0:
        query = BlobInfo.gql("WHERE filename = '%s'" % file_name)
        blob_info = query[0]
        self.response.headers['Content-Type'] = "application/json"
        self.response.out.write(json.dumps(blob_info, default=serialize))
      elif size is not None and len(size) > 0:
        query = BlobInfo.gql("WHERE size > %s" % size)
        data = []
        for result in query:
          data.append(result)
        self.response.headers['Content-Type'] = "application/json"
        self.response.out.write(json.dumps(data, default=serialize))
      else:
        blob_info = BlobInfo.get(key)
        if blob_info is not None:
          self.response.headers['Content-Type'] = "application/json"
          self.response.out.write(json.dumps(blob_info, default=serialize))
        else:
          self.response.set_status(404)

  def delete(self):
    key = self.request.get('key')
    async = self.request.get('async')
    if async is not None and async == 'true':
      delete_rpc = blobstore.delete_async(key)
      if delete_rpc.get_result() is None:
        self.response.out.write(json.dumps({ 'success' : True }))
      else:
        self.response.out.write(json.dumps({ 'success' : False }))
    else:
      blob_info = BlobInfo.get(key)
      self.response.headers['Content-Type'] = "application/json"
      if blob_info is not None:
        blob_info.delete()
        self.response.out.write(json.dumps({ 'success' : True }))
      else:
        self.response.out.write(json.dumps({ 'success' : False }))

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    upload_files = self.get_uploads('file')
    blob_info = upload_files[0]
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps({ 'key' : str(blob_info.key()) }))

class DownloadHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    resource = str(urllib.unquote(resource))
    blob_info = blobstore.BlobInfo.get(resource)
    self.send_blob(blob_info)

application = webapp.WSGIApplication([
  ('/python/blobstore/url', MainHandler),
  ('/python/blobstore/upload', UploadHandler),
  ('/python/blobstore/download/(.*)', DownloadHandler),
  ('/python/blobstore/query', BlobQueryHandler),
], debug=True)

if __name__ == '__main__':
  wsgiref.handlers.CGIHandler().run(application)