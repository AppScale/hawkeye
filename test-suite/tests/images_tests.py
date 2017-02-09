import json
from PIL import Image
from time import sleep
import StringIO

import hawkeye_test_runner
from hawkeye_test_runner import HawkeyeTestCase
from hawkeye_utils import DeprecatedHawkeyeTestCase
import hawkeye_utils

__author__ = 'hiranya'

PROJECTS = {}

class ImageDeleteTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_delete('/images/logo')
    self.assertEquals(response.status, 200)

class ImageUploadTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    with open('resources/logo.png', 'rb') as logo_png:
      response = self.app.post(
        '/{lang}/images/logo', files={'resources/logo.png': logo_png}
      )
    self.assertEquals(response.status_code, 201)
    project_info = response.json()
    self.assertTrue(project_info['success'])
    self.assertIsNotNone(project_info['project_id'])
    PROJECTS['appscale'] = project_info['project_id']
    sleep(5)

class ImageLoadTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/images/logo?project_id=' + PROJECTS['appscale'])
    self.assertEquals(response.status, 200)
    self.assertEquals(response.headers['content-type'], 'image/png')

    # Make sure we actually received an image in the response.
    image = Image.open(StringIO.StringIO(response.payload))
    self.assertEquals(100, image.size[0])

class ImageMetadataTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/images/logo?metadata=true&project_id=' +
                             PROJECTS['appscale'])
    self.assertEquals(response.status, 200)
    logo_info = json.loads(response.payload)
    self.assertEquals(logo_info['width'], 100)
    self.assertEquals(logo_info['format'], 0)

class ImageResizeTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/images/logo?resize=50&metadata=true&project_id=' +
                             PROJECTS['appscale'])
    self.assertEquals(response.status, 200)
    logo_info = json.loads(response.payload)
    self.assertEquals(logo_info['width'], 50)
    self.assertEquals(logo_info['format'], 0)

class ImageResizeTransformTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/images/logo?transform=true&resize=50&'
                             'metadata=true&project_id=' + PROJECTS['appscale'])
    self.assertEquals(response.status, 200)
    logo_info = json.loads(response.payload)
    self.assertEquals(logo_info['width'], 50)
    self.assertEquals(logo_info['format'], 0)

class ImageRotateTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/images/logo?rotate=true&metadata=true&project_id=' +
                             PROJECTS['appscale'])
    self.assertEquals(response.status, 200)
    logo_info = json.loads(response.payload)
    self.assertEquals(logo_info['height'], 100)
    self.assertEquals(logo_info['format'], 0)

class ImageRotateTransformTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/images/logo?transform=true&rotate=true&'
                             'metadata=true&project_id=' + PROJECTS['appscale'])
    self.assertEquals(response.status, 200)
    logo_info = json.loads(response.payload)
    self.assertEquals(logo_info['height'], 100)
    self.assertEquals(logo_info['format'], 0)

def suite(lang, app):
  suite = hawkeye_test_runner.HawkeyeTestSuite('Images Test Suite', 'images')
  suite.addTest(ImageDeleteTest(app))
  suite.addTest(ImageUploadTest(app))
  suite.addTest(ImageLoadTest(app))
  suite.addTest(ImageMetadataTest(app))
  suite.addTest(ImageResizeTest(app))
  suite.addTest(ImageRotateTest(app))

  if lang == 'python':
    suite.addTest(ImageResizeTransformTest(app))
    suite.addTest(ImageRotateTransformTest(app))

  # Clean up entities. They can affect later tests.
  suite.addTest(ImageDeleteTest(app))
  return suite
