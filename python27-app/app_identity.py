import webapp2
import json
from google.appengine.api import app_identity
import base64


class ProjectIDHandler(webapp2.RequestHandler):
  def get(self):
    self.response.write(app_identity.get_application_id())


class HostnameHandler(webapp2.RequestHandler):
  def get(self):
    self.response.write(app_identity.get_default_version_hostname())


class AccessTokenHandler(webapp2.RequestHandler):
  def get(self):
    auth_token, expiration_time = app_identity.get_access_token(
        'https://www.googleapis.com/auth/cloud-platform')
    json.dump({'token': auth_token, 'expires': expiration_time}, self.response)


class SignBlobHandler(webapp2.RequestHandler):
  def get(self):
    encoded_blob = self.request.get('blob').encode('utf-8')
    blob = base64.urlsafe_b64decode(encoded_blob)
    key_name, signature = app_identity.sign_blob(blob)
    json.dump({'key_name': key_name, 'signature': base64.b64encode(signature)},
              self.response)


class CertificateHandler(webapp2.RequestHandler):
  def get(self):
    certs = []
    for cert in app_identity.get_public_certificates():
      certs.append({'key_name': cert.key_name,
                    'pem': cert.x509_certificate_pem})

    json.dump(certs, self.response)


class ServiceAccountNameHandler(webapp2.RequestHandler):
  def get(self):
    self.response.write(app_identity.get_service_account_name())


urls = [
    ('/python/app_identity/project_id', ProjectIDHandler),
    ('/python/app_identity/hostname', HostnameHandler),
    ('/python/app_identity/access_token', AccessTokenHandler),
    ('/python/app_identity/sign', SignBlobHandler),
    ('/python/app_identity/certificates', CertificateHandler),
    ('/python/app_identity/service_account_name', ServiceAccountNameHandler)
]
