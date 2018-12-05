hawkeye
=======

API fidelity test suite for AppScale

prerequisites
=======

The `geckodriver` executable must be available on your current path.

Start up appscale as usual:

```
appscale up
```

Get Hawkeye from git:

```
git clone git@github.com:AppScale/hawkeye.git
```

compile the Java version as indicated in java-app/README.md
and deploy the Java, and Python 2.7 versions:

```
appscale deploy hawkeye/java-app/module-main/war
appscale deploy hawkeye/python27-app/module-main
```
if you're going to test modules suite
you also need to deploy additional python module:
```
appscale deploy hawkeye/java-app/module-a/war
appscale deploy hawkeye/python27-app/module-a
```

Assuming that your head node runs on 192.168.33.10, you'll now have
Hawkeye Java (module-main) running at 192.168.33.10:8080,
Hawkeye Java (module-a) running at 192.168.33.10:8081,
Hawkeye Python 2.7 (module-main) running at 192.168.33.10:8082,
Hawkeye Python 2.7 (module-a) running at 192.168.33.10:8083.

run hawkeye
=======

Go into the `test-suite` directory:

```
cd test-suite
```

Create 2 csv files containing app modules and versions info:

```
cat > versions-java.csv << APP_VERSIONS
MODULE,VERSION,HTTP-URL,HTTPS-URL,IS-DEFAULT
default,1,http://192.168.33.10:8080,https://192.168.33.10:4380,yes
module-a,1,http://192.168.33.10:8081,https://192.168.33.10:4381,yes
APP_VERSIONS

cat > versions-python.csv << APP_VERSIONS
MODULE,VERSION,HTTP-URL,HTTPS-URL,IS-DEFAULT
default,1,http://192.168.33.10:8082,https://192.168.33.10:4382,yes
module-a,1,http://192.168.33.10:8083,https://192.168.33.10:4383,yes
APP_VERSIONS
```

and run it:

```
python hawkeye.py --app APP_ID --versions-csv FILE --lang LANG --baseline
```

For this example, running Hawkeye Java would be:

```
python hawkeye.py --app hawkeyejava --versions-csv versions-java.csv --lang java --baseline
```

and Python 2.7 would be:

```
python hawkeye.py --app hawkeyepython27 --versions-csv versions-python.csv --lang python --baseline
```

hawkeye output
=======

You'll see output like the following:

```
[user@host test-suite]$ python hawkeye.py --app myapp --versions-csv ./versions-example.csv --lang python  --baseline

User API Test Suite
===================
.FFE
----------------------------------------------------------------------
Ran 4 tests in 0.625s

FAILED (failures=2, errors=1)

XMPP Test Suite
===============
.
----------------------------------------------------------------------
Ran 1 test in 1.343s

OK

Blobstore Test Suite
====================
..........
----------------------------------------------------------------------
Ran 10 tests in 9.346s

OK

Cron Test Suite
===============
F
----------------------------------------------------------------------
Ran 1 test in 123.424s

FAILED (failures=1)

Modules API Test Suite
======================
.....
----------------------------------------------------------------------
Ran 5 tests in 6.431s

OK

Memcache Test Suite
===================
............
----------------------------------------------------------------------
Ran 12 tests in 13.017s

OK

Images Test Suite
=================
.........
----------------------------------------------------------------------
Ran 9 tests in 6.478s

OK

Datastore Test Suite
====================
.....F......FF.....F.FF.....F..FF.
----------------------------------------------------------------------
Ran 34 tests in 90.639s

FAILED (failures=9)

Asynchronous Datastore Test Suite
=================================
......F......FF.....F
----------------------------------------------------------------------
Ran 21 tests in 13.949s

FAILED (failures=4)

Secure URL Test Suite
=====================
FFFF
----------------------------------------------------------------------
Ran 4 tests in 1.497s

FAILED (failures=4)

Logservice Test Suite
=====================
F
----------------------------------------------------------------------
Ran 1 test in 0.525s

FAILED (failures=1)

NDB Test Suite
==============
........FFF....
----------------------------------------------------------------------
Ran 15 tests in 8.251s

FAILED (failures=3)

Task Queue Test Suite
=====================
.....F...F...
----------------------------------------------------------------------
Ran 13 tests in 82.349s

FAILED (failures=2)

Config Environment Variable Test Suite
======================================
..
----------------------------------------------------------------------
Ran 2 tests in 1.319s

OK

Comparison to baseline:
 97  tests matched baseline result
 23  tests did not match baseline result
    tests.async_datastore_tests.CompositeQueryTest.runTest ... FAIL (ok was expected)
    tests.async_datastore_tests.GQLProjectionQueryTest.runTest ... FAIL (ok was expected)
    tests.async_datastore_tests.OrderedKindAncestorQueryTest.runTest ... FAIL (ok was expected)
    tests.async_datastore_tests.ProjectionQueryTest.runTest ... FAIL (ok was expected)
    tests.cron_tests.CronTest.runTest ... FAIL (ok was expected)
    tests.datastore_tests.CompositeMultiple.runTest ... FAIL (ok was expected)
    tests.datastore_tests.CompositeProjection.runTest ... FAIL (ok was expected)
    tests.datastore_tests.CompositeQueryTest.runTest ... FAIL (ok was expected)
    tests.datastore_tests.CursorQueries.runTest ... FAIL (ok was expected)
    tests.datastore_tests.GQLProjectionQueryTest.runTest ... FAIL (ok was expected)
    tests.datastore_tests.MultipleEqualityFilters.runTest ... FAIL (ok was expected)
    tests.datastore_tests.OrderedKindAncestorQueryTest.runTest ... FAIL (ok was expected)
    tests.datastore_tests.ProjectionQueryTest.runTest ... FAIL (ok was expected)
    tests.logservice_tests.FetchLogTest.runTest ... FAIL (ok was expected)
    tests.ndb_tests.NDBCompositeQueryTest.runTest ... FAIL (ok was expected)
    tests.ndb_tests.NDBGQLTest.runTest ... FAIL (ok was expected)
    tests.ndb_tests.NDBProjectionQueryTest.runTest ... FAIL (ok was expected)
    tests.secure_url_tests.AlwaysSecureRegexTest.runTest ... FAIL (ok was expected)
    tests.secure_url_tests.AlwaysSecureTest.runTest ... FAIL (ok was expected)
    tests.secure_url_tests.NeverSecureRegexTest.runTest ... FAIL (ok was expected)
    tests.secure_url_tests.NeverSecureTest.runTest ... FAIL (ok was expected)
    tests.taskqueue_tests.LeaseModificationTest.runTest ... FAIL (ok was expected)
    tests.taskqueue_tests.RESTPullQueueTest.runTest ... FAIL (ok was expected)
 11  tests ran, but not found in baseline
    tests.datastore_tests.IndexVersatility.runTest ... FAIL
    tests.datastore_tests.LongTxRead.runTest ... ok
    tests.modules_tests.TestCreatingAndGettingEntity.test_default_module ... ok
    tests.modules_tests.TestCreatingAndGettingEntity.test_module_a ... ok
    tests.modules_tests.TestTaskTargets.test_task_targets ... ok
    tests.modules_tests.TestVersionDetails.test_default_module ... ok
    tests.modules_tests.TestVersionDetails.test_module_a ... ok
    tests.taskqueue_tests.TaskEtaTest.runTest ... ok
    tests.user_tests.AdminLoginTest.runTest ... FAIL
    tests.user_tests.LogoutURLTest.runTest ... ERROR
    tests.user_tests.UserLoginTest.runTest ... FAIL
 1   tests in baseline, but not ran
    tests.images_tests.ImageUploadTest.runTest ... ok
```

The only important part here is following:

```
 97  tests matched baseline result
 23  tests did not match baseline result
    tests.async_datastore_tests.CompositeQueryTest.runTest ... FAIL (ok was expected)
    tests.async_datastore_tests.GQLProjectionQueryTest.runTest ... FAIL (ok was expected)
    tests.async_datastore_tests.OrderedKindAncestorQueryTest.runTest ... FAIL (ok was expected)
    tests.async_datastore_tests.ProjectionQueryTest.runTest ... FAIL (ok was expected)
    tests.cron_tests.CronTest.runTest ... FAIL (ok was expected)
    ...
```

If you run into any of the baseline tests failing, you should definitely dig into these logs:
* AppScale logs (run "appscale logs somedirectory" to grab AppScale logs and put them in somedirectory).
* Hawkeye logs, located in "hawkeye/test-suite/hawkeye-logs"
