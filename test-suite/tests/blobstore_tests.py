import json
import urlparse
from hawkeye_utils import HawkeyeTestCase, HawkeyeTestSuite

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
    content_type, body = self.encode(FILE1, FILE1_DATA)
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
    content_type, body = self.encode(FILE2, FILE2_DATA)
    headers = { 'Content-Type': content_type }
    parser = urlparse.urlparse(url)
    response = self.file_upload(parser.path, body, headers)
    self.assertEquals(response.status, 200)
    blob_key = json.loads(response.payload)['key']
    self.assertTrue(blob_key is not None and len(blob_key) > 0)
    FILE_UPLOADS[FILE2] = blob_key

  def encode (self, file_name, content):
    """
    Encode the specified file name and content payload into a HTTP
    file upload request.

    Args:
      file_name Name of the file
      content   String payload to be uploaded

    Returns:
      A HTTP multipart form request encoded payload string
    """

    # Thanks Pietro Abate for the helpful post at:
    # http://mancoosi.org/~abate/upload-file-using-httplib
    boundary = '----------boundary------'
    delimiter = '\r\n'
    body = []
    body.extend(
      ['--' + boundary,
       'Content-Disposition: form-data; name="file"; filename="%s"'
       % file_name,
       # The upload server determines the mime-type, no need to set it.
       'Content-Type: application/octet-stream',
       '',
       content,
       ])
    # Finalize the form body
    body.extend(['--' + boundary + '--', ''])
    return 'multipart/form-data; boundary=%s' % boundary, delimiter.join(body)

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

class QueryBlobMetadataTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/blobstore/query?key={0}'.format(
      FILE_UPLOADS[FILE1]))
    self.assertEquals(response.status, 200)
    file_info = json.loads(response.payload)
    self.assertEquals(file_info['file'], FILE1)

    response = self.http_get('/blobstore/query?key={0}'.format(
      FILE_UPLOADS[FILE2]))
    self.assertEquals(response.status, 200)
    file_info = json.loads(response.payload)
    self.assertEquals(file_info['file'], FILE2)

    response = self.http_get('/blobstore/query?key=bogus')
    self.assertEquals(response.status, 404)

class BlobstoreGQLTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/blobstore/query?' \
                             'file=file1.txt'.format(FILE_UPLOADS[FILE1]))
    self.assertEquals(response.status, 200)
    file_info = json.loads(response.payload)
    self.assertEquals(file_info['file'], FILE1)

    response = self.http_get('/blobstore/query?' \
                             'file=file2.txt'.format(FILE_UPLOADS[FILE2]))
    self.assertEquals(response.status, 200)
    file_info = json.loads(response.payload)
    self.assertEquals(file_info['file'], FILE2)

    response = self.http_get('/blobstore/query?' \
                             'size={0}'.format(len(FILE1_DATA)))
    self.assertEquals(response.status, 200)
    blobs = json.loads(response.payload)
    self.assertTrue(len(blobs) > 0)
    for blob in blobs:
      self.assertNotEquals(blob['file'], FILE1)


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

class AsyncQueryBlobDataTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/blobstore/query?key={0}&data=true&' \
                    'start=0&end=5&async=true'.format(FILE_UPLOADS[FILE1]))
    self.assertEquals(response.status, 200)
    self.assertEquals(response.payload, 'FILE U')

    response = self.http_get('/blobstore/query?key={0}&data=true&' \
                    'start=0&end=5&async=true'.format(FILE_UPLOADS[FILE2]))
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
    self.assertEquals(response.status, 500)

    response = self.http_delete('/blobstore/query?key={0}'.format(
      FILE_UPLOADS[FILE2]))
    self.assertEquals(response.status, 200)
    file_info = json.loads(response.payload)
    self.assertTrue(file_info['success'])

    response = self.http_get('/blobstore/download/{0}'.format(
      FILE_UPLOADS[FILE2]))
    self.assertEquals(response.status, 500)

class AsyncUploadBlobTest(UploadBlobTest):
  def run_hawkeye_test(self):
    response = self.http_get('/blobstore/url?async=true')
    self.assertEquals(response.status, 200)
    url = json.loads(response.payload)['url']
    self.assertTrue(url is not None and len(url) > 0)
    content_type, body = self.encode(FILE3, FILE3_DATA)
    headers = { 'Content-Type': content_type }
    parser = urlparse.urlparse(url)
    response = self.file_upload(parser.path, body, headers)
    self.assertEquals(response.status, 200)
    blob_key = json.loads(response.payload)['key']
    self.assertTrue(blob_key is not None and len(blob_key) > 0)
    FILE_UPLOADS[FILE3] = blob_key

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