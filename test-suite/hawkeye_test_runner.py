import csv
import logging
import unittest

logger = logging.getLogger(__name__)


class HawkeyeTestSuite(unittest.TestSuite):
  """
  Usual TestSuite but with name and short_name which are used by
  HawkeyeTestResult
  """

  def __init__(self, name, short_name, **kwargs):
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
    super(HawkeyeTestSuite, self).__init__(**kwargs)
    self.name = name
    self.short_name = short_name


class HawkeyeTestResult(unittest.TextTestResult):
  """
  """
  
  ERROR = "ERROR"
  FAILURE = "FAIL"
  SUCCESS = "ok"
  SKIP = "skip"
  EXPECTED_FAILURE = "expected-failure"
  UNEXPECTED_SUCCESS = "unexpected-success"

  def __init__(self, stream, descriptions, verbosity):
    super(HawkeyeTestResult, self).__init__(stream, descriptions, verbosity)
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



def save_report_dict_to_csv(result, file_name):
  """
  :param result: HawkeyeTestResult
  :param file_name:
  """
  with open(file_name, "w") as csv_file:
    csv_writer = csv.writer(csv_file)
    for test_id in sorted(result.report_dict.keys()):
      csv_writer.writerow((test_id, result.report_dict[test_id]))


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


class DiffToBaseline(object):
  def __init__(self):
    self.match_baseline = []   # tuples (test_id, status)
    self.do_not_match_baseline = []   # tuples (test_id, expected, actual)
    self.missed_in_current_test = []   # tuples (test_id, expected)
    self.missed_in_baseline = []   # tuples (test_id, actual)



def compare_test_reports(expected_report_dict, actual_report_dict):
  diff = DiffToBaseline()

  for test_id, expected in expected_report_dict.iteritems():
    # Check baseline tests
    actual = actual_report_dict.get(test_id)
    if actual == expected:
      diff.match_baseline.append((test_id, expected))
    elif actual is None:
      diff.missed_in_current_test.append((test_id, expected))
    elif actual != expected:
      diff.do_not_match_baseline.append((test_id, expected, actual))

  for test_id, actual in actual_report_dict.iteritems():
    # Find tests which are not presented in baseline
    if test_id not in expected_report_dict:
      diff.missed_in_baseline.append((test_id, actual))


class HawkeyeSuitesRunner(object):

  def __init__(self):
    # TODO
    pass

  def run_suites(self, hawkeye_suites):
    for suite in hawkeye_suites:
      logger.info(suite.name)   # Make formatting properly configured
      test_runner = unittest.TextTestRunner(resultclass=HawkeyeTestResult)
      test_runner.run(suite)
