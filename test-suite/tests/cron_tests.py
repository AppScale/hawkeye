from hawkeye_utils import HawkeyeTestCase, HawkeyeConstants, HawkeyeTestSuite
import json
from time import sleep
import uuid

__author__ = 'jovan'

class CronTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/cron?query=True')
    entity_list = json.loads(response.payload)
    self.assertEquals(response.status, 200)

def suite(lang):
  suite = HawkeyeTestSuite('Cron Test Suite', 'cron')
  suite.addTest(CronTest())
  return suite
