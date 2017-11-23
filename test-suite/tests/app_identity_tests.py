import base64
import json
from urlparse import urlparse

from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from hawkeye_test_runner import DeprecatedHawkeyeTestCase, HawkeyeTestSuite


def verify_signature(data, signature, x509_certificate):
  cert = x509.load_pem_x509_certificate(x509_certificate, default_backend())
  public_key = cert.public_key()

  try:
    public_key.verify(
      signature,
      data,
      padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
      ),
      hashes.SHA256()
    )
  except InvalidSignature:
    return False

  return True


class ProjectIDTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    project_id = self.http_get('/app_identity/project_id').payload
    self.assertEqual(project_id, 'hawkeyepython27')


class HostnameTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    hostname = self.http_get('/app_identity/hostname').payload
    version_location = self.app.build_url('/', https=False)
    expected_hostname = urlparse(version_location).netloc
    self.assertEqual(hostname, expected_hostname)


class AccessTokenTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/app_identity/service_account_name')
    self.assertEqual(response.status, 200)

    response = self.http_get('/app_identity/access_token')
    # TODO: Test the token itself.
    self.assertEqual(response.status, 200)


class SignatureTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    blob = 'important message'
    payload = base64.urlsafe_b64encode(blob)
    response = self.http_get('/app_identity/sign?blob={}'.format(payload))
    signature = base64.b64decode(json.loads(response.payload)['signature'])

    response = self.http_get('/app_identity/certificates')
    certificates = json.loads(response.payload)

    valid_signature = False
    for cert in certificates:
      if verify_signature(blob, signature, cert['pem'].encode('utf-8')):
        valid_signature = True

    self.assertTrue(valid_signature)


def suite(lang, app):
  suite = HawkeyeTestSuite('App Identity Test Suite', 'app_identity')

  if lang == 'python':
    suite.addTests(ProjectIDTest.all_cases(app))
    suite.addTests(HostnameTest.all_cases(app))
    suite.addTests(AccessTokenTest.all_cases(app))
    suite.addTests(SignatureTest.all_cases(app))

  return suite
