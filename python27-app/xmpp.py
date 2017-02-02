import json
import logging
import os
import time

from google.appengine.api import xmpp
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp import xmpp_handlers

# To send XMPP messages to ourself, we need to know our
# own hostname. For App Engine, it's always a constant,
# but for AppScale, it can vary based on what IP address
# runs the XMPP receiver.
# Also, in App Engine, getting your application ID from
# the environment includes a s~ at the beginning (or
# a dev~ on the dev_appserver, while in AppScale it
# does not, so remove that off the front so that we get
# the right host to send our messages to.
if 'NGINX_HOST' in os.environ:  # AppScale
  HOST = os.environ['NGINX_HOST']
  APP_ID = os.environ['APPLICATION_ID']
else:  # Google App Engine
  HOST = "appspot.com"
  APP_ID = os.environ['APPLICATION_ID'].split("~")[1]
MY_JABBER_ID = APP_ID + "@" + HOST

# The keyname used to track message state via a datastore entity.
TEST_KEYNAME = "test"


class XmppMessages(object):
  """ The messages used in the XMPP tests. """
  HELLO = 'pew pew from hawkeye'
  NON_EXISTENT = 'non-existent'
  SENT = 'message sent!'
  RECEIVED = 'message received!'


class XmppMetadata(db.Model):
  """XmppMetadata tracks state about XMPP messages sent
  during Hawkeye tests.

  The following handlers use XmppMetadata as a debugging
  aid to ensure that XMPP messages are being sent and
  received correctly.
  """
  state = db.StringProperty(required=True)

class XmppGetHandler(webapp.RequestHandler):
  """XmppGetHandler sets up routes for testing the XMPP API.

  Specifically, it sets up a route to (1) send XMPP
  messages, to (2) view XMPP metadata, and (3) delete XMPP
  metadata. The Datastore is used to store
  the state of messages that have been sent or received.
  To ensure that the Datastore info is in a known state,
  we have a route to clean up old data. The intended
  state machine for XMPP message metadata is:
  NON EXISTENT -> MESSAGE SENT -> MESSAGE RECEIVED
  """
  def get(self):
    """Returns info on the state of the XMPP message we've
    sent for testing.
    """
    metadata = XmppMetadata.get_by_key_name(TEST_KEYNAME)
    if metadata:
      self.response.headers['Content-Type'] = "application/json"
      self.response.out.write(json.dumps({
        'status' : True,
        'exists' : True,
        'state': metadata.state
      }))
    else:
      self.response.headers['Content-Type'] = "application/json"
      self.response.out.write(json.dumps({
        'status' : True,
        'exists' : False,
        'state': XmppMessages.NON_EXISTENT
      }))

  def post(self):
    """Sends an XMPP from this app to itself. """
    @db.transactional
    def update_state(key):
      metadata = db.get(key)
      if metadata is None:
        XmppMetadata(key_name=TEST_KEYNAME, state=XmppMessages.SENT).put()
      else:
        # The 'received' handler may have already updated the state.
        assert metadata.state == XmppMessages.RECEIVED

    xmpp.send_message(MY_JABBER_ID, XmppMessages.HELLO)

    entity_key = db.Key.from_path('XmppMetadata', TEST_KEYNAME)
    update_state(entity_key)

    # write out the result, in json
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps({
      'status' : True,
      'exists' : True,
      'state': XmppMessages.SENT
    }))

  def delete(self):
    """Cleans up Datastore state concerning XMPP messages.
    """
    # if the metadata exists, delete it
    metadata = XmppMetadata.get_by_key_name(TEST_KEYNAME)
    if not metadata:
      self.response.headers['Content-Type'] = "application/json"
      self.response.out.write(json.dumps({
        'status' : True,
        'deleted' : False,
        'exists' : False
      }))
      return

    # TODO(cgb): Put a try/except on this and return
    # status = False if a Datastore exception is thrown.
    metadata.delete()

    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps({
      'status' : True,
      'deleted' : True,
      'exists' : False
    }))

class XmppReceiveHandler(xmpp_handlers.CommandHandler):
  """XmppReceiveHandler sets up routes for receiving XMPP messages.

  To enable external callers to know when messages have been
  received, this handler writes to the Datastore (which can then
  be accessed via the XmppGetHandler.
  """
  def text_message(self, message=None):
    """Receives an XMPP message previously sent to this app.
    """
    # make sure the payload is what we're expecting
    if message.arg != XmppMessages.HELLO:
      self.response.headers['Content-Type'] = "application/json"
      self.response.out.write(json.dumps({
        'status' : False,
        'reason' : 'payload mismatch',
        'state': 'unknown'
      }))
      return

    XmppMetadata(key_name=TEST_KEYNAME, state=XmppMessages.RECEIVED).put()

    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps({
      'status': True,
      'exists': True,
      'state': XmppMessages.RECEIVED
    }))

urls = [
  (r'/python/xmpp/?', XmppGetHandler),
  (r'/_ah/xmpp/message/chat/?', XmppReceiveHandler),
]
