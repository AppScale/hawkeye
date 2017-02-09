import httplib
import json
import os
import ssl
import sys

from unittest.case import TestCase
from unittest.runner import TextTestResult, TextTestRunner

HOST = None
PORT = -1
LANG = None
CONSOLE_MODE = False

SSL_PORT_OFFSET = 3700

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
    self.status = response.status
    self.headers = {}
    for header in response.getheaders():
      self.headers[header[0]] = header[1]
    self.payload = response.read()

class HawkeyeTestCase(TestCase):
  """
  This abstract class provides a skeleton to implement actual
  Hawkeye test cases. To implement a test case, this class must
  be extended by providing an implementation for the runTest
  method. Use the http_* methods to perform HTTP calls on backend
  endpoints. All the HTTP calls performed via these methods are
  traced and logged to hawkeye-logs/http.log.
  """

  def __init__(self, log_base_dir=None):
    """Create a new instance of HawkeyeTestCase.

    Args:
      log_base_dir: A str indicating the directory the logs should be stored in.
    """
    TestCase.__init__(self)
    self.description_printed = False
    if log_base_dir is None:
      if 'LOG_BASE_DIR' in os.environ:
        self.log_base_dir = os.environ['LOG_BASE_DIR']
      else:
        self.log_base_dir = 'logs'
    else:
      self.log_base_dir = log_base_dir

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

  def file_upload(self, path, payload, headers, prepend_lang=False):
    """
    Perform a HTTP POST request on the specified URL path and uploads
    the specified payload as a HTTP form based file upload..
    The hostname and port segments of the URL are inferred from
    the values of the 2 constants hawkeye_utils.HOST and
    hawkeye_utils.PORT.

    Args:
      path          A URL path fragment (eg: /foo)
      payload       Payload string content to be uploaded
      headers       A dictionary to be sent as HTTP headers
      prepend_lang  If True the value of hawkeye_utils.LANG will be
                    prepended to the provided URL path. Default is
                    False.

    Returns:
      An instance of ResponseInfo
    """
    return self.__make_request('POST', path, payload, headers, prepend_lang)

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
    http_log = open('{0}/http-{1}.log'.format(self.log_base_dir, LANG), 'a')
    if not self.description_printed:
      http_log.write('\n' + str(self) + '\n')
      http_log.write('=' * 70)
      self.description_printed = True

    original = sys.stdout
    sys.stdout = http_log
    try:
      print
      if prepend_lang:
        path = "/" + LANG + path
      if use_ssl:
        try:
          conn = httplib.HTTPSConnection(
            HOST + ':' + str(PORT - SSL_PORT_OFFSET),
            context=ssl._create_unverified_context())
        except AttributeError:
          conn = httplib.HTTPSConnection(
            HOST + ':' + str(PORT - SSL_PORT_OFFSET))
      else:
        conn = httplib.HTTPConnection(HOST + ':' + str(PORT))
      conn.set_debuglevel(1)
      if method == 'POST' or method == 'PUT':
        if headers is not None:
          conn.request(method, path, payload, headers)
        else:
          conn.request(method, path, payload)
        print 'req-body: ' + payload
      else:
        if headers is not None:
          conn.request(method, path, headers=headers)
        else:
          conn.request(method, path)
      response = conn.getresponse()
      response_info = ResponseInfo(response)
      conn.close()
      if response_info.payload is not None and len(response_info.payload) > 0:
        print 'resp-body: ' + response_info.payload
      return response_info
    finally:
      sys.stdout = original
      http_log.close()


class HawkeyeConstants:
  PROJECT_SYNAPSE = 'Synapse'
  PROJECT_XERCES = 'Xerces'
  PROJECT_HADOOP = 'Hadoop'

  MOD_CORE = 'Core'
  MOD_NHTTP = 'NHTTP'


def encode (file_name, content):
  """
  Encode the specified file name and content payload into a HTTP
  file upload request.

  Args:
    file_name Name of the file
    content   String payload to be uploaded

  Returns:
    A HTTP multipart form request encoded payload string
  """

  # Thanks Pietro Abate for the helpful post at:
  # http://mancoosi.org/~abate/upload-file-using-httplib
  boundary = '----------boundary------'
  delimiter = '\r\n'
  body = []
  body.extend(
    ['--' + boundary,
     'Content-Disposition: form-data; name="file"; filename="%s"'
     % file_name,
     # The upload server determines the mime-type, no need to set it.
     'Content-Type: application/octet-stream',
     '',
     content,
     ])
  # Finalize the form body
  body.extend(['--' + boundary + '--', ''])
  return 'multipart/form-data; boundary=%s' % boundary, delimiter.join(body)

def encode_file(file_path):
  file_data = open(file_path, 'rb')
  content = file_data.read()
  file_data.close()
  return encode(os.path.basename(file_path), content)
