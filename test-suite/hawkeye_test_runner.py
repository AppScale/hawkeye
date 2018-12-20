import csv
import inspect
import json
import sys
import traceback
import unittest

# We want to proceed nicely on systems that don't have termcolor installed.
try:
  from termcolor import cprint
except ImportError:
  sys.stderr.write('termcolor module not found\n')
  def cprint(msg, *args, **kwargs):
    """
    Fallback definition of cprint in case the termcolor module is not available.

    Args:
      msg: a str to be printed stdout.
      args: additional positional arguments for cprint that are ignored.
      kwargs: keyword arguments for cprint. It is ignored in dummy cprint.
    """
    print(msg)

from hawkeye_utils import logger, ResponseInfo


class HawkeyeTestCase(unittest.TestCase):
  """
  Extension of unittest.TestCase. It has `app` attribute for easy access to the
  tested application.
  """

  def __init__(self, methodName, application):
    """
    Args:
      methodName: A string representing test method name.
      application: An Application object. 
    """
    super(HawkeyeTestCase, self).__init__(methodName)
    self.app = application

  @classmethod
  def all_cases(cls, app):
    """
    Helper method which is used for building suites. It creates a list of
    test cases with specified `app` attribute. Test case is created for each
    method with name starting with 'test' or method with name 'runTest'.

    Args:
      app: An Application object to be passed to __init__ of HawkeyeTestCase.

    Returns:
      A list of instances of cls (an instance for each test method).
    """
    return [cls(method_name, app) for method_name in cls._cases_names()]

  @classmethod
  def _cases_names(cls):
    return [
      name for name, _ in inspect.getmembers(cls, predicate=inspect.ismethod)
      if name.startswith("test") or name == "runTest"
    ]


class HawkeyeTestSuite(unittest.TestSuite):
  """
  Usual TestSuite but with name and short_name which are used by hawkeye
  """

  def __init__(self, name, short_name, **kwargs):
    """
    Args:
      name: A descriptive name for the test suite.
      short_name: A shorter but unique name for the test suite.
        Should be ideally just one word. This short name is used to name
        log files and other command line options related to this
        test suite.
      kwargs: keyword arguments to be passed to super __init__.
    """
    super(HawkeyeTestSuite, self).__init__(**kwargs)
    self.name = name
    self.short_name = short_name


class HawkeyeTestResult(unittest.TextTestResult):
  """
  Like a usual unittest.TextTestResult but it writes logs to hawkeye logger
  and saves report to dictionary like:
  {
    "tests.search_tests.SearchTest.runTest": "ok",
    "tests.search_tests.GetRangeTest.test_default_limit": "FAIL",
    "tests.search_tests.GetTest.test_unknown_doc": "skip",
    "tests.search_tests.PutTest.test_invalid_id": "ERROR",
    ...
  }
  """

  ERROR = "ERROR"
  FAILURE = "FAIL"
  SUCCESS = "ok"
  SKIP = "skip"
  EXPECTED_FAILURE = "expected-failure"
  UNEXPECTED_SUCCESS = "unexpected-success"

  def __init__(self, stream, descriptions, verbosity):
    super(HawkeyeTestResult, self).__init__(stream, descriptions, verbosity)
    self.verbosity = verbosity
    self.report_dict = {}
    """
    Item of self.report_dict is pair of test IDs ('<class_name>.<method_name>')
     and test status (one of 'ERROR', 'ok', ...)
    """

  def startTest(self, test):
    super(HawkeyeTestResult, self).startTest(test)
    logger.info(
      "==========================================\n"
      "Starting {test_id}".format(test_id=test.id())
    )

  def addError(self, test, err):
    super(HawkeyeTestResult, self).addError(test, err)
    self.report_dict[test.id()] = self.ERROR
    logger.error("{test_id} - failed with error:\n{trace}"
                 .format(test_id=test.id(),
                         trace=self._render_cut_traceback(test, err)))

  def addFailure(self, test, err):
    super(HawkeyeTestResult, self).addFailure(test, err)
    self.report_dict[test.id()] = self.FAILURE
    logger.error("{test_id} - failed with error:\n{trace}"
                 .format(test_id=test.id(),
                         trace=self._render_cut_traceback(test, err)))

  def addSuccess(self, test):
    super(HawkeyeTestResult, self).addSuccess(test)
    self.report_dict[test.id()] = self.SUCCESS
    logger.debug("{test_id} - succeeded".format(test_id=test.id()))

  def addSkip(self, test, reason):
    super(HawkeyeTestResult, self).addSkip(test, reason)
    self.report_dict[test.id()] = self.SKIP
    logger.debug("{test_id} - skipped".format(test_id=test.id()))

  def addExpectedFailure(self, test, err):
    super(HawkeyeTestResult, self).addExpectedFailure(test, err)
    self.report_dict[test.id()] = self.EXPECTED_FAILURE
    logger.info("{test_id} - failed as expected".format(test_id=test.id()))

  def addUnexpectedSuccess(self, test):
    super(HawkeyeTestResult, self).addUnexpectedSuccess(test)
    self.report_dict[test.id()] = self.UNEXPECTED_SUCCESS
    logger.warn("{test_id} - unexpectedly succeeded"
                .format(test_id=test.id()))

  def printErrors(self):
    if self.verbosity > 1:
      super(HawkeyeTestResult, self).printErrors()
    else:
      self.stream.write("\n")

  def _render_cut_traceback(self, test, err):
    """
    Simplified modification of
    unittest.TestResult._exc_info_to_string(self, err, test).
    It renders only cut stacktrace of error.

    Args:
      test: A TestCase object.
      err: A tuple of exctype, value and tb.
    Returns:
      A string with stacktrace of error.
    """
    exctype, value, tb = err
    # Skip test runner traceback levels
    while tb and self._is_relevant_tb_level(tb):
      tb = tb.tb_next

    if exctype is test.failureException:
      # Skip assert*() traceback levels
      length = self._count_relevant_tb_levels(tb)
      msg_lines = traceback.format_exception(exctype, value, tb, length)
    else:
      msg_lines = traceback.format_exception(exctype, value, tb)

    return "".join(msg_lines)


def save_report_dict_to_csv(report_dict, file_name):
  """
  Persists dictionary to csv file in alphabetical order of keys.

  Args:
    report_dict: A dict with statuses of tests (<test_id>: <status>).
    file_name: A string - name of csv file where report should be saved.
  """
  with open(file_name, "w") as csv_file:
    csv_writer = csv.writer(csv_file)
    for test_id in sorted(report_dict.keys()):
      csv_writer.writerow((test_id, report_dict[test_id]))


def load_report_dict_from_csv(file_name):
  """
  Loads test statuses report from csv file.

  Args:
    file_name: A string representing name of source csv file.
  Returns:
    A dictionary with statuses of tests (<test_id>: <status>).
  """
  with open(file_name, "r") as csv_file:
    return {test_id: result for test_id, result in csv.reader(csv_file)}


class ReportsDiff(object):
  """
  Util class which defines structure for storing
  difference between test reports.
  """
  def __init__(self):
    self.match = []   # tuples (test_id, status)
    self.do_not_match = []   # tuples (test_id, first, second)
    self.missed_in_first = []   # tuples (test_id, second)
    self.missed_in_second = []   # tuples (test_id, first)


def compare_test_reports(first_report_dict, second_report_dict):
  """
  Compares two reports and returns ReportsDiff with detailed difference of
  two reports. Supposed to be used for comparison to baseline.

  Args:
    first_report_dict: A dict with statuses of tests (<test_id>: <status>)..
    second_report_dict: A dict with statuses of tests (<test_id>: <status>)..
  Returns:
    A ReportDiff with details about difference between 1st and 2nd reports..
  """
  diff = ReportsDiff()

  for test_id, first in first_report_dict.iteritems():
    # Check tests which are presented in the first report
    second = second_report_dict.get(test_id)
    if second == first:
      diff.match.append((test_id, first))
    elif second is None:
      diff.missed_in_second.append((test_id, first))
    elif second != first:
      diff.do_not_match.append((test_id, first, second))

  for test_id, second in second_report_dict.iteritems():
    # Find tests which are not presented in the first report
    if test_id not in first_report_dict:
      diff.missed_in_first.append((test_id, second))

  # Order lists by test_id
  diff.match = sorted(diff.match, key=lambda item: item[0])
  diff.do_not_match = sorted(diff.do_not_match, key=lambda item: item[0])
  diff.missed_in_first = sorted(diff.missed_in_first, key=lambda item: item[0])
  diff.missed_in_second = sorted(diff.missed_in_second, key=lambda item: item[0])

  return diff


class HawkeyeSuitesRunner(object):

  def __init__(self, language, logs_dir, baseline_file, verbosity=1):
    """
    Args:
      language: A string ('python' or 'java').
      logs_dir: A string - path to directory to save files with errors report.
      baseline_file: A string representing name of baseline file.
      verbosity: A flag. Is passed to TextTestRunner and HawkeyeTestResult.
        Defines how many details will be written to stdout.
    """
    self.language = language
    self.logs_dir = logs_dir
    self.baseline_file = baseline_file
    self.verbosity = verbosity
    self.suites_report = {}

  def run_suites(self, hawkeye_suites):
    """
    Iterates through hawkeye_suites and executes containing tests.
    For each failed suite file with error details is saved.
    Summarized report is built.

    Args:
      hawkeye_suites: A list of HawkeyeTestSuite objects.
    """
    for suite in hawkeye_suites:
      print("\n{}".format(suite.name))
      print("=" * len(suite.name))
      test_runner = unittest.TextTestRunner(resultclass=HawkeyeTestResult,
                                            verbosity=self.verbosity,
                                            stream=sys.stdout)
      result = test_runner.run(suite)
      """:type result: HawkeyeTestResult """

      self.suites_report.update(result.report_dict)
      if result.errors or result.failures:
        self._save_error_details(suite.short_name, result)

  ERR_TEMPLATE = (
    "======================================================================\n"
    "{flavour}: {test_id}\n"
    "----------------------------------------------------------------------\n"
    "{error}\n"
  )

  def _save_error_details(self, suite_short_name, text_test_result):
    """
    Saves error details (related to specific suite)
    to a file in logs directory.

    Args:
      suite_short_name: A string - short name of HawkeyeTestSuite.
      text_test_result: A HawkeyeTestResult object - test result with errors.
    """
    error_details_file = "{logs_dir}/{suite}-{lang}-errors.log".format(
      logs_dir=self.logs_dir, suite=suite_short_name, lang=self.language)
    with open(error_details_file, "w") as error_log:
      error_log.writelines((
        self.ERR_TEMPLATE.format(flavour="ERROR", test_id=test.id(), error=err)
        for test, err in text_test_result.errors
      ))
      error_log.writelines((
        self.ERR_TEMPLATE.format(flavour="FAIL", test_id=test.id(), error=err)
        for test, err in text_test_result.failures
      ))

  def print_summary(self, verbosity):
    """
    Prints comparison to baseline.

    Args:
      verbosity: An integer - if > 1 details about difference is printed.
    """
    baseline_report = load_report_dict_from_csv(self.baseline_file)
    diff = compare_test_reports(baseline_report, self.suites_report)

    # Specify output styles depending on success or failure
    if diff.do_not_match:
      matched_style = None
      different_style = ["bold"]
    else:
      matched_style = ["bold"]
      different_style = None

    # Print summary with nice formatting
    cprint("\nComparison to baseline:", attrs=["bold"])
    cprint(" {match:<3} tests matched baseline result"
      .format(match=len(diff.match)), "green", attrs=matched_style)

    cprint(" {different:<3} tests did not match baseline result"
      .format(different=len(diff.do_not_match)), "red", attrs=different_style)
    if verbosity > 1 and diff.do_not_match:
      # Optionally print details about test which do not match baseline
      different = "\n    ".join((
        "{} ... {} ({} was expected)".format(test_id, actual, expected)
        for test_id, expected, actual in diff.do_not_match
      ))
      cprint("    " + different, color="red")

    cprint(" {missed_in_baseline:<3} tests ran, but not found in baseline"
      .format(missed_in_baseline=len(diff.missed_in_first)), attrs=["bold"])
    if verbosity > 1 and diff.missed_in_first:
      # Optionally print details about test which are missed in baseline
      missed_in_baseline = "\n    ".join((
        "{} ... {}".format(test_id, actual)
        for test_id, actual in diff.missed_in_first
      ))
      cprint("    " + missed_in_baseline)

    cprint(" {missed_in_suites:<3} tests in baseline, but not ran"
      .format(missed_in_suites=len(diff.missed_in_second)), attrs=["bold"])
    if verbosity > 1 and diff.missed_in_second:
      # Optionally print details about test which are missed in test suites
      missed_in_suites = "\n    ".join((
        "{} ... {}".format(test_id, expected)
        for test_id, expected in diff.missed_in_second
      ))
      cprint("    " + missed_in_suites)


class DeprecatedHawkeyeTestCase(HawkeyeTestCase):
  """
  This DEPRECATED abstract class provides a skeleton to implement actual
  Hawkeye test cases. To implement a test case, this class must
  be extended by providing an implementation for the runTest
  method. Use the http_* methods to perform HTTP calls on backend
  endpoints. All the HTTP calls performed via these methods are
  traced and logged to hawkeye-logs/<lang>-detailed <datetime>.log.
  """
  LANG = None

  def __init__(self, methodName, application):
    """
    Args:
      methodName: A string representing name of test method (e.g.: "runTest").
      application: An Application object.
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
    Perform a HTTP GET request on the specified URL path using Application
    object provided by new HawkeyeTestCase.

    Args:
      path: A URL path fragment (eg: /foo).
      headers: A dictionary to be sent as HTTP headers.
      prepend_lang: If True the value of hawkeye_utils.LANG will be
        prepended to the provided URL path. Default is : .
      use_ssl: If True use HTTPS to make the connection. Defaults to False.

    Returns:
      An instance of ResponseInfo.
    """
    return self.__make_request('GET', path, headers=headers,
      prepend_lang=prepend_lang, use_ssl=use_ssl, **kwargs)

  def http_post(self, path, payload, headers=None, prepend_lang=True, **kwargs):
    """
    Perform a HTTP POST request on the specified URL path using Application
    object provided by new HawkeyeTestCase. If a content-type header is not set
    defaults to 'application/x-www-form-urlencoded' content type.

    Args:
      path: A URL path fragment (eg: /foo).
      payload: A string payload to be sent POSTed.
      headers: A dictionary of headers.
      prepend_lang: If True the value of hawkeye_utils.LANG will be
        prepended to the provided URL path. Default is True.

    Returns:
      An instance of ResponseInfo.
    """
    if headers is None:
      headers = { 'Content-Type' : 'application/x-www-form-urlencoded' }
    elif 'Content-Type' not in headers:
      headers['Content-Type'] = 'application/x-www-form-urlencoded'
    return self.__make_request('POST', path, payload, headers=headers,
      prepend_lang=prepend_lang, **kwargs)

  def http_put(self, path, payload, headers=None, prepend_lang=True, **kwargs):
    """
    Perform a HTTP PUT request on the specified URL path using Application
    object provided by new HawkeyeTestCase. If a content-type header is not set
    defaults to 'application/x-www-form-urlencoded' content type.

    Args:
      path: A URL path fragment (eg: /foo).
      payload: A string payload to be sent POSTed.
      headers: A dictionary of headers.
      prepend_lang: If True the value of hawkeye_utils.LANG will be
        prepended to the provided URL path. Default is True.

    Returns:
      An instance of ResponseInfo.
    """
    if headers is None:
      headers = { 'Content-Type' : 'application/x-www-form-urlencoded' }
    elif 'Content-Type' not in headers:
      headers['Content-Type'] = 'application/x-www-form-urlencoded'
    return self.__make_request('PUT', path, payload, headers=headers,
      prepend_lang=prepend_lang, **kwargs)

  def http_delete(self, path, prepend_lang=True, **kwargs):
    """
    Perform a HTTP DELETE request on the specified URL path using Application
    object provided by new HawkeyeTestCase.

    Args:
      path: A URL path fragment (eg: /foo).
      prepend_lang: If True the value of hawkeye_utils.LANG will be
        prepended to the provided URL path. Default is True.

    Returns:
      An instance of ResponseInfo.
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
      path: A URL path.

    Returns:
      A list of entities.

    Raises:
      AssertionError  If the resulting list is empty.
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
    are traced and logged to hawkeye-logs/<lang>-detailed <datetime>.log.

    Args:
      method: HTTP method (eg: GET, POST).
      path: URL path to execute on.
      payload: Payload to be sent. Only used if the method is POST or PUT.
      headers: Any HTTP headers to be sent as a dictionary.
      prepend_lang: If True the value of hawkeye_utils.LANG will be prepended
        to the URL.
      use_ssl: If True use HTTPS to make the connection. Defaults to False.

    Returns:
      An instance of ResponseInfo.
    """
    if prepend_lang:
      path = "/" + self.LANG + path
    response = self.app.request(
      method, path, https=use_ssl, data=payload, headers=headers, **kwargs
    )
    response_info = ResponseInfo(response)
    return response_info
