#!/usr/local/Python-2.7.3/python

#this used to be: #!/usr/bin/python
#but we need v2.7 to run correctly

import hawkeye_utils
import optparse
import os
import sys
from tests import datastore_tests, ndb_tests, memcache_tests, taskqueue_tests, blobstore_tests, user_tests, images_tests, secure_url_tests, xmpp_tests
import csv
import StringIO

__author__ = 'hiranya'

SUPPORTED_LANGUAGES = [ 'java', 'python', 'python27' ]

def init_test_suites(lang):
  return {
    'blobstore' : blobstore_tests.suite(lang),
    'datastore' : datastore_tests.suite(lang),
    'images' : images_tests.suite(lang),
    'memcache' : memcache_tests.suite(lang),
    'ndb' : ndb_tests.suite(lang),
    'secure_url' : secure_url_tests.suite(lang),
    'taskqueue' : taskqueue_tests.suite(lang),
    'users' : user_tests.suite(lang),
    'xmpp' : xmpp_tests.suite(lang),
  }

def print_usage_and_exit(msg, parser):
  print msg
  parser.print_help()
  exit(1)

if __name__ == '__main__':
  parser = optparse.OptionParser()
  parser.add_option('-s', '--server', action='store',
    type='string', dest='server', help='Hostname of the target AppEngine server')
  parser.add_option('-p', '--port', action='store',
    type='int', dest='port', help='Port of the target AppEngine server')
  parser.add_option('-l', '--lang', action='store',
    type='string', dest='lang', help='Language binding to test (eg: python, python27, java)')
  parser.add_option('--user', action='store',
    type='string', dest='user', help='Admin username (defaults to a@a.a)')
  parser.add_option('--pass', action='store',
    type='string', dest='password', help='Admin password (defaults to aaaaaa')
  parser.add_option('-c', '--console', action='store_true',
    dest='console', help='Log errors and failures to console')
  parser.add_option('--suites', action='store', type='string',
    dest='suites', help='A comma separated list of suites to run')
  parser.add_option('--exclude-suites', action='store', type='string',
    dest='exclude_suites', help='A comma separated list of suites to exclude')
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
  exclude_suites = []
  if options.suites is not None:
    suite_names = options.suites.split(',')
  if options.exclude_suites is not None:
    exclude_suites = options.exclude_suites.split(',')

  if options.user is not None:
    user_tests.USER_EMAIL = options.user
  if options.password is not None:
    user_tests.USER_PASSWORD = options.password

  hawkeye_utils.HOST = options.server
  hawkeye_utils.PORT = options.port
  hawkeye_utils.LANG = options.lang

  if options.console:
    hawkeye_utils.CONSOLE_MODE = True

  suites = {}
  TEST_SUITES = init_test_suites(options.lang)
  for suite_name in suite_names:
    suite_name = suite_name.strip()
    if suite_name == 'all':
      suites = TEST_SUITES
      break
    elif TEST_SUITES.has_key(suite_name):
      suites[suite_name] = TEST_SUITES[suite_name]
    else:
      print_usage_and_exit('Unsupported test suite: {0}'.
        format(suite_name), parser)

  for exclude_suite in exclude_suites:
    exclude_suite = exclude_suite.strip()
    if suites.has_key(exclude_suite):
      del(suites[exclude_suite])
    elif not TEST_SUITES.has_key(exclude_suite):
      print_usage_and_exit('Unsupported test suite: {0}'.
        format(exclude_suite), parser)

  if not suites:
    print_usage_and_exit('Must specify at least one suite to execute', parser)

  if not os.path.exists('logs'):
    os.makedirs('logs')

  for child_file in os.listdir('logs'):
    file_path = os.path.join('logs', child_file)
    if os.path.isfile(file_path):
      os.unlink(file_path)

  i=1;
  ran_suites={}
  for suite in suites.values():
    runner = hawkeye_utils.HawkeyeTestRunner(suite)
    print "suite "+str(i)+" "+suite.name
    i+=1
    # we are gong to capture stout to a string, print it out and then parse it for comparison/saving
    #  in the CSV file for the baseline
    old_stdout = sys.stderr
    sys.stderr = StringIO.StringIO()
    runner.run_suite()
    output = sys.stderr.getvalue()
    sys.stderr = old_stdout  #restore stdout
    print "BLERGBLERG:"+output,
    print "BLERGBLERG:"
    ran_suites[suite.name]=output.strip()
  
  w = csv.writer(open("output.csv", "w"))
  for key, val in ran_suites.items():
    w.writerow([key, val])
