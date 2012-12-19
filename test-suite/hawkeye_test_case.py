import httplib
import json
from unittest.case import TestCase

__author__ = 'hiranya'

HOST = None
PORT = -1
LANG = None

class HawkeyeTestCase(TestCase):

  def http_get(self, path):
    return self.__make_request('GET', path)

  def http_post(self, path, payload):
    return self.__make_request('POST', path, payload)

  def http_delete(self, path):
    return self.__make_request('DELETE', path)

  def assert_and_get_list(self, path):
    response = self.http_get(path)
    list = json.loads(response.read())
    self.assertTrue(len(list) > 0)
    return list

  def __make_request(self, method, path, payload=None):
    path = "/" + LANG + path
    conn = httplib.HTTPConnection(HOST + ':' + str(PORT))
    if method == 'POST' or method == 'PUT':
      conn.request(method, path, payload)
    else:
      conn.request(method, path)
    response = conn.getresponse()
    conn.close()
    return response