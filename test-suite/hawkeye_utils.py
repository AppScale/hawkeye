import httplib
import json
import os
import ssl
import sys

from unittest.case import TestCase
from unittest.runner import TextTestResult, TextTestRunner

from hawkeye_test_runner import HawkeyeTestCase


class ResponseInfo:
  """
  Contains the metadata and data related to a HTTP response. In
  particular this class can be used as a holder of HTTP response
  code, headers and payload information.
  """

  def __init__(self, response):
    """
    Create a new instance of ResponseInfo using the given HTTPResponse
    object.
    """
    self.status = response.status_code
    self.headers = response.headers
    self.payload = response.text()


class DeprecatedHawkeyeTestCase(HawkeyeTestCase):
  """
  This abstract class provides a skeleton to implement actual
  Hawkeye test cases. To implement a test case, this class must
  be extended by providing an implementation for the runTest
  method. Use the http_* methods to perform HTTP calls on backend
  endpoints. All the HTTP calls performed via these methods are
  traced and logged to hawkeye-logs/http.log.
  """
  LANG = None

  def __init__(self, application):
    """
    Args:
      application: Application object
    """
    super(DeprecatedHawkeyeTestCase, self).__init__(application)
    self.description_printed = False

  def runTest(self):
    """
    Called by the unittest framework to run a test case.
    """
    self.run_hawkeye_test()

  def run_hawkeye_test(self):
    """
    Subclasses must implement this method and provide the actual
    test case logic.
    """
    raise NotImplementedError

  def http_get(self, path, headers=None, prepend_lang=True, use_ssl=False):
    """
    Perform a HTTP GET request on the specified URL path.
    The hostname and port segments of the URL are inferred from
    the values of the 2 constants hawkeye_utils.HOST and
    hawkeye_utils.PORT.

    Args:
      path          A URL path fragment (eg: /foo)
      headers       A dictionary to be sent as HTTP headers
      prepend_lang  If True the value of hawkeye_utils.LANG will be
                    prepended to the provided URL path. Default is
                    True.
      use_ssl       If True use HTTPS to make the connection. Defaults
                    to False.

    Returns:
      An instance of ResponseInfo
    """
    return self.__make_request('GET', path, headers=headers,
      prepend_lang=prepend_lang, use_ssl=use_ssl)

  def http_post(self, path, payload, headers=None, prepend_lang=True):
    """
    Perform a HTTP POST request on the specified URL path.
    The hostname and port segments of the URL are inferred from
    the values of the 2 constants hawkeye_utils.HOST and
    hawkeye_utils.PORT. If a content-type header is not set
    defaults to 'application/x-www-form-urlencoded' content type.

    Args:
      path          A URL path fragment (eg: /foo)
      payload       A string payload to be sent POSTed
      headers       A dictionary of headers
      prepend_lang  If True the value of hawkeye_utils.LANG will be
                    prepended to the provided URL path. Default is
                    True

    Returns:
      An instance of ResponseInfo
    """
    if headers is None:
      headers = { 'Content-Type' : 'application/x-www-form-urlencoded' }
    elif not headers.has_key('Content-Type'):
      headers['Content-Type'] = 'application/x-www-form-urlencoded'
    return self.__make_request('POST', path, payload, headers=headers,
      prepend_lang=prepend_lang)

  def http_put(self, path, payload, headers=None, prepend_lang=True):
    """
    Perform a HTTP PUT request on the specified URL path.
    The hostname and port segments of the URL are inferred from
    the values of the 2 constants hawkeye_utils.HOST and
    hawkeye_utils.PORT. If a content-type header is not set
    defaults to 'application/x-www-form-urlencoded' content type.

    Args:
      path          A URL path fragment (eg: /foo)
      payload       A string payload to be sent POSTed
      headers       A dictionary of headers
      prepend_lang  If True the value of hawkeye_utils.LANG will be
                    prepended to the provided URL path. Default is
                    True

    Returns:
      An instance of ResponseInfo
    """
    if headers is None:
      headers = { 'Content-Type' : 'application/x-www-form-urlencoded' }
    elif not headers.has_key('Content-Type'):
      headers['Content-Type'] = 'application/x-www-form-urlencoded'
    return self.__make_request('PUT', path, payload, headers=headers,
      prepend_lang=prepend_lang)

  def http_delete(self, path, prepend_lang=True):
    """
    Perform a HTTP DELETE request on the specified URL path.
    The hostname and port segments of the URL are inferred from
    the values of the 2 constants hawkeye_utils.HOST and
    hawkeye_utils.PORT.

    Args:
      path          A URL path fragment (eg: /foo)
      prepend_lang  If True the value of hawkeye_utils.LANG will be
                    prepended to the provided URL path. Default is
                    True

    Returns:
      An instance of ResponseInfo
    """
    return self.__make_request('DELETE', path, prepend_lang=prepend_lang)

  def assert_and_get_list(self, path):
    """
    Executes a HTTP GET on the specified URL path and parse the output
    payload into a list of entities. Semantics of the GET request are
    similar to that of the http_get function of this class. Additionally
    this function also asserts that the resulting list has at least one
    element.

    Args:
      path  A URL path

    Returns:
      A list of entities

    Raises:
      AssertionError  If the resulting list is empty
    """
    response = self.http_get(path)
    self.assertEquals(response.status, 200)
    list = json.loads(response.payload)
    self.assertTrue(len(list) > 0)
    return list

  def __make_request(self, method, path, payload=None, headers=None,
                     prepend_lang=True, use_ssl=False):
    """
    Make a HTTP call using the provided arguments. HTTP request and response
    are traced and logged to hawkeye-logs/http.log.

    Args:
      method       HTTP method (eg: GET, POST)
      path         URL path to execute on
      payload      Payload to be sent. Only used if the method is POST or PUT
      headers      Any HTTP headers to be sent as a dictionary
      prepend_lang If True the value of hawkeye_utils.LANG will be prepended
                   to the URL
      use_ssl      If True use HTTPS to make the connection. Defaults to False.

    Returns:
      An instance of ResponseInfo
    """
    if prepend_lang:
      path = "/" + self.LANG + path
    response = self.app.logged_request(
      method, path, https=use_ssl, data=payload, headers=headers
    )
    response_info = ResponseInfo(response)
    return response_info


class HawkeyeConstants:
  PROJECT_SYNAPSE = 'Synapse'
  PROJECT_XERCES = 'Xerces'
  PROJECT_HADOOP = 'Hadoop'

  MOD_CORE = 'Core'
  MOD_NHTTP = 'NHTTP'
