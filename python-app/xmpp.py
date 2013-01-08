import wsgiref
from google.appengine.api import xmpp
import os

try:
  import json
except ImportError:
  import simplejson as json

from google.appengine.ext import db, webapp
from google.appengine.ext.webapp import xmpp_handlers

__author__ = 'chris'

# To send XMPP messages to ourself, we need to know our
# own hostname. For App Engine, it's always a constant,
# but for AppScale, it can vary based on what IP address
# runs the XMPP receiver.
if 'NGINX_HOST' in os.environ:
  HOST = os.environ['NGINX_HOST']
else:
  HOST = "appspot.com"

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

  MESSAGE = "pew pew from hawkeye"

  NON_EXISTENT = "non-existent"

  MESSAGE_SENT = "message sent!"

  MESSAGE_RECEIVED = "message received!"

  TEST_KEYNAME = "test"

  MY_JABBER_ID = os.environ['APPLICATION_ID'] + "@" + HOST + "/bot"

  def get(self):
    """Returns info on the state of the XMPP message we've
    sent for testing.
    """
    metadata = XmppMetadata.get_by_key_name(self.TEST_KEYNAME)
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
        'state': self.NON_EXISTENT
      }))

  def post(self):
    """Sends an XMPP from this app to itself.
    """
    # send the message
    # TODO(cgb): how do we get our jabber id in AppScale?
    xmpp.send_message(self.MY_JABBER_ID, self.MESSAGE)

    # update our metadata
    # TODO(cgb): Add a try/except on this and return
    # status=False if we run into a Datastore exception
    metadata = XmppMetadata(key_name = self.TEST_KEYNAME,
      state = self.MESSAGE_SENT)
    metadata.put()

    # write out the result, in json
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps({
      'status' : True,
      'exists' : True,
      'state': metadata.state
    }))

  def delete(self):
    """Cleans up Datastore state concerning XMPP messages.
    """
    # if the metadata exists, delete it
    metadata = XmppMetadata.get_by_key_name(self.TEST_KEYNAME)
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

  MESSAGE = "pew pew from hawkeye"

  MESSAGE_RECEIVED = "message received!"

  TEST_KEYNAME = "test"

  def text_message(self, message=None):
    """Receives an XMPP message previously sent to this app.
    """
    # make sure the payload is what we're expecting
    if message.arg != self.MESSAGE:
      self.response.headers['Content-Type'] = "application/json"
      self.response.out.write(json.dumps({
        'status' : False,
        'reason' : 'payload mismatch',
        'state': 'unknown'
      }))
      return

    # TODO(cgb): Put a try/except on this and return
    # status = False if a Datastore exception is thrown.
    metadata = XmppMetadata.get_by_key_name(self.TEST_KEYNAME)
    metadata.state = self.MESSAGE_RECEIVED
    metadata.put()

    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps({
      'status' : True,
      'exists' : True,
      'state': metadata.state
    }))

application = webapp.WSGIApplication([
  (r'/python/xmpp/?', XmppGetHandler),
  (r'/_ah/xmpp/message/chat/?', XmppReceiveHandler),
], debug=True)

if __name__ == '__main__':
  wsgiref.handlers.CGIHandler().run(application)
