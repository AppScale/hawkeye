#!/usr/bin/python
""" hawkeye.py: Run API fidelity tests on AppScale. """

import optparse
import os
import sys

from hawkeye_test_runner import HawkeyeSuitesRunner, save_report_dict_to_csv

if not sys.version_info[:2] > (2, 6):
  raise RuntimeError("Hawkeye will only run with Python 2.7 or newer.")

import hawkeye_utils
from tests import (
  datastore_tests, ndb_tests, memcache_tests, taskqueue_tests, blobstore_tests,
  user_tests, images_tests, secure_url_tests, xmpp_tests,
  environment_variable_tests, async_datastore_tests, cron_tests
)

SUPPORTED_LANGUAGES = ['java', 'python']


def build_suites_list(lang, include, exclude):
  """
  :param lang: language to test, either 'python' or 'java'
  :param include: suites to return (use empty list to include all)
  :param exclude: suites to skip (is ignored if 'include' is specified)
  """
  defined_suites  = {
    'blobstore' : blobstore_tests.suite(lang),
    'datastore' : datastore_tests.suite(lang),
    'async_datastore' : async_datastore_tests.suite(lang),
    'env_var' : environment_variable_tests.suite(lang),
    'images' : images_tests.suite(lang),
    'memcache' : memcache_tests.suite(lang),
    'ndb' : ndb_tests.suite(lang),
    'secure_url' : secure_url_tests.suite(lang),
    'taskqueue' : taskqueue_tests.suite(lang),
    'users' : user_tests.suite(lang),
    'xmpp' : xmpp_tests.suite(lang),
    'cron' : cron_tests.suite(lang),
  }
  # Validation include and exclude lists
  for suite_name in include + exclude:
    if suite_name not in defined_suites:
      print_usage_and_exit("Unknown suite '{}'. Suite can be one of {}"
                           .format(suite_name, defined_suites.keys()))

  if include:
    return [
      suite for suite_name, suite in defined_suites.iteritems()
      if suite_name in include
    ]
  if exclude:
    return [
      suite for suite_name, suite in defined_suites.iteritems()
      if suite_name not in exclude
    ]
  return defined_suites.values()


def print_usage_and_exit(msg):
  """
  Print out usage for this program and  and exit.
  :param msg: error message to print out.
  """
  print msg
  build_option_parser().print_help()
  exit(1)


def build_option_parser():
  parser = optparse.OptionParser()
  parser.add_option('-s', '--server', action='store',
    type='string', dest='server',
    help='Hostname of the target AppEngine server')
  parser.add_option('-p', '--port', action='store',
    type='int', dest='port', help='Port of the target AppEngine server')
  parser.add_option('-l', '--lang', action='store',
    type='string', dest='lang',
    help='Language binding to test (eg: python, python27, java)')
  parser.add_option('--user', action='store',
    type='string', dest='user', help='Admin username (defaults to a@a.com)')
  parser.add_option('--pass', action='store',
    type='string', dest='password', help='Admin password (defaults to aaaaaa)')
  parser.add_option('-c', '--console', action='store_true',
    dest='console', help='Log errors and failures to console')
  parser.add_option('--suites', action='store', type='string',
    dest='suites', help='A comma separated list of suites to run')
  parser.add_option('--exclude-suites', action='store', type='string',
    dest='exclude_suites', help='A comma separated list of suites to exclude')
  parser.add_option('--baseline', action='store_true',
    dest='verbose_baseline',
    help='Turn on verbose reporting for baseline comparison')
  parser.add_option('--log-dir', action='store', type='string',
    dest='base_dir',
    help='Directory to store error logs.')
  parser.add_option('--keep-old-logs', action='store_true',
    dest='keep_old_logs', help='Keep existing hawkeye logs')
  return parser


if __name__ == '__main__':
  parser = build_option_parser()
  (options, args) = parser.parse_args(sys.argv[1:])

  if options.server is None:
    print_usage_and_exit('Target server name not specified')
  elif options.port is None:
    print_usage_and_exit('Target port name not specified')
  elif options.lang is not None and options.lang not in SUPPORTED_LANGUAGES:
    print_usage_and_exit('Unsupported language. Must be one of: {0}'.
      format(SUPPORTED_LANGUAGES))
  elif options.lang is None:
    options.lang = 'python'

  if options.base_dir is None:
    base_dir = os.getcwd()
  else:
    base_dir = options.base_dir
    if base_dir[0] == '~':
      base_dir = "{0}{1}".format(os.environ['HOME'], base_dir[1:])

  include_suites = []
  exclude_suites = []
  if options.suites:
    include_suites = options.suites.split(',')
  if options.exclude_suites:
    exclude_suites = options.exclude_suites.split(',')

  if options.user:
    user_tests.USER_EMAIL = options.user
  if options.password:
    user_tests.USER_PASSWORD = options.password

  hawkeye_utils.HOST = options.server
  hawkeye_utils.PORT = options.port
  hawkeye_utils.LANG = options.lang

  if options.console:
    hawkeye_utils.CONSOLE_MODE = True

  hawkeye_logs = os.path.join(base_dir, 'hawkeye-logs')
  if not os.path.exists(hawkeye_logs):
    os.makedirs(hawkeye_logs)

  os.environ['LOG_BASE_DIR'] = hawkeye_logs

  if not options.keep_old_logs:
    for child_file in os.listdir(hawkeye_logs):
      file_path = os.path.join(hawkeye_logs, child_file)
      if os.path.isfile(file_path):
        os.unlink(file_path)

  suites = build_suites_list(options.lang, include_suites, exclude_suites)

  if not suites:
    print_usage_and_exit('Must specify at least one suite to execute')

  verbosity = 2 if options.console else 1
  baseline_file = "hawkeye_baseline_{lang}.csv".format(lang=options.lang)

  test_runner = HawkeyeSuitesRunner(
    options.lang, hawkeye_logs, baseline_file, verbosity)

  test_runner.run_suites(suites)
  test_runner.print_summary(options.verbose_baseline)
  save_report_dict_to_csv(test_runner.suites_report, "hawkeye_output.csv")
