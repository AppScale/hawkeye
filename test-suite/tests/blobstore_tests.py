import json
import urlparse
from hawkeye_utils import HawkeyeTestCase, HawkeyeTestSuite

__author__ = 'hiranya'

file_uploads = {}

FILE1 = 'file1.txt'
FILE2 = 'file2.txt'
FILE3 = 'file3.txt'

FILE1_DATA = 'FILE UPLOAD CONTENT'
FILE2_DATA = 'AppScale Rocks!!!'
FILE3_DATA = 'ASYNC FILE UPLOAD CONTENT'

class UploadBlobTest(HawkeyeTestCase):
  def runTest(self):
    global file_uploads

    status, headers, payload = self.http_get('/blobstore/url')
    self.assertEquals(status, 200)
    url = json.loads(payload)['url']
    self.assertTrue(url is not None and len(url) > 0)
    content_type, body = self.encode(FILE1, FILE1_DATA)
    headers = { 'Content-Type': content_type }
    parser = urlparse.urlparse(url)
    status, headers, payload = self.file_upload(parser.path, body, headers)
    self.assertEquals(status, 200)
    blob_key = json.loads(payload)['key']
    self.assertTrue(blob_key is not None and len(blob_key) > 0)
    file_uploads[FILE1] = blob_key

    status, headers, payload = self.http_get('/blobstore/url')
    self.assertEquals(status, 200)
    url = json.loads(payload)['url']
    self.assertTrue(url is not None and len(url) > 0)
    content_type, body = self.encode(FILE2, FILE2_DATA)
    headers = { 'Content-Type': content_type }
    parser = urlparse.urlparse(url)
    status, headers, payload = self.file_upload(parser.path, body, headers)
    self.assertEquals(status, 200)
    blob_key = json.loads(payload)['key']
    self.assertTrue(blob_key is not None and len(blob_key) > 0)
    file_uploads[FILE2] = blob_key

  def encode (self, file_name, content):
    # Thanks Pietro Abate for the helpful post at:
    # http://mancoosi.org/~abate/upload-file-using-httplib
    BOUNDARY = '----------boundary------'
    CRLF = '\r\n'
    body = []
    body.extend(
      ['--' + BOUNDARY,
       'Content-Disposition: form-data; name="file"; filename="%s"'
       % file_name,
       # The upload server determines the mime-type, no need to set it.
       'Content-Type: application/octet-stream',
       '',
       content,
       ])
    # Finalize the form body
    body.extend(['--' + BOUNDARY + '--', ''])
    return 'multipart/form-data; boundary=%s' % BOUNDARY, CRLF.join(body)

class DownloadBlobTest(HawkeyeTestCase):
  def runTest(self):
    status, headers, payload = self.http_get('/blobstore/download/{0}'.format(file_uploads[FILE1]))
    self.assertEquals(status, 200)
    self.assertEquals(payload, FILE1_DATA)

    status, headers, payload = self.http_get('/blobstore/download/{0}'.format(file_uploads[FILE2]))
    self.assertEquals(status, 200)
    self.assertEquals(payload, FILE2_DATA)

class QueryBlobMetadataTest(HawkeyeTestCase):
  def runTest(self):
    status, headers, payload = self.http_get('/blobstore/query?key={0}'.format(file_uploads[FILE1]))
    self.assertEquals(status, 200)
    dict = json.loads(payload)
    self.assertEquals(dict['file'], FILE1)

    status, headers, payload = self.http_get('/blobstore/query?key={0}'.format(file_uploads[FILE2]))
    self.assertEquals(status, 200)
    dict = json.loads(payload)
    self.assertEquals(dict['file'], FILE2)

    status, headers, payload = self.http_get('/blobstore/query?key=bogus')
    self.assertEquals(status, 404)

class BlobstoreGQLTest(HawkeyeTestCase):
  def runTest(self):
    status, headers, payload = self.http_get('/blobstore/query?file=file1.txt'.format(file_uploads[FILE1]))
    self.assertEquals(status, 200)
    dict = json.loads(payload)
    self.assertEquals(dict['file'], FILE1)

    status, headers, payload = self.http_get('/blobstore/query?file=file2.txt'.format(file_uploads[FILE2]))
    self.assertEquals(status, 200)
    dict = json.loads(payload)
    self.assertEquals(dict['file'], FILE2)

    status, headers, payload = self.http_get('/blobstore/query?size={0}'.format(len(FILE1_DATA)))
    self.assertEquals(status, 200)
    blobs = json.loads(payload)
    self.assertTrue(len(blobs) > 0)
    for blob in blobs:
      self.assertNotEquals(blob['file'], FILE1)


class QueryBlobDataTest(HawkeyeTestCase):
  def runTest(self):
    status, headers, payload = self.http_get('/blobstore/query?key={0}&data=true&start=0&end=5'.format(file_uploads[FILE1]))
    self.assertEquals(status, 200)
    self.assertEquals(payload, 'FILE U')

    status, headers, payload = self.http_get('/blobstore/query?key={0}&data=true&start=0&end=5'.format(file_uploads[FILE2]))
    self.assertEquals(status, 200)
    self.assertEquals(payload, 'AppSca')

class AsyncQueryBlobDataTest(HawkeyeTestCase):
  def runTest(self):
    status, headers, payload = self.http_get('/blobstore/query?key={0}&data=true&start=0&end=5&async=true'.format(file_uploads[FILE1]))
    self.assertEquals(status, 200)
    self.assertEquals(payload, 'FILE U')

    status, headers, payload = self.http_get('/blobstore/query?key={0}&data=true&start=0&end=5&async=true'.format(file_uploads[FILE2]))
    self.assertEquals(status, 200)
    self.assertEquals(payload, 'AppSca')

class DeleteBlobTest(HawkeyeTestCase):
  def runTest(self):
    status, headers, payload = self.http_delete('/blobstore/query?key={0}'.format(file_uploads[FILE1]))
    self.assertEquals(status, 200)
    dict = json.loads(payload)
    self.assertTrue(dict['success'])

    status, headers, payload = self.http_get('/blobstore/download/{0}'.format(file_uploads[FILE1]))
    self.assertEquals(status, 500)

    status, headers, payload = self.http_delete('/blobstore/query?key={0}'.format(file_uploads[FILE2]))
    self.assertEquals(status, 200)
    dict = json.loads(payload)
    self.assertTrue(dict['success'])

    status, headers, payload = self.http_get('/blobstore/download/{0}'.format(file_uploads[FILE2]))
    self.assertEquals(status, 500)

class AsyncUploadBlobTest(UploadBlobTest):
  def runTest(self):
    global file_uploads

    status, headers, payload = self.http_get('/blobstore/url?async=true')
    self.assertEquals(status, 200)
    url = json.loads(payload)['url']
    self.assertTrue(url is not None and len(url) > 0)
    content_type, body = self.encode(FILE3, FILE3_DATA)
    headers = { 'Content-Type': content_type }
    parser = urlparse.urlparse(url)
    status, headers, payload = self.file_upload(parser.path, body, headers)
    self.assertEquals(status, 200)
    blob_key = json.loads(payload)['key']
    self.assertTrue(blob_key is not None and len(blob_key) > 0)
    file_uploads[FILE3] = blob_key

class AsyncDeleteBlobTest(HawkeyeTestCase):
  def runTest(self):
    status, headers, payload = self.http_delete('/blobstore/query?key={0}&async=true'.format(file_uploads[FILE3]))
    self.assertEquals(status, 200)
    dict = json.loads(payload)
    self.assertTrue(dict['success'])

    status, headers, payload = self.http_get('/blobstore/download/{0}'.format(file_uploads[FILE3]))
    self.assertEquals(status, 500)

def suite():
  suite = HawkeyeTestSuite('Blobstore Test Suite', 'blobstore')
  suite.addTest(UploadBlobTest())
  suite.addTest(AsyncUploadBlobTest())
  suite.addTest(DownloadBlobTest())
  suite.addTest(QueryBlobMetadataTest())
  suite.addTest(BlobstoreGQLTest())
  suite.addTest(QueryBlobDataTest())
  suite.addTest(AsyncQueryBlobDataTest())
  suite.addTest(DeleteBlobTest())
  suite.addTest(AsyncDeleteBlobTest())
  return suite