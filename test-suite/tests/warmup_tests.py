from hawkeye_test_runner import HawkeyeTestCase, HawkeyeTestSuite

class WarmupRequestRanTest(HawkeyeTestCase):
  """
  Verifies if app can get info about module and version.
  """
  def runTest(self):
    response = self.app.get('/warmup_status', module='warmup')
    self.assertEquals(response.status_code, 200)
    actual = response.json()
    self.assertTrue(actual['success'])

def suite(lang, app):
  suite = HawkeyeTestSuite('Warmup inbound_services Test Suite', 'warmup')
  suite.addTests(WarmupRequestRanTest.all_cases(app))
  return suite
