import json
import logging
import os
from datetime import datetime

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from hawkeye_test_runner import HawkeyeTestCase

LIMITED_BODY_LENGTH = 200


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
    self.payload = response.text


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

  def __init__(self, methodName, application):
    """
    Args:
      application: Application object
    """
    super(DeprecatedHawkeyeTestCase, self).__init__(methodName, application)
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

  def http_get(self, path, headers=None, prepend_lang=True,
               use_ssl=False, **kwargs):
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
      prepend_lang=prepend_lang, use_ssl=use_ssl, **kwargs)

  def http_post(self, path, payload, headers=None, prepend_lang=True, **kwargs):
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
    elif 'Content-Type' not in headers:
      headers['Content-Type'] = 'application/x-www-form-urlencoded'
    return self.__make_request('POST', path, payload, headers=headers,
      prepend_lang=prepend_lang, **kwargs)

  def http_put(self, path, payload, headers=None, prepend_lang=True, **kwargs):
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
    elif 'Content-Type' not in headers:
      headers['Content-Type'] = 'application/x-www-form-urlencoded'
    return self.__make_request('PUT', path, payload, headers=headers,
      prepend_lang=prepend_lang, **kwargs)

  def http_delete(self, path, prepend_lang=True, **kwargs):
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
    return self.__make_request(
      'DELETE', path, prepend_lang=prepend_lang, **kwargs)

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
                     prepend_lang=True, use_ssl=False, **kwargs):
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
      method, path, https=use_ssl, data=payload, headers=headers, **kwargs
    )
    response_info = ResponseInfo(response)
    return response_info


class HawkeyeConstants:
  PROJECT_SYNAPSE = 'Synapse'
  PROJECT_XERCES = 'Xerces'
  PROJECT_HADOOP = 'Hadoop'

  MOD_CORE = 'Core'
  MOD_NHTTP = 'NHTTP'


def hawkeye_request(method, url, params=None, verbosity=2, verify=False,
                    allow_redirects=False, **kwargs):
  """
  Wrapper of requests.request. It writes logs about request sent and
  response received. It also sets default value of `verify` and `allow_redirects`
  to False
  :param method: string name of http method
  :param url: string URL
  :param params: a dict with query-string params
  :param verbosity: 0 - don't write logs
                    1 - log only request URL and response status
                    2 - log request and response without body
                    3 - add limited body
                    4 - write full request and response with full body
  :param verify:
  :param allow_redirects:
  :param kwargs:
  :return:
  """
  try:
    resp = requests.request(
      method, url, params=params, verify=verify,
      allow_redirects=allow_redirects, **kwargs
    )
    # Use real request which was sent by requests lib
    request_headers = resp.request.headers
    request_body = resp.request.body
  except:
    # Okay. Try to recover request which was tried to be sent by requests lib
    request_headers = kwargs.get("headers")
    if "data" in kwargs and verbosity > 2:
      request_body = kwargs.get("data")
    elif "json" in kwargs and verbosity > 2:
      request_body = json.dumps(kwargs.get("json"))
    elif "files" in kwargs and verbosity > 2:
      request_body = "LOGGING STUB: Files are here"
    else:
      request_body = None
    raise
  finally:
    # Anyway log request
    _log_request(method, url, request_headers, request_body, verbosity)
  _log_response(resp.status_code, url, resp.headers, resp.content, verbosity)
  return resp


def _log_request(method, url, headers, body, verbosity):
  if verbosity < 1:
    return
  if verbosity == 1:
    return logger.info(
      "Request: {method} {url}".format(method=method.upper(), url=url)
    )
  # More verbose message will contain headers
  header_lines = "\n".join([
    "{header}: {value}".format(header=name, value=value)
    for name, value in headers.iteritems()
  ])
  if verbosity == 2:
    return logger.info(
      "Request: {method} {url}\n{headers}"
      .format(method=method.upper(), url=url, headers=header_lines)
    )
  if verbosity == 3:
    body = body[:LIMITED_BODY_LENGTH] if body else ""
  else:
    body = body or ""
  logger.info(
    "Sending request:\n{method} {url}\n{headers}\n\n{body}"
    .format(method=method.upper(), url=url, headers=header_lines, body=body)
  )


def _log_response(status, url, headers, content, verbosity):
  if verbosity < 1:
    return
  if verbosity == 1:
    return logger.info(
      "Response: {status} {url}".format(status=status, url=url)
    )
  # More verbose message will contain headers
  header_lines = "\n".join([
    "{header}: {value}".format(header=name, value=value)
    for name, value in headers.iteritems()
  ])
  if verbosity == 2:
    return logger.info(
      "Response: {status} {url}\n{headers}"
      .format(status=status, url=url, headers=header_lines)
    )
  if verbosity == 3:
    content = content[:LIMITED_BODY_LENGTH] if content else ""
  else:
    content = content or ""
  logger.info(
    "Sending request:\n{method} {url}\n{headers}\n\n{content}"
    .format(method=status, url=url, headers=header_lines, content=content)
  )


def configure_hawkeye_logging(hawkeye_logs_dir, language):
  """
  This function configures hawkeye logger and loggers of some libraries
  to write relevant logs to specific log file located in
  hawkeye_logs_dir.
  Hawkeye logs written by logging framework in contrast to those logs
  which are written manually to report files are aimed to collect debug
  information which can help to understand unexpected failure of testcase.

  Args:
    hawkeye_logs_dir: a string - path to hawkeye logs directory
    language: a string - name of currently testing language
  """
  # Configure simple formatter
  formatter = logging.Formatter("%(levelname)s %(name)s %(message)s")

  # Configure file handler
  file_name = (
    "{lang}-detailed {dt:%Y-%m-%d %H-%M-%S}.log"
    .format(lang=language, dt=datetime.now())
  )
  file_path = os.path.join(hawkeye_logs_dir, file_name)
  handler = logging.FileHandler(file_path)
  handler.setFormatter(formatter)
  handler.setLevel(logging.DEBUG)

  # Configure hawkeye logger
  logger.addHandler(handler)
  logger.setLevel(logging.DEBUG)

  # Other loggers
  requests_logger = logging.getLogger("requests")
  requests_logger.addHandler(handler)
  requests_logger.setLevel(logging.WARN)
  requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


logger = logging.getLogger("hawkeye")