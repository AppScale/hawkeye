import optparse
import unittest
from unittest.runner import TextTestRunner
import sys
import hawkeye_test_case
from tests import datastore_tests, ndb_tests

__author__ = 'hiranya'

SUPPORTED_LANGUAGES = [ 'java', 'python' ]

def print_usage_and_exit(msg, parser):
  print msg
  parser.print_help()
  exit(1)

if __name__ == '__main__':
  parser = optparse.OptionParser()
  parser.add_option('-s', '--server', action='store', type='string', dest='server')
  parser.add_option('-p', '--port', action='store', type='int', dest='port')
  parser.add_option('-l', '--lang', action='store', type='string', dest='lang')
  parser.add_option('--suites', action='store', type='string', dest='suites')
  (options,args) = parser.parse_args(sys.argv[1:])

  if options.server is None:
    print_usage_and_exit('Target server name not specified', parser)
  elif options.port is None:
    print_usage_and_exit('Target port name not specified', parser)
  elif options.lang is not None and options.lang not in SUPPORTED_LANGUAGES:
    print_usage_and_exit('Unsupported language. Must be one of: {0}'.format(SUPPORTED_LANGUAGES), parser)
  elif options.lang is None:
    options.lang = 'python'

  suite_names = ['all']
  if options.suites is not None:
    suite_names = options.suites.split(',')

  suites = []
  for suite_name in suite_names:
    suite_name = suite_name.strip()
    if suite_name == 'all':
      suites = [ datastore_tests.suite(), ndb_tests.suite() ]
      break
    elif suite_name == 'datastore':
      suites.append(datastore_tests.suite())
    elif suite_name == 'ndb':
      suites.append(ndb_tests.suite())
    else:
      print_usage_and_exit('Unsupported test suite: {0}'.format(suite_name), parser)

  hawkeye_test_case.HOST = options.server
  hawkeye_test_case.PORT = options.port
  hawkeye_test_case.LANG = options.lang

  aggregate_suite = unittest.TestSuite(suites)
  TextTestRunner(verbosity=2).run(aggregate_suite)