import json
import urlparse

from hawkeye_test_runner import HawkeyeTestSuite, DeprecatedHawkeyeTestCase

__author__ = 'hiranya'

LOGIN_COOKIES = {}

USER_EMAIL = 'a@a.com'
USER_PASSWORD = 'aaaaaa'

class LoginURLTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/users/home')
    self.assertEquals(response.status, 200)
    url_info = json.loads(response.payload)
    self.assertEquals(url_info['type'], 'login')

class UserLoginTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/users/secure', verbosity=1)
    self.assertEquals(response.status, 302)
    self.assertTrue('location' in response.headers)

    parser = urlparse.urlparse(response.headers['location'])
    login_url = parser.path + '?' + parser.query
    payload = 'email={0}&password={1}&action=Login'.format(
      USER_EMAIL, USER_PASSWORD)
    response = self.http_post(
      login_url, payload, prepend_lang=False, verbosity=1)
    self.assertEquals(response.status, 302)
    self.assertTrue('location' in response.headers)
    self.assertTrue('set-cookie' in response.headers)
    parser = urlparse.urlparse(response.headers['location'])
    continue_url = parser.path
    self.assertTrue(continue_url, '/users/secure')

    LOGIN_COOKIES['user'] = response.headers['set-cookie']
    headers = { 'Cookie' : LOGIN_COOKIES['user'] }
    response = self.http_get('/users/secure', headers=headers, verbosity=1)
    self.assertEquals(response.status, 200)
    user_info = json.loads(response.payload)
    self.assertTrue(user_info['user'] is not None)
    self.assertEquals(user_info['email'], USER_EMAIL)
    self.assertFalse(user_info['admin'])

class AdminLoginTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    response = self.http_get('/users/secure', verbosity=1)
    self.assertEquals(response.status, 302)
    self.assertTrue('location' in response.headers)

    parser = urlparse.urlparse(response.headers['location'])
    login_url = parser.path + '?' + parser.query
    payload = 'email={0}&password={1}&action=Login&admin=True&isAdmin=on'.format(
      USER_EMAIL, USER_PASSWORD)
    response = self.http_post(login_url, payload, prepend_lang=False)
    self.assertEquals(response.status, 302)
    self.assertTrue('location' in response.headers)
    self.assertTrue('set-cookie' in response.headers)
    parser = urlparse.urlparse(response.headers['location'])
    continue_url = parser.path
    self.assertTrue(continue_url, '/users/secure')

    LOGIN_COOKIES['main'] = response.headers['set-cookie']
    headers = { 'Cookie' : LOGIN_COOKIES['main'] }
    response = self.http_get('/users/secure', headers=headers, verbosity=1)
    self.assertEquals(response.status, 200)
    user_info = json.loads(response.payload)
    self.assertTrue(user_info['user'] is not None)
    self.assertEquals(user_info['email'], USER_EMAIL)
    self.assertTrue(user_info['admin'])

class LogoutURLTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    headers = { 'Cookie' : LOGIN_COOKIES['user'] }
    response = self.http_get('/users/home', headers=headers)
    self.assertEquals(response.status, 200)
    url_info = json.loads(response.payload)
    self.assertEquals(url_info['type'], 'logout')

def suite(lang, app):
  suite = HawkeyeTestSuite('User API Test Suite', 'users')
  suite.addTests(LoginURLTest.all_cases(app))
  suite.addTests(UserLoginTest.all_cases(app))
  suite.addTests(AdminLoginTest.all_cases(app))
  suite.addTests(LogoutURLTest.all_cases(app))
  return suite

