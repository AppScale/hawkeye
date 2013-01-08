import wsgiref
from google.appengine.api import users
import utils

try:
  import json
except ImportError:
  import simplejson as json

from google.appengine.ext import db, webapp
import webapp2

__author__ = 'chris'

class XmppHandler(xmpp_handlers.CommandHandler):
  """XmppHandler sets up routes for testing the XMPP API.

  Specifically, it sets up a route to (1) send XMPP
  messages, and (2) receive them. The intention is that
  a caller would always call these routes in this order,
  so to aid in debugging, we use the Datastore to store
  the state of messages that have been sent or received.
  To ensure that the Datastore info is in a known state,
  we add a third route to clean up old data. The intended
  state machine for XMPP message metadata is:
  NOT EXISTENT -> MESSAGE SENT -> MESSAGE RECEIVED
  """

  def get(self):
    """Sends an XMPP from this app to itself.
    """
    # send the message
    xmpp.send_message(our_address, MESSAGE)

    # update our metadata
    # TODO(cgb): Add a try/except on this and return
    # success=False if we run into a Datastore exception
    metadata = XmppMetadata(key_name = TEST_KEYNAME)
    metadata.state = MESSAGE_SENT
    metadata.put()

    # write out the result, in json
    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps({
      'success' : True,
      'exists' : True,
      'state': metadata.state
    })


  def text_message(self, message=None):
    """Receives an XMPP message previously sent to this app.
    """
    # make sure the payload is what we're expecting
    if message_arg != MESSAGE:
      self.response.headers['Content-Type'] = "application/json"
      self.response.out.write(json.dumps({
        'success' : False,
        'reason' : 'payload mismatch'
        'state': 'unknown'
      })

    # TODO(cgb): Put a try/except on this and return
    # success = False if a Datastore exception is thrown.
    metadata = XmppMetadata.get_by_keyname(TEST_KEYNAME)
    metadata.state = MESSAGE_RECEIVED
    metadata.put()

    self.response.out.write(json.dumps({
      'success' : True,
      'exists' : True,
      'state': metadata.state
    })

  def delete(self):
    """Cleans up Datastore state concerning XMPP messages.
    """
    # if the metadata exists, delete it
    metadata = XmppMetadata.get_by_keyname(TEST_KEYNAME)
    if not metadata:
      self.response.headers['Content-Type'] = "application/json"
      self.response.out.write(json.dumps({
        'success' : True,
        'deleted' : False,
        'exists' : False
      })

    # TODO(cgb): Put a try/except on this and return
    # success = False if a Datastore exception is thrown.
    metadata.delete()

    self.response.headers['Content-Type'] = "application/json"
    self.response.out.write(json.dumps({
      'success' : True,
      'deleted' : True,
      'exists' : False
    })

application = webapp.WSGIApplication([
  ('/_ah/xmpp/message/chat/', XmppHandler),
], debug=True)

if __name__ == '__main__':
  wsgiref.handlers.CGIHandler().run(application)
