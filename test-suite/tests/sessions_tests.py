from hawkeye_test_runner import HawkeyeTestCase, HawkeyeTestSuite


class SessionsTest(HawkeyeTestCase):
  def test_sessions(self):
    name = 'user1'
    response = self.app.post('/{lang}/sessions/session_handler',
                             data={'name': name})
    self.assertEqual(response.status_code, 200)
    instance_id = response.text.strip()
    cookies = response.cookies

    # Assuming there are at least two instances for the version
    # (the appengine-web.xml specifies that there should be at least two), it's
    # very unlikely for a request to hit the same instance.
    max_retries = 20
    retry = 0
    while True:
      response = self.app.get('/{lang}/sessions/session_handler',
                              cookies=cookies)
      self.assertEqual(response.status_code, 200)
      if response.json()['instanceId'] == instance_id:
        retry += 1
        self.assertLess(retry, max_retries)
        continue

      self.assertEqual(response.json()['name'], name)


def suite(lang, app):
  suite = HawkeyeTestSuite('Sessions Test Suite', 'sessions')

  if lang == 'java':
    suite.addTests(SessionsTest.all_cases(app))

  return suite
