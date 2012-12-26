#!/usr/bin/python

import hawkeye_utils
import optparse
import os
import sys
from tests import datastore_tests, ndb_tests, memcache_tests, taskqueue_tests, blobstore_tests, user_tests

__author__ = 'hiranya'

SUPPORTED_LANGUAGES = [ 'java', 'python' ]

def print_usage_and_exit(msg, parser):
  print msg
  parser.print_help()
  exit(1)

if __name__ == '__main__':
  parser = optparse.OptionParser()
  parser.add_option('-s', '--server', action='store',
    type='string', dest='server')
  parser.add_option('-p', '--port', action='store',
    type='int', dest='port')
  parser.add_option('-l', '--lang', action='store',
    type='string', dest='lang')
  parser.add_option('--user', action='store',
    type='string', dest='user')
  parser.add_option('--pass', action='store',
    type='string', dest='password')
  parser.add_option('-c', '--console', action='store_true',
    dest='console')
  parser.add_option('--suites', action='store', type='string',
    dest='suites')
  (options, args) = parser.parse_args(sys.argv[1:])

  if options.server is None:
    print_usage_and_exit('Target server name not specified', parser)
  elif options.port is None:
    print_usage_and_exit('Target port name not specified', parser)
  elif options.lang is not None and options.lang not in SUPPORTED_LANGUAGES:
    print_usage_and_exit('Unsupported language. Must be one of: {0}'.
      format(SUPPORTED_LANGUAGES), parser)
  elif options.lang is None:
    options.lang = 'python'

  suite_names = ['all']
  if options.suites is not None:
    suite_names = options.suites.split(',')

  if options.user is not None:
    hawkeye_utils.USER_EMAIL = options.user
  if options.password is not None:
    hawkeye_utils.USER_PASSWORD = options.password

  hawkeye_utils.HOST = options.server
  hawkeye_utils.PORT = options.port
  hawkeye_utils.LANG = options.lang

  if options.console:
    hawkeye_utils.CONSOLE_MODE = True

  suites = []
  for suite_name in suite_names:
    suite_name = suite_name.strip()
    if suite_name == 'all':
      suites = [ datastore_tests.suite(), ndb_tests.suite(), memcache_tests.suite(),
                 taskqueue_tests.suite(), blobstore_tests.suite(), user_tests.suite() ]
      break
    elif suite_name == 'datastore':
      suites.append(datastore_tests.suite())
    elif suite_name == 'ndb':
      suites.append(ndb_tests.suite())
    elif suite_name == 'memcache':
      suites.append(memcache_tests.suite())
    elif suite_name == 'taskqueue':
      suites.append(taskqueue_tests.suite())
    elif suite_name == 'blobstore':
      suites.append(blobstore_tests.suite())
    elif suite_name == 'users':
      suites.append(user_tests.suite())
    else:
      print_usage_and_exit('Unsupported test suite: {0}'.
        format(suite_name), parser)

  if not os.path.exists('logs'):
    os.makedirs('logs')

  for child_file in os.listdir('logs'):
    file_path = os.path.join('logs', child_file)
    if os.path.isfile(file_path):
      os.unlink(file_path)

  for suite in suites:
    runner = hawkeye_utils.HawkeyeTestRunner(suite)
    runner.run_suite()
