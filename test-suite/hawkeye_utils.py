import httplib
import json
from unittest.case import TestCase
from unittest.runner import TextTestResult, TextTestRunner
from unittest.suite import TestSuite
import sys

__author__ = 'hiranya'

HOST = None
PORT = -1
LANG = None

class HawkeyeTestCase(TestCase):

  def __init__(self):
    TestCase.__init__(self)
    self.description_printed = False

  def http_get(self, path):
    return self.__make_request('GET', path)

  def http_post(self, path, payload):
    return self.__make_request('POST', path, payload)

  def http_delete(self, path):
    return self.__make_request('DELETE', path)

  def assert_and_get_list(self, path):
    status, headers, payload = self.http_get(path)
    self.assertEquals(status, 200)
    list = json.loads(payload)
    self.assertTrue(len(list) > 0)
    return list

  def __make_request(self, method, path, payload=None):
    http_log = open('logs/http.log', 'a')
    if not self.description_printed:
      http_log.write('\n' + str(self) + '\n')
      http_log.write('=' * 70)
      self.description_printed = True

    original = sys.stdout
    sys.stdout = http_log
    print
    path = "/" + LANG + path
    conn = httplib.HTTPConnection(HOST + ':' + str(PORT))
    conn.set_debuglevel(1)
    if method == 'POST' or method == 'PUT':
      conn.request(method, path, payload)
      print 'req-body: ' + payload
    else:
      conn.request(method, path)
    response = conn.getresponse()
    status, headers, payload = response.status, response.getheaders(), response.read()
    conn.close()
    if payload is not None and len(payload) > 0:
      print 'resp-body: ' + payload
    sys.stdout = original
    http_log.close()
    return status, headers, payload

class HawkeyeTestSuite(TestSuite):
  def __init__(self, name, short_name):
    TestSuite.__init__(self)
    self.name = name
    self.short_name = short_name

class HawkeyeTestResult(TextTestResult):
  def __init__(self, stream, descriptions, verbosity, suite):
    TextTestResult.__init__(self, stream, descriptions, verbosity)
    self.suite = suite

  def printErrors(self):
    if self.dots or self.showAll:
      self.stream.writeln()
    self.printErrorInfo('ERROR', self.errors, False)
    self.printErrorInfo('FAIL', self.failures, True)

  def printErrorInfo(self, flavour, errors, append):
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

class HawkeyeTestRunner(TextTestRunner):
  def __init__(self, suite):
    TextTestRunner.__init__(self, verbosity=2)
    self.suite = suite
    self.stream.writeln('\n' + suite.name)
    self.stream.writeln('=' * len(suite.name))

  def run_suite(self):
    self.run(self.suite)

  def _makeResult(self):
    return HawkeyeTestResult(self.stream, self.descriptions, self.verbosity, self.suite.short_name)

class HawkeyeConstants:
  PROJECT_SYNAPSE = 'Synapse'
  PROJECT_XERCES = 'Xerces'
  PROJECT_HADOOP = 'Hadoop'

  MOD_CORE = 'Core'
  MOD_NHTTP = 'NHTTP'