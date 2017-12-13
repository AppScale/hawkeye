#!/usr/bin/python2.7
"""hawkeye.py: Run API fidelity tests on AppScale.

Usage:
  hawkeye.py --app APP_ID --versions-csv FILE [options]
  hawkeye.py (-h | --help)

Options:
  -h, --help           # show this help message and exit
  --app                # Application ID to test
  --versions-csv FILE  # File containing http and https URL to app versions
  -l LANG --lang=LANG  # Language binding to test (python or java) [default: python]
  --user=USER          # Admin username [default: a@a.com]
  --pass=PASSWORD      # Admin password [default: aaaaaa]
  -c, --console        # Log errors and failures to console
  --suites=SUITES      # A comma separated list of suites to run
  --exclude-suites=EXCLUDE_SUITES # A comma separated list of suites to exclude
  --baseline           # Turn on verbose reporting for baseline comparison
  --log-dir=BASE_DIR   # Directory to store error logs
  --keep-old-logs      # Keep existing hawkeye logs
"""
import csv
import os
import sys

import docopt

import hawkeye_utils
from application import Application, AppURLBuilder
from application_versions import AppVersion
from hawkeye_test_runner import HawkeyeSuitesRunner, save_report_dict_to_csv, \
  DeprecatedHawkeyeTestCase

if not sys.version_info[:2] > (2, 6):
  raise RuntimeError("Hawkeye will only run with Python 2.7 or newer.")

from tests import (
  datastore_tests, ndb_tests, memcache_tests, taskqueue_tests, blobstore_tests,
  user_tests, images_tests, secure_url_tests, xmpp_tests,
  environment_variable_tests, async_datastore_tests, cron_tests,
  logservice_tests, modules_tests, urlfetch_tests
)

SUPPORTED_LANGUAGES = ['java', 'python']


def build_suites_list(lang, include, exclude, application):
  """
  Based on language, include and exclude filters, build list of
  HawkeyeTestSuite objects.

  Args:
    lang: A string representing language to test ('python' or 'java').
    include: A list of str - suites to return (use empty list to include all).
    exclude: A list of str - suites to skip
      ('exclude' is ignored if 'include' is specified).
    application: An Application object - wraps requests library and provides
      api for access to testing AppEngine application.

  Returns:
    a list of HawkeyeTestSuite for specified language.
  """
  defined_suites  = {
    'blobstore' : blobstore_tests.suite(lang, application),
    'datastore' : datastore_tests.suite(lang, application),
    'async_datastore' : async_datastore_tests.suite(lang, application),
    'env_var' : environment_variable_tests.suite(lang, application),
    'images' : images_tests.suite(lang, application),
    'memcache' : memcache_tests.suite(lang, application),
    'ndb' : ndb_tests.suite(lang, application),
    'secure_url' : secure_url_tests.suite(lang, application),
    'taskqueue' : taskqueue_tests.suite(lang, application),
    'urlfetch': urlfetch_tests.suite(lang, application),
    'users' : user_tests.suite(lang, application),
    'xmpp' : xmpp_tests.suite(lang, application),
    'cron' : cron_tests.suite(lang, application),
    'logservice': logservice_tests.suite(lang, application),
    'modules' : modules_tests.suite(lang, application),
  }
  # Validation include and exclude lists
  for suite_name in include + exclude:
    if suite_name not in defined_suites:
      print_usage_and_exit("Unknown suite '{}'. Suite can be one of {}"
                           .format(suite_name, defined_suites.keys()))

  if include:
    suites = [suite for suite_name, suite in defined_suites.iteritems()
              if suite_name in include]
  else:
    suites = [suite for suite_name, suite in defined_suites.iteritems()
              if suite_name not in exclude]

  if not suites:
    print_usage_and_exit('Must specify at least one suite to execute')
  return suites


def print_usage_and_exit(msg):
  """
  Print out msg and then usage for this program and exit.

  Args:
    msg: A string representing error msg to print out before usage doc.
  """
  print(msg)
  print(__doc__)
  exit(1)


class HawkeyeParameters(object):
  """
  Container of parameters which are used to configure
  specific hawkeye tests run.
  """
  def __init__(self):
    self.language = None
    self.suites = None
    self.test_result_verbosity = None
    self.baseline_verbosity = None
    self.baseline_file = None
    self.log_dir = None
    self.output_file = None


def process_command_line_options():
  """
  Validates and processes command line arguments. Builds HawkeyeParameters.

  Returns:
    An instance of HawkeyeParameters with filled attributres.
  """
  options = docopt.docopt(__doc__)

  # Validate language
  language = options["--lang"]
  if language not in SUPPORTED_LANGUAGES:
    print_usage_and_exit('Unsupported language. Must be one of: {0}'.
      format(SUPPORTED_LANGUAGES))

  # Prepare logs directory
  base_dir = options["--log-dir"] or os.getcwd()
  if base_dir.startswith("~"):
    base_dir = os.path.join(os.environ['HOME'], base_dir[1:])
  hawkeye_logs = os.path.join(base_dir, 'hawkeye-logs')
  if not os.path.exists(hawkeye_logs):
    os.makedirs(hawkeye_logs)
  elif not options["--keep-old-logs"]:
    for child_file in os.listdir(hawkeye_logs):
      file_path = os.path.join(hawkeye_logs, child_file)
      if os.path.isfile(file_path):
        os.unlink(file_path)

  # Set user email and password in user_tests module
  user_tests.USER_EMAIL = options["--user"]
  user_tests.USER_PASSWORD = options["--pass"]

  # Initialize Application object
  app_id = options["--app"]
  versions = []
  with open(options["--versions-csv"]) as versions_csv:
    # Skip header line
    versions_csv.next()
    for module, version, http, https, is_default in csv.reader(versions_csv):
      version = AppVersion(
        app_id=app_id, module=module, version=version,
        http_url=http, https_url=https,
        is_default_for_module=is_default.lower() == 'yes'
      )
      versions.append(version)

  url_builder = AppURLBuilder(versions, language)
  app = Application(app_id, url_builder)

  # Determine suites list
  include_opt = options["--suites"]
  include_suites = include_opt.split(',') if include_opt else []
  exclude_opt = options["--exclude-suites"]
  exclude_suites = exclude_opt.split(',') if exclude_opt else []
  suites = build_suites_list(language, include_suites, exclude_suites, app)

  # Prepare summarized hawkeye parameters
  hawkeye_params = HawkeyeParameters()
  hawkeye_params.language = language
  hawkeye_params.suites = suites
  hawkeye_params.baseline_file = "hawkeye_baseline_{}.csv".format(language)
  hawkeye_params.test_result_verbosity = 2 if options["--console"] else 1
  hawkeye_params.baseline_verbosity = 2 if options["--baseline"] else 1
  hawkeye_params.log_dir = hawkeye_logs
  hawkeye_params.output_file = "hawkeye_output.csv"
  return hawkeye_params


def run_hawkeye_tests(params):
  """
  Runs hawkeye tests according to params. Prints summary and saves
  test results to csv file.

  Args:
    params: An instance of HawkeyeParameters.
  """
  # Configure logging
  hawkeye_utils.configure_hawkeye_logging(params.log_dir, params.language)

  DeprecatedHawkeyeTestCase.LANG = params.language

  # Prepare and start testing suites
  test_runner = HawkeyeSuitesRunner(
    params.language,
    params.log_dir,
    params.baseline_file,
    params.test_result_verbosity
  )
  test_runner.run_suites(params.suites)
  test_runner.print_summary(params.baseline_verbosity)
  save_report_dict_to_csv(test_runner.suites_report, params.output_file)


if __name__ == '__main__':
  hawkeye_parameters = process_command_line_options()
  run_hawkeye_tests(hawkeye_parameters)
