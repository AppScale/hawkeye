from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from hawkeye_test_runner import HawkeyeTestCase, HawkeyeTestSuite


class TestChannelAPI(HawkeyeTestCase):
  CONTAINER_ID = 'message'

  CHANNEL_ID = 'channelTest'

  MESSAGE = "wow it's like real-time!"

  READY = 'Channel open'

  # The maximum number of seconds to wait for a channel event.
  TIMEOUT = 10

  UNSET = 'unset'

  def test_js_receive(self):
    listener_url = self.app.build_url(
      '/static/listener.html?channelID={}'.format(self.CHANNEL_ID))

    # Instruct a headless browser to listen on a channel.
    options = Options()
    options.headless = True
    with webdriver.Firefox(firefox_options=options) as driver:
      driver.get(listener_url)

      # Wait for the document to load.
      locator = (By.ID, self.CONTAINER_ID)
      WebDriverWait(driver, self.TIMEOUT).until(
        EC.presence_of_element_located(locator))

      # Wait for the channel to open.
      WebDriverWait(driver, self.TIMEOUT).until(
        EC.text_to_be_present_in_element(locator, self.READY))

      # Post a message to the channel.
      self.app.post(
        '/{lang}/channel/send-message',
        data={'channelID': self.CHANNEL_ID, 'message': self.MESSAGE})

      # Wait for the client to receive the message.
      WebDriverWait(driver, self.TIMEOUT).until(
        EC.text_to_be_present_in_element(locator, self.MESSAGE))


def suite(lang, app):
  suite = HawkeyeTestSuite('Channel Test Suite', 'channel')
  suite.addTests(TestChannelAPI.all_cases(app))
  return suite
