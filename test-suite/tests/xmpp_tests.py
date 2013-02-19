import json
import time

from hawkeye_utils import HawkeyeTestCase, HawkeyeTestSuite

__author__ = 'chris'

class SendAndReceiveTest(HawkeyeTestCase):
  """This test exercises the XMPP API by sending a message and
  ensuring that the side-effect caused by the message's receipt
  occurs.

  Does not work on the SDK, because it does not send or receive
  XMPP messages.
  """

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

    # wait a moment for the message to be sent and the
    # datastore operation to occur
    time.sleep(5)

    # the sending of the XMPP message should have been
    # received by the app, which then causes the datastore
    # entry to be updated. let's make sure that update happened!
    response = self.http_get('/xmpp')
    xmpp_info = json.loads(response.payload)
    self.assertEquals(response.status, 200)
    self.assertTrue(xmpp_info['status'])
    self.assertEquals(xmpp_info['state'], 'message received!')

    # finally, clean up the mess we made for this test
    response = self.http_delete('/xmpp')
    self.assertEquals(response.status, 200)

    # and we should see no metadata
    response = self.http_get('/xmpp')
    xmpp_info = json.loads(response.payload)
    self.assertEquals(response.status, 200)
    self.assertTrue(xmpp_info['status'])
    self.assertEquals(xmpp_info['state'], 'non-existent')

def suite(lang):
  suite = HawkeyeTestSuite('XMPP Test Suite', 'xmpp')
  suite.addTest(SendAndReceiveTest())
  return suite
