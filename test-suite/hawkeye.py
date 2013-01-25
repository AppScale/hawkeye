#!/usr/bin/python

import hawkeye_utils
import optparse
import os
import sys
from tests import datastore_tests, ndb_tests, memcache_tests, taskqueue_tests, blobstore_tests, user_tests, images_tests, secure_url_tests, xmpp_tests
import csv
import StringIO
# we want to fail nicely since all systems don't have terminal colors
try:
  from termcolor import cprint
except ImportError:
  sys.stderr.write('termcolor module not found\n');
  # defining the cprint function as 
  def cprint(msg,color,end='\n'):
    sys.stdout.write(msg)
    if end is not '':
      sys.stdout.write(end)

__author__ = 'hiranya,Brian'

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
  parser.add_option('--baseline', action='store_true',
    dest='verbose_baseline', help='Turn on verbose reporting for baseline comparison')
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

  ran_suites={}
  for suite in suites.values():
    # we capture output to a string, print it out and then parse it for comparison/saving
    #  in the CSV file for the baseline
    buff =  StringIO.StringIO()
    runner = hawkeye_utils.HawkeyeTestRunner(suite)
    runner.set_stream(buff)
    runner.run_suite()
    output = buff.getvalue()
    buff.close()
    print output
    #
    #i=1;
    for line in output.splitlines():
      if line.startswith('runTest ('):
        #print str(i)+" "+line[9:line.index(')')]+" = "+line[line.rfind(' '):]
        #i+=1;
	key=line[9:line.index(')')]
	val = line[line.rfind(' '):]
    	ran_suites[key]=val
 
  # write the test results to a file in CSV format
  w = csv.writer(open("hawkeye_output.csv", "w"))
  for key, val in sorted(ran_suites.items()):
    w.writerow([key, val])

  # read in the baseline file (if found)
  baseline_results={}
  try:
    for key, val in csv.reader(open("hawkeye_baseline_"+options.lang+".csv")):
      baseline_results[key]=val
  except:
    print "ERROR: Could not open baseline file for comparison"

  # compare 'ran_suites' with 'baseline_results'
  tests_matched=0;
  tests_no_match=0;
  test_no_match_buffer=''
  tests_added=0
  test_added_buffer=''
  tests_ommitted=0
  test_ommitted_buffer=''
  test_results = {} #dict to count the various result values
  for key in ran_suites.keys():
    # add to the count (i.e. how many 'ok', how many 'FAIL'...)
    value = ran_suites[key]
    if(value in test_results): test_results[value]+=1
    else:  test_results[value]=1
    # compare to baseline
    if(key in baseline_results):
      if(baseline_results[key]==ran_suites[key]):
      	tests_matched+=1
      else:
        tests_no_match+=1
	test_no_match_buffer += "\t"+key+" ="+value+" (baseline ="+baseline_results[key]+")\n"
      del baseline_results[key]
    else:
      tests_added+=1
      test_added_buffer += "\t"+key+" ="+value+"\n"
  # how many ommited (how many are left in the baseline list)
  tests_ommitted = len(baseline_results)
  for key in baseline_results.keys():
    test_ommitted_buffer += "\t"+key+" ="+value+"\n"

  print "Comparison to baseline"
  print str(tests_matched)+" tests match baseline result"
  print str(tests_no_match)+" tests did not match baseline result"
  if options.verbose_baseline and tests_no_match>0:
    #print test_no_match_buffer,
    cprint(test_no_match_buffer,'red',end='')
  print str(tests_added)+" tests run, but not found in baseline"
  if options.verbose_baseline and tests_added>0:
    print test_added_buffer,
  print str(tests_ommitted)+" tests in baseline, but not run"
  if options.verbose_baseline and tests_ommitted>0:
    print test_ommitted_buffer,
  for status in sorted(test_results.keys()):
    print str(test_results[status])+" test with value: "+status
