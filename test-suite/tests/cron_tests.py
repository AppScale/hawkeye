from hawkeye_utils import DeprecatedHawkeyeTestCase, HawkeyeConstants
from hawkeye_test_runner import HawkeyeTestSuite
import json
from time import sleep
import uuid
import datetime

__author__ = 'jovan'

class CronTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    time_start = datetime.datetime.now()
    success = False
    while True:
      response = self.http_get('/cron?query=True')
      if response.status == 200:
        success = True
        break
      time_now = datetime.datetime.now()
      time_delta = time_now - time_start
      seconds = time_delta.seconds
      if(seconds > 120):
        break
      sleep(5)
    self.assertEquals(success, True)

def suite(lang, app):
  suite = HawkeyeTestSuite('Cron Test Suite', 'cron')
  suite.addTests(CronTest.all_cases(app))
  return suite
