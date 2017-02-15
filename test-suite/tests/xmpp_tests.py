import json
import time

from hawkeye_test_runner import HawkeyeTestSuite, DeprecatedHawkeyeTestCase

__author__ = 'chris'

class SendAndReceiveTest(DeprecatedHawkeyeTestCase):
  """This test exercises the XMPP API by sending a message and
  ensuring that the side-effect caused by the message's receipt
  occurs.

  Does not work on the SDK, because it does not send or receive
  XMPP messages.
  """
  def tearDown(self):
    self.http_delete('/xmpp')

  def run_hawkeye_test(self):
    # first, clean up any old data that may have been laying
    # around from a previous invocation of this test
    response = self.http_delete('/xmpp')
    self.assertEquals(response.status, 200)

    # that means we should see no metadata
    response = self.http_get('/xmpp')
    xmpp_info = json.loads(response.payload)
    self.assertEquals(response.status, 200)
    self.assertTrue(xmpp_info['status'])
    self.assertEquals(xmpp_info['state'], 'non-existent')

    # next, visit the URL that triggers a XMPP message to
    # be sent
    response = self.http_post('/xmpp', 'a=b')
    xmpp_info = json.loads(response.payload)
    self.assertEquals(response.status, 200)
    self.assertTrue(xmpp_info['status'])
    self.assertEquals(xmpp_info['state'], 'message sent!')

    # Ensure the XMPP message has been received by the application.
    message_received = False
    for _ in range(5):
      response = self.http_get('/xmpp')
      xmpp_info = json.loads(response.payload)
      self.assertEquals(response.status, 200)
      self.assertTrue(xmpp_info['status'])
      if xmpp_info['state'] == 'message received!':
        message_received = True
        break
      time.sleep(1)

    self.assertTrue(message_received)

    # finally, clean up the mess we made for this test
    response = self.http_delete('/xmpp')
    self.assertEquals(response.status, 200)

    # and we should see no metadata
    response = self.http_get('/xmpp')
    xmpp_info = json.loads(response.payload)
    self.assertEquals(response.status, 200)
    self.assertTrue(xmpp_info['status'])
    self.assertEquals(xmpp_info['state'], 'non-existent')

def suite(lang, app):
  suite = HawkeyeTestSuite('XMPP Test Suite', 'xmpp')
  suite.addTests(SendAndReceiveTest.all_cases(app))
  return suite
