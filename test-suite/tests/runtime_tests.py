from hawkeye_test_runner import HawkeyeTestCase, HawkeyeTestSuite


class JSPCompilationTest(HawkeyeTestCase):
  def test_jsp_compilation(self):
    response = self.app.get('/java/jsp')
    self.assertEqual(response.text.strip(), '2 + 2 = 4')


def suite(lang, app):
  suite = HawkeyeTestSuite('Runtime Test Suite', 'runtime')

  if lang == 'java':
    suite.addTests(JSPCompilationTest.all_cases(app))

  return suite
