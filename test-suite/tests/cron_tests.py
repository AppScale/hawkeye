import datetime
import time

from hawkeye_test_runner import (HawkeyeTestCase, HawkeyeTestSuite,
                                 DeprecatedHawkeyeTestCase)

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
      time.sleep(5)
    self.assertEquals(success, True)


class CronTargetTest(HawkeyeTestCase):
  def test_cron_target(self):
    deadline = time.time() + 120
    while True:
      self.assertLess(time.time(), deadline)
      response = self.app.get('/{lang}/cron-target')
      if response.status_code == 200:
        break


def suite(lang, app):
  suite = HawkeyeTestSuite('Cron Test Suite', 'cron')
  suite.addTests(CronTest.all_cases(app))
  if lang == 'python':
    suite.addTests(CronTargetTest.all_cases(app))

  return suite
