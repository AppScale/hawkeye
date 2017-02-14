import json
from StringIO import StringIO

from hawkeye_test_runner import HawkeyeTestSuite, HawkeyeTestCase, \
  DeprecatedHawkeyeTestCase
from hawkeye_utils import hawkeye_request

__author__ = 'hiranya'

FILE_UPLOADS = {}

FILE1_NAME = 'file1.txt'
FILE2_NAME = 'file2.txt'
FILE3_NAME = 'file3.txt'

FILE1 = StringIO('FILE UPLOAD CONTENT')
FILE2 = StringIO('AppScale Rocks!!!')
FILE3 = StringIO('ASYNC FILE UPLOAD CONTENT')

class UploadBlobTest(HawkeyeTestCase):
  def test_blobstore_upload_handler(self):
    response = self.app.get('/{lang}/blobstore/url')
    self.assertEquals(response.status_code, 200)
    url = response.json()['url']
    self.assertTrue(url is not None and len(url) > 0)
    files = {FILE1_NAME: (FILE1_NAME, FILE1, 'application/octet-stream')}
    response = hawkeye_request('POST', url, files=files)
    self.assertEquals(response.status_code, 200)
    blob_key = response.json()['key']
    self.assertTrue(blob_key is not None and len(blob_key) > 0)
    FILE_UPLOADS[FILE1_NAME] = blob_key

    response = self.app.get('/{lang}/blobstore/url')
    self.assertEquals(response.status_code, 200)
    url = response.json()['url']
    self.assertTrue(url is not None and len(url) > 0)
    files = {FILE2_NAME: (FILE2_NAME, FILE2, 'application/octet-stream')}
    response = hawkeye_request('POST', url, files=files)
    self.assertEquals(response.status_code, 200)
    blob_key = response.json()['key']
    self.assertTrue(blob_key is not None and len(blob_key) > 0)
    FILE_UPLOADS[FILE2_NAME] = blob_key

class DownloadBlobTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/blobstore/download/{0}'.format(
      FILE_UPLOADS[FILE1_NAME]))
    self.assertEquals(response.status, 200)
    self.assertEquals(response.payload, FILE1)

    response = self.http_get('/blobstore/download/{0}'.format(
      FILE_UPLOADS[FILE2_NAME]))
    self.assertEquals(response.status, 200)
    self.assertEquals(response.payload, FILE2)

class QueryBlobByKeyTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/blobstore/query?key={0}'.format(
      FILE_UPLOADS[FILE1_NAME]))
    self.assertEquals(response.status, 200)
    file_info = json.loads(response.payload)
    self.assertEquals(file_info['filename'], FILE1_NAME)

    response = self.http_get('/blobstore/query?key={0}'.format(
      FILE_UPLOADS[FILE2_NAME]))
    self.assertEquals(response.status, 200)
    file_info = json.loads(response.payload)
    self.assertEquals(file_info['filename'], FILE2_NAME)

    response = self.http_get('/blobstore/query?key=bogus')
    self.assertEquals(response.status, 404)

class QueryBlobByPropertyTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/blobstore/query?' \
                             'file=file1.txt'.format(FILE_UPLOADS[FILE1_NAME]))
    self.assertEquals(response.status, 200)
    file_info = json.loads(response.payload)
    self.assertEquals(file_info['filename'], FILE1_NAME)

    response = self.http_get('/blobstore/query?' \
                             'file=file2.txt'.format(FILE_UPLOADS[FILE2_NAME]))
    self.assertEquals(response.status, 200)
    file_info = json.loads(response.payload)
    self.assertEquals(file_info['filename'], FILE2_NAME)

    response = self.http_get('/blobstore/query?' \
                             'size={0}'.format(len(FILE1)))
    self.assertEquals(response.status, 200)
    blobs = json.loads(response.payload)
    for blob in blobs:
      self.assertNotEquals(blob['filename'], FILE1_NAME)


class QueryBlobDataTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/blobstore/query?key={0}&data=' \
                            'true&start=0&end=5'.format(FILE_UPLOADS[FILE1_NAME]))
    self.assertEquals(response.status, 200)
    self.assertEquals(response.payload, 'FILE U')

    response = self.http_get('/blobstore/query?key={0}&data=' \
                            'true&start=0&end=5'.format(FILE_UPLOADS[FILE2_NAME]))
    self.assertEquals(response.status, 200)
    self.assertEquals(response.payload, 'AppSca')

class DeleteBlobTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_delete('/blobstore/query?key={0}'.format(
      FILE_UPLOADS[FILE1_NAME]))
    self.assertEquals(response.status, 200)
    file_info = json.loads(response.payload)
    self.assertTrue(file_info['success'])

    response = self.http_get('/blobstore/download/{0}'.format(
      FILE_UPLOADS[FILE1_NAME]))
    self.assertTrue(response.status == 500 or response.status == 404)

    response = self.http_delete('/blobstore/query?key={0}'.format(
      FILE_UPLOADS[FILE2_NAME]))
    self.assertEquals(response.status, 200)
    file_info = json.loads(response.payload)
    self.assertTrue(file_info['success'])

    response = self.http_get('/blobstore/download/{0}'.format(
      FILE_UPLOADS[FILE2_NAME]))
    self.assertTrue(response.status == 500 or response.status == 404)

class AsyncUploadBlobTest(HawkeyeTestCase):
  def test_blob_creation(self):
    response = self.app.get('/{lang}/blobstore/url?async=true')
    self.assertEquals(response.status_code, 200)
    url = response.json()['url']
    self.assertTrue(url is not None and len(url) > 0)
    files = {FILE3_NAME: (FILE3_NAME, FILE3, 'application/octet-stream')}
    response = hawkeye_request('POST', url, files=files)
    self.assertEquals(response.status_code, 200)
    blob_key = response.json()['key']
    self.assertTrue(blob_key is not None and len(blob_key) > 0)
    FILE_UPLOADS[FILE3_NAME] = blob_key

class AsyncQueryBlobDataTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/blobstore/query?key={0}&data=true&'\
                             'start=0&end=5&async=true'.format(FILE_UPLOADS[FILE3_NAME]))
    self.assertEquals(response.status, 200)
    self.assertEquals(response.payload, 'ASYNC ')

class AsyncDeleteBlobTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_delete('/blobstore/query?key={0}&' \
                                  'async=true'.format(FILE_UPLOADS[FILE3_NAME]))
    self.assertEquals(response.status, 200)
    file_info = json.loads(response.payload)
    self.assertTrue(file_info['success'])

    response = self.http_get('/blobstore/download/{0}'.format(
      FILE_UPLOADS[FILE3_NAME]))
    self.assertEquals(response.status, 500)

class CreateURLScheme(HawkeyeTestCase):
  def test_different_schemas(self):
    path = '/python/blobstore/create_url'
    response = self.app.get(path, https=False)
    self.assertTrue(response.url.startswith('http:'))
    response = self.app.get(path, https=True)
    self.assertTrue(response.url.startswith('https'))

def suite(lang, app):
  suite = HawkeyeTestSuite('Blobstore Test Suite', 'blobstore')
  suite.addTests(UploadBlobTest.all_cases(app))
  suite.addTests(DownloadBlobTest.all_cases(app))
  suite.addTests(QueryBlobDataTest.all_cases(app))
  suite.addTests(QueryBlobByKeyTest.all_cases(app))
  suite.addTests(QueryBlobByPropertyTest.all_cases(app))
  suite.addTests(DeleteBlobTest.all_cases(app))

  if lang == 'python':
    suite.addTests(AsyncUploadBlobTest.all_cases(app))
    suite.addTests(AsyncQueryBlobDataTest.all_cases(app))
    suite.addTests(AsyncDeleteBlobTest.all_cases(app))
    suite.addTests(CreateURLScheme.all_cases(app))
  return suite
