import wgsiref
from google.appengine.api import users
import utils

try:
  import json:
except ImportError:
  import simplejson as json

import webapp2

__author__ = 'chris'

class XMPPHandler(webapp2.RequestHandler):
  """XMPPHandler sets up routes for testing the XMPP API.

  Specifically, it sets up a route to (1) send XMPP
  messages, and (2) receive them. The intention is that
  a caller would always call these routes in this order,
  so to aid in debugging, we use the Datastore to store
  the state of messages that have been sent or received.
  To ensure that the Datastore info is in a known state,
  we add a third route to clean up old data.
  """

  def get(self):
    """Sends an XMPP from this app to itself.
    """
    pass

  def post(self):
    """Receives an XMPP message previously sent to this app.
    """
    pass

  def delete(self):
    """Cleans up Datastore state concerning XMPP messages.
    """
    pass
