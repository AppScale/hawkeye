import json
import ssl
import urllib2
import urlparse
from hawkeye_utils import HawkeyeTestCase, HawkeyeTestSuite
import hawkeye_utils

__author__ = 'hiranya'

FILE_UPLOADS = {}

FILE1 = 'file1.txt'
FILE2 = 'file2.txt'
FILE3 = 'file3.txt'

FILE1_DATA = 'FILE UPLOAD CONTENT'
FILE2_DATA = 'AppScale Rocks!!!'
FILE3_DATA = 'ASYNC FILE UPLOAD CONTENT'

class UploadBlobTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/blobstore/url')
    self.assertEquals(response.status, 200)
    url = json.loads(response.payload)['url']
    self.assertTrue(url is not None and len(url) > 0)
    content_type, body = hawkeye_utils.encode(FILE1, FILE1_DATA)
    headers = { 'Content-Type': content_type }
    parser = urlparse.urlparse(url)
    response = self.file_upload(parser.path, body, headers)
    self.assertEquals(response.status, 200)
    blob_key = json.loads(response.payload)['key']
    self.assertTrue(blob_key is not None and len(blob_key) > 0)
    FILE_UPLOADS[FILE1] = blob_key

    response = self.http_get('/blobstore/url')
    self.assertEquals(response.status, 200)
    url = json.loads(response.payload)['url']
    self.assertTrue(url is not None and len(url) > 0)
    content_type, body = hawkeye_utils.encode(FILE2, FILE2_DATA)
    headers = { 'Content-Type': content_type }
    parser = urlparse.urlparse(url)
    response = self.file_upload(parser.path, body, headers)
    self.assertEquals(response.status, 200)
    blob_key = json.loads(response.payload)['key']
    self.assertTrue(blob_key is not None and len(blob_key) > 0)
    FILE_UPLOADS[FILE2] = blob_key

class DownloadBlobTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/blobstore/download/{0}'.format(
      FILE_UPLOADS[FILE1]))
    self.assertEquals(response.status, 200)
    self.assertEquals(response.payload, FILE1_DATA)

    response = self.http_get('/blobstore/download/{0}'.format(
      FILE_UPLOADS[FILE2]))
    self.assertEquals(response.status, 200)
    self.assertEquals(response.payload, FILE2_DATA)

class QueryBlobByKeyTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/blobstore/query?key={0}'.format(
      FILE_UPLOADS[FILE1]))
    self.assertEquals(response.status, 200)
    file_info = json.loads(response.payload)
    self.assertEquals(file_info['filename'], FILE1)

    response = self.http_get('/blobstore/query?key={0}'.format(
      FILE_UPLOADS[FILE2]))
    self.assertEquals(response.status, 200)
    file_info = json.loads(response.payload)
    self.assertEquals(file_info['filename'], FILE2)

    response = self.http_get('/blobstore/query?key=bogus')
    self.assertEquals(response.status, 404)

class QueryBlobByPropertyTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/blobstore/query?' \
                             'file=file1.txt'.format(FILE_UPLOADS[FILE1]))
    self.assertEquals(response.status, 200)
    file_info = json.loads(response.payload)
    self.assertEquals(file_info['filename'], FILE1)

    response = self.http_get('/blobstore/query?' \
                             'file=file2.txt'.format(FILE_UPLOADS[FILE2]))
    self.assertEquals(response.status, 200)
    file_info = json.loads(response.payload)
    self.assertEquals(file_info['filename'], FILE2)

    response = self.http_get('/blobstore/query?' \
                             'size={0}'.format(len(FILE1_DATA)))
    self.assertEquals(response.status, 200)
    blobs = json.loads(response.payload)
    for blob in blobs:
      self.assertNotEquals(blob['filename'], FILE1)


class QueryBlobDataTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/blobstore/query?key={0}&data=' \
                            'true&start=0&end=5'.format(FILE_UPLOADS[FILE1]))
    self.assertEquals(response.status, 200)
    self.assertEquals(response.payload, 'FILE U')

    response = self.http_get('/blobstore/query?key={0}&data=' \
                            'true&start=0&end=5'.format(FILE_UPLOADS[FILE2]))
    self.assertEquals(response.status, 200)
    self.assertEquals(response.payload, 'AppSca')

class DeleteBlobTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_delete('/blobstore/query?key={0}'.format(
      FILE_UPLOADS[FILE1]))
    self.assertEquals(response.status, 200)
    file_info = json.loads(response.payload)
    self.assertTrue(file_info['success'])

    response = self.http_get('/blobstore/download/{0}'.format(
      FILE_UPLOADS[FILE1]))
    self.assertTrue(response.status == 500 or response.status == 404)

    response = self.http_delete('/blobstore/query?key={0}'.format(
      FILE_UPLOADS[FILE2]))
    self.assertEquals(response.status, 200)
    file_info = json.loads(response.payload)
    self.assertTrue(file_info['success'])

    response = self.http_get('/blobstore/download/{0}'.format(
      FILE_UPLOADS[FILE2]))
    self.assertTrue(response.status == 500 or response.status == 404)

class AsyncUploadBlobTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/blobstore/url?async=true')
    self.assertEquals(response.status, 200)
    url = json.loads(response.payload)['url']
    self.assertTrue(url is not None and len(url) > 0)
    content_type, body = hawkeye_utils.encode(FILE3, FILE3_DATA)
    headers = { 'Content-Type': content_type }
    parser = urlparse.urlparse(url)
    response = self.file_upload(parser.path, body, headers)
    self.assertEquals(response.status, 200)
    blob_key = json.loads(response.payload)['key']
    self.assertTrue(blob_key is not None and len(blob_key) > 0)
    FILE_UPLOADS[FILE3] = blob_key

class AsyncQueryBlobDataTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/blobstore/query?key={0}&data=true&'\
                             'start=0&end=5&async=true'.format(FILE_UPLOADS[FILE3]))
    self.assertEquals(response.status, 200)
    self.assertEquals(response.payload, 'ASYNC ')

class AsyncDeleteBlobTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_delete('/blobstore/query?key={0}&' \
                                  'async=true'.format(FILE_UPLOADS[FILE3]))
    self.assertEquals(response.status, 200)
    file_info = json.loads(response.payload)
    self.assertTrue(file_info['success'])

    response = self.http_get('/blobstore/download/{0}'.format(
      FILE_UPLOADS[FILE3]))
    self.assertEquals(response.status, 500)

class CreateURLScheme(HawkeyeTestCase):
  def run_hawkeye_test(self):
    path = '/python/blobstore/create_url'
    url = 'http://{}:{}{}'.format(
      hawkeye_utils.HOST, hawkeye_utils.PORT, path)
    response = urllib2.urlopen(url)
    self.assertEqual(response.read()[:5], 'http:')

    url = 'https://{}:{}{}'.format(
      hawkeye_utils.HOST,
      hawkeye_utils.PORT - hawkeye_utils.SSL_PORT_OFFSET,
      path)
    if hasattr(ssl, '_create_unverified_context'):
      context = ssl._create_unverified_context()
      response = urllib2.urlopen(url, context=context)
    else:
      response = urllib2.urlopen(url)
    self.assertEqual(response.read()[:5], 'https')

def suite(lang):
  suite = HawkeyeTestSuite('Blobstore Test Suite', 'blobstore')
  suite.addTest(UploadBlobTest())
  suite.addTest(DownloadBlobTest())
  suite.addTest(QueryBlobDataTest())
  suite.addTest(QueryBlobByKeyTest())
  suite.addTest(QueryBlobByPropertyTest())
  suite.addTest(DeleteBlobTest())

  if lang == 'python':
    suite.addTest(AsyncUploadBlobTest())
    suite.addTest(AsyncQueryBlobDataTest())
    suite.addTest(AsyncDeleteBlobTest())
    suite.addTest(CreateURLScheme())
  return suite