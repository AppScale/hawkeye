import httplib
import json
import os
import sys
from unittest.case import TestCase
from unittest.runner import TextTestResult, TextTestRunner
from unittest.suite import TestSuite

__author__ = 'hiranya'

HOST = None
PORT = -1
LANG = None
CONSOLE_MODE = False
USER_EMAIL = 'a@a.a'
USER_PASSWORD = 'aaaaaa'

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
  traced and logged to logs/http.log.
  """

  def __init__(self):
    """
    Create a new instance of HawkeyeTestCase.
    """
    TestCase.__init__(self)
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

  def http_get(self, path, headers=None, prepend_lang=True):
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
                    True

    Returns:
      An instance of ResponseInfo
    """
    return self.__make_request('GET', path, headers=headers,
      prepend_lang=prepend_lang)

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
                     prepend_lang=True):
    """
    Make a HTTP call using the provided arguments. HTTP request and response
    are traced and logged to logs/http.log.

    Args:
      method  HTTP method (eg: GET, POST)
      path    URL path to execute on
      payload Payload to be sent. Only used if the method is POST or PUT
      headers Any HTTP headers to be sent as a dictionary
      prepend_lang If True the value of hawkeye_utils.LANG will be prepended
                    to the URL

    Returns:
      An instance of ResponseInfo
    """
    http_log = open('logs/http.log', 'a')
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

class HawkeyeTestSuite(TestSuite):
  """
  A collection of test cases that can be executed as a single atomic
  unit. Each test suite is identified by a unique identifier (short name)
  and a more detailed long name attribute. HawkeyeTestSuite logs the
  results of each test case to console in the least verbose manner possible.
  In case of test failures and errors, the error details and stack traces are
  logged to logs/{short_name}.log. If required the suite can be configured to
  log this information to the console as well.
  """

  def __init__(self, name, short_name):
    """
    Create a new instance of HawkeyeTestSuite with the given name and short
    name. Use the addTest instance method to add test cases to the suite.

    Args:
      name  A descriptive name for the test suite
      short_name  A shorter but unique name for the test suite. Should be
                  ideally just one word. This short name is used to name
                  log files and other command line options related to this
                  test suite.
    """
    TestSuite.__init__(self)
    self.name = name
    self.short_name = short_name

class HawkeyeTestResult(TextTestResult):
  """
  A collection of test results generated by a suite of test cases.
  This class is primarily responsible for collecting all the test
  results and any errors as a suite is being executed and then finally
  log it to the console and the file system. This class by default logs
  all failures and errors to the file system. If hawkeye_utils.CONSOLE_MODE
  is set to True this class will also log error details to the console.
  Also see the documentation of unittest.TextTestResult class.
  """

  def __init__(self, stream, descriptions, verbosity, suite):
    """
    Create a new instance to gather and log the results of the specified
    test suite.

    Args:
      stream        Standard output stream
      descriptions  A list of test case descriptions
      verbosity     An integer describing the required verbosity
      suite         The associated HawkeyeTestSuite instance
    """
    TextTestResult.__init__(self, stream, descriptions, verbosity)
    self.suite = suite

  def printErrors(self):
    if self.dots or self.showAll:
      self.stream.writeln()
    self.print_error_info('ERROR', self.errors, False)
    self.print_error_info('FAIL', self.failures, True)

  def print_error_info(self, flavour, errors, append):
    """
    Log the errors and failures to the file system. Optionally,
    if the hawkeye_utils.CONSOLE_MODE is set to True, will log
    the same information to the console as well.

    Args:
      flavour Type of information to log (eg: 'ERROR', 'FAIL')
      errors  The list of errors to log
      append  Whether to append the information to the current log file
              or to create a new log file
    """
    if not errors:
      return

    if append:
      mode = 'a'
    else:
      mode = 'w'
    error_log = open('logs/{0}-errors.log'.format(self.suite), mode)
    for test, err in errors:
      error_log.write(self.separator1)
      error_log.write('\n')
      error_log.write("%s: %s" % (flavour,self.getDescription(test)))
      error_log.write('\n')
      error_log.write(self.separator2)
      error_log.write('\n')
      error_log.write("%s" % err)
      error_log.write('\n')
    error_log.flush()
    error_log.close()

    if CONSOLE_MODE:
      for test, err in errors:
        self.stream.write(self.separator1)
        self.stream.write('\n')
        self.stream.write("%s: %s" % (flavour,self.getDescription(test)))
        self.stream.write('\n')
        self.stream.write(self.separator2)
        self.stream.write('\n')
        self.stream.write("%s" % err)
        self.stream.write('\n')
      self.stream.flush()

class HawkeyeTestRunner(TextTestRunner):
  """
  An extension of unittest.TextTestRunner that keeps the console output
  clean and less verbose while logging all the failures and error details
  to a separate log file in the logs directory.
  """

  def __init__(self, suite):
    """
    Create a new instance of the test runner for the given test suite.

    Args:
      suite An instance of HawkeyeTestSuite class
    """

    TextTestRunner.__init__(self, verbosity=2)
    self.suite = suite
    self.stream.writeln('\n' + suite.name)
    self.stream.writeln('=' * len(suite.name))

  def run_suite(self):
    """
    Run the child test suite and print the outcome to console and relevant
    log files.
    """
    if self.suite.countTestCases() > 0:
      self.run(self.suite)
    else:
      self.stream.writeln('No test cases for {0} API - SKIPPING'.format(LANG))

  def _makeResult(self):
    return HawkeyeTestResult(self.stream, self.descriptions,
      self.verbosity, self.suite.short_name)

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