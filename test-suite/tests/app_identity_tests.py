import base64
from urlparse import urlparse

from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from hawkeye_test_runner import HawkeyeTestCase, HawkeyeTestSuite


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


class ProjectIDTest(HawkeyeTestCase):
  def test_project_id(self):
    project_id = self.app.get('/{lang}/app_identity/project_id').text.strip()
    self.assertEqual(project_id, self.app.app_id)


class HostnameTest(HawkeyeTestCase):
  def test_hostname(self):
    hostname = self.app.get('/{lang}/app_identity/hostname').text.strip()
    version_location = self.app.build_url('/', https=False)
    expected_hostname = urlparse(version_location).netloc
    self.assertEqual(hostname, expected_hostname)


class AccessTokenTest(HawkeyeTestCase):
  def test_access_token(self):
    response = self.app.get('/{lang}/app_identity/service_account_name')
    self.assertEqual(response.status_code, 200)

    response = self.app.get('/{lang}/app_identity/access_token')
    # TODO: Test the token itself.
    self.assertEqual(response.status_code, 200)


class SignatureTest(HawkeyeTestCase):
  def test_blob_signing(self):
    blob = 'important message'
    payload = base64.urlsafe_b64encode(blob)
    response = self.app.get(
      '/{{lang}}/app_identity/sign?blob={}'.format(payload))
    signature = base64.b64decode(response.json()['signature'])

    response = self.app.get('/{lang}/app_identity/certificates')
    certificates = response.json()

    valid_signature = False
    for cert in certificates:
      if verify_signature(blob, signature, cert['pem'].encode('utf-8')):
        valid_signature = True

    self.assertTrue(valid_signature)


def suite(lang, app):
  suite = HawkeyeTestSuite('App Identity Test Suite', 'app_identity')

  suite.addTests(ProjectIDTest.all_cases(app))
  suite.addTests(HostnameTest.all_cases(app))
  suite.addTests(AccessTokenTest.all_cases(app))
  suite.addTests(SignatureTest.all_cases(app))

  return suite
