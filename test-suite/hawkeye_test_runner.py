import csv
import sys
import unittest

# We want to proceed nicely on systems that don't have termcolor installed.
try:
  from termcolor import cprint
except ImportError:
  sys.stderr.write('termcolor module not found\n')
  def cprint(msg, **kwargs):
    """
    Fallback definition of cprint in case the termcolor module is not available.
    :param msg: string to be printed stdout.
    :param kwargs: arguments for cprint. It is ignored.
    """
    print msg


class HawkeyeTestSuite(unittest.TestSuite):
  """
  Usual TestSuite but with name and short_name which are used by hawkeye
  """

  def __init__(self, name, short_name, **kwargs):
    """
    :param name: A descriptive name for the test suite
    :param short_name: A shorter but unique name for the test suite.
             Should be ideally just one word. This short name is used to name
             log files and other command line options related to this
             test suite.
    """
    super(HawkeyeTestSuite, self).__init__(**kwargs)
    self.name = name
    self.short_name = short_name


class HawkeyeTestResult(unittest.TextTestResult):
  """
  Like a usual unittest.TextTestResult but saves report to dictionary like:
  {
    "tests.search_tests.SearchTest.runTest": "ok",
    "tests.search_tests.GetRangeTest": "FAIL",
    "tests.search_tests.GetTest": "skip",
    "tests.search_tests.PutTest": "ERROR",
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

  def addError(self, test, err):
    super(HawkeyeTestResult, self).addError(test, err)
    self.report_dict[test.id()] = self.ERROR

  def addFailure(self, test, err):
    super(HawkeyeTestResult, self).addFailure(test, err)
    self.report_dict[test.id()] = self.FAILURE

  def addSuccess(self, test):
    super(HawkeyeTestResult, self).addSuccess(test)
    self.report_dict[test.id()] = self.SUCCESS

  def addSkip(self, test, reason):
    super(HawkeyeTestResult, self).addSkip(test, reason)
    self.report_dict[test.id()] = self.SKIP

  def addExpectedFailure(self, test, err):
    super(HawkeyeTestResult, self).addExpectedFailure(test, err)
    self.report_dict[test.id()] = self.EXPECTED_FAILURE

  def addUnexpectedSuccess(self, test):
    super(HawkeyeTestResult, self).addUnexpectedSuccess(test)
    self.report_dict[test.id()] = self.UNEXPECTED_SUCCESS

  def printErrors(self):
    if self.verbosity > 1:
      super(HawkeyeTestResult, self).printErrors()
    else:
      self.stream.write("\n")


def save_report_dict_to_csv(report_dict, file_name):
  """
  :param report_dict:
  :param file_name:
  """
  with open(file_name, "w") as csv_file:
    csv_writer = csv.writer(csv_file)
    for test_id in sorted(report_dict.keys()):
      csv_writer.writerow((test_id, report_dict[test_id]))


def load_report_dict_from_csv(file_name):
  with open(file_name, "r") as csv_file:
    return {test_id: result for test_id, result in csv.reader(csv_file)}


ERR_TEMPLATE = (
  "======================================================================\n"
  "{flavour}: {test_id}\n"
  "----------------------------------------------------------------------\n"
  "{error}\n"
)


def save_error_details(text_test_result, file_name):
  with open(file_name, "w") as error_log:
    error_log.writelines((
      ERR_TEMPLATE.format(flavour="ERROR", test_id=test.id(), error=err)
      for test, err in text_test_result.errors
    ))
    error_log.writelines((
      ERR_TEMPLATE.format(flavour="FAIL", test_id=test.id(), error=err)
      for test, err in text_test_result.failures
    ))


class ReportsDiff(object):
  def __init__(self):
    self.match = []   # tuples (test_id, status)
    self.do_not_match = []   # tuples (test_id, first, second)
    self.missed_in_first = []   # tuples (test_id, second)
    self.missed_in_second = []   # tuples (test_id, first)


def compare_test_reports(first_report_dict, second_report_dict):
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
    :param logs_dir: Directory to save files with errors report
    :param verbosity: integer
    """
    self.language = language
    self.logs_dir = logs_dir
    self.baseline_file = baseline_file
    self.verbosity = verbosity
    self.suites_report = {}

  def run_suites(self, hawkeye_suites):

    for suite in hawkeye_suites:
      print "\n{}".format(suite.name)
      test_runner = unittest.TextTestRunner(resultclass=HawkeyeTestResult,
                                            verbosity=self.verbosity)
      result = test_runner.run(suite)
      """:type result: HawkeyeTestResult """

      self.suites_report.update(result.report_dict)

      if result.errors or result.failures:
        error_details_file = "{logs_dir}/{suite}-{lang}-errors.log".format(
          logs_dir=self.logs_dir, suite=suite.short_name, lang=self.language)
        save_error_details(result, error_details_file)

  def print_summary(self, verbose):
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

    cprint(" {different:<3} tests didn't match baseline result"
      .format(different=len(diff.do_not_match)), "red", attrs=different_style)
    if verbose and diff.do_not_match:
      # Optionally print details about test which do not match baseline
      different = "\n    ".join((
        "{} ... {} ({} was expected)".format(test_id, actual, expected)
        for test_id, expected, actual in diff.do_not_match
      ))
      cprint("    " + different, color="red")

    cprint(" {missed_in_baseline:<3} tests ran, but not found in baseline"
      .format(missed_in_baseline=len(diff.missed_in_first)), attrs=["bold"])
    if verbose and diff.missed_in_first:
      # Optionally print details about test which are missed in baseline
      missed_in_baseline = "\n    ".join((
        "{} ... {}".format(test_id, actual)
        for test_id, actual in diff.missed_in_first
      ))
      cprint("    " + missed_in_baseline)

    cprint(" {missed_in_suites:<3} tests in baseline, but not ran"
      .format(missed_in_suites=len(diff.missed_in_second)), attrs=["bold"])
    if verbose and diff.missed_in_second:
      # Optionally print details about test which are missed in test suites
      missed_in_suites = "\n    ".join((
        "{} ... {}".format(test_id, expected)
        for test_id, expected in diff.missed_in_second
      ))
      cprint("    " + missed_in_suites)