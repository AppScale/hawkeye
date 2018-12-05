import webapp2

from google.appengine.api import channel


class GetToken(webapp2.RequestHandler):
  def get(self):
    channel_id = self.request.get('channelID')
    token = channel.create_channel(channel_id)
    self.response.write(token)


class SendMessage(webapp2.RequestHandler):
  def post(self):
    channel_id = self.request.get('channelID')
    message = self.request.get('message')
    channel.send_message(channel_id, message)


urls = [
  (r'/python/channel/get-token', GetToken),
  (r'/python/channel/send-message', SendMessage)
]
