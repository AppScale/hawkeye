import json
from PIL import Image
from time import sleep
import StringIO
from hawkeye_utils import HawkeyeTestCase
import hawkeye_utils

__author__ = 'hiranya'

PROJECTS = {}

class ImageDeleteTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_delete('/images/logo')
    self.assertEquals(response.status, 200)

class ImageUploadTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    content_type, body = hawkeye_utils.encode_file('resources/logo.png')
    headers = { 'Content-Type': content_type }
    response = self.file_upload('/images/logo', body, headers, prepend_lang=True)
    self.assertEquals(response.status, 201)
    project_info = json.loads(response.payload)
    self.assertTrue(project_info['success'])
    self.assertTrue(project_info['project_id'] is not None)
    PROJECTS['appscale'] = project_info['project_id']
    sleep(5)

class ImageLoadTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/images/logo?project_id=' + PROJECTS['appscale'])
    self.assertEquals(response.status, 200)
    self.assertEquals(response.headers['content-type'], 'image/png')

    # Make sure we actually received an image in the response.
    image = Image.open(StringIO.StringIO(response.payload))
    self.assertEquals((100, 32), image.size)

class ImageMetadataTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/images/logo?metadata=true&project_id=' +
                             PROJECTS['appscale'])
    self.assertEquals(response.status, 200)
    logo_info = json.loads(response.payload)
    self.assertEquals(logo_info['width'], 100)
    self.assertEquals(logo_info['format'], 0)

class ImageResizeTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/images/logo?resize=50&metadata=true&project_id=' +
                             PROJECTS['appscale'])
    self.assertEquals(response.status, 200)
    logo_info = json.loads(response.payload)
    self.assertEquals(logo_info['width'], 50)
    self.assertEquals(logo_info['format'], 0)

class ImageResizeTransformTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/images/logo?transform=true&resize=50&'
                             'metadata=true&project_id=' + PROJECTS['appscale'])
    self.assertEquals(response.status, 200)
    logo_info = json.loads(response.payload)
    self.assertEquals(logo_info['width'], 50)
    self.assertEquals(logo_info['format'], 0)

class ImageRotateTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/images/logo?rotate=true&metadata=true&project_id=' +
                             PROJECTS['appscale'])
    self.assertEquals(response.status, 200)
    logo_info = json.loads(response.payload)
    self.assertEquals(logo_info['height'], 100)
    self.assertEquals(logo_info['format'], 0)

class ImageRotateTransformTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/images/logo?transform=true&rotate=true&'
                             'metadata=true&project_id=' + PROJECTS['appscale'])
    self.assertEquals(response.status, 200)
    logo_info = json.loads(response.payload)
    self.assertEquals(logo_info['height'], 100)
    self.assertEquals(logo_info['format'], 0)

def suite(lang):
  suite = hawkeye_utils.HawkeyeTestSuite('Images Test Suite', 'images')
  suite.addTest(ImageDeleteTest())
  suite.addTest(ImageUploadTest())
  suite.addTest(ImageLoadTest())
  suite.addTest(ImageMetadataTest())
  suite.addTest(ImageResizeTest())
  suite.addTest(ImageRotateTest())

  if lang == 'python':
    suite.addTest(ImageResizeTransformTest())
    suite.addTest(ImageRotateTransformTest())
  return suite