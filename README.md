hawkeye
=======

API fidelity test suite for AppScale

prerequisites
=======

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
appscale deploy hawkeye/java-app
appscale deploy hawkeye/python27-app
```
additionally you need to deploy two versions of module_a:
```
appscale deploy hawkeye/python27-app/module_a_previous.yaml
appscale deploy hawkeye/python27-app/module_a_current.yaml
```
and finally mark v2 as default version for module_a:
```
appscale set-default-version module_a v2
```

Assuming that your head node runs on 192.168.33.10, you'll now have Hawkeye Java running at 192.168.33.10:8080, and Hawkeye Python 2.7 running at 192.168.33.10:8081.

run hawkeye
=======

Go into the `test-suite` directory:

```
cd hawkeye/test-suite
```

and run it:

```
python hawkeye.py -s server_ip -p server_port -l lang --baseline
```

For this example, running Hawkeye Java would be:

```
python hawkeye.py -s 192.168.33.10 -p 8080 -l java --baseline
```

and Python 2.7 would be:

```
python hawkeye.py -s 192.168.33.10 -p 8081 -l python --baseline
```

hawkeye output
=======

You'll see output like the following:

```
outer-haven:test-suite cgb$ python hawkeye.py -s ec2-107-22-98-150.compute-1.amazonaws.com -p 8081 -l python --baselin
e

User API Test Suite
===================
runTest (tests.user_tests.LoginURLTest) ... ok
runTest (tests.user_tests.UserLoginTest) ... FAIL
runTest (tests.user_tests.AdminLoginTest) ... FAIL
runTest (tests.user_tests.LogoutURLTest) ... ERROR

----------------------------------------------------------------------
Ran 4 tests in 1.232s

FAILED (failures=2, errors=1)


XMPP Test Suite
===============
runTest (tests.xmpp_tests.SendAndReceiveTest) ... ok

----------------------------------------------------------------------
Ran 1 test in 7.453s

OK


Blobstore Test Suite
====================
runTest (tests.blobstore_tests.UploadBlobTest) ... FAIL
runTest (tests.blobstore_tests.DownloadBlobTest) ... ERROR
runTest (tests.blobstore_tests.QueryBlobDataTest) ... ERROR
runTest (tests.blobstore_tests.QueryBlobByKeyTest) ... ERROR
runTest (tests.blobstore_tests.QueryBlobByPropertyTest) ... ERROR
runTest (tests.blobstore_tests.DeleteBlobTest) ... ERROR
runTest (tests.blobstore_tests.AsyncUploadBlobTest) ... FAIL
runTest (tests.blobstore_tests.AsyncQueryBlobDataTest) ... ERROR
runTest (tests.blobstore_tests.AsyncDeleteBlobTest) ... ERROR

----------------------------------------------------------------------
Ran 9 tests in 1.031s

FAILED (failures=2, errors=7)


Cron Test Suite
===============
runTest (tests.cron_tests.CronTest) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.276s

OK


Memcache Test Suite
===================
runTest (tests.memcache_tests.MemcacheAddTest) ... ok
runTest (tests.memcache_tests.MemcacheKeyTest) ... ok
runTest (tests.memcache_tests.MemcacheSetTest) ... ok
runTest (tests.memcache_tests.MemcacheKeyExpiryTest) ... ok
runTest (tests.memcache_tests.MemcacheDeleteTest) ... ok
runTest (tests.memcache_tests.MemcacheMultiAddTest) ... ok
runTest (tests.memcache_tests.MemcacheMultiSetTest) ... ok
runTest (tests.memcache_tests.MemcacheMultiDeleteTest) ... ok
runTest (tests.memcache_tests.MemcacheIncrTest) ... ok
runTest (tests.memcache_tests.MemcacheIncrInitTest) ... FAIL
runTest (tests.memcache_tests.MemcacheCasTest) ... FAIL

----------------------------------------------------------------------
Ran 11 tests in 18.599s

FAILED (failures=2)


Images Test Suite
=================
runTest (tests.images_tests.ImageDeleteTest) ... ok
runTest (tests.images_tests.ImageUploadTest) ... ok
runTest (tests.images_tests.ImageLoadTest) ... ok
runTest (tests.images_tests.ImageMetadataTest) ... ok
runTest (tests.images_tests.ImageResizeTest) ... ok
runTest (tests.images_tests.ImageRotateTest) ... ok
runTest (tests.images_tests.ImageResizeTransformTest) ... ok
runTest (tests.images_tests.ImageRotateTransformTest) ... ok

----------------------------------------------------------------------
Ran 8 tests in 8.190s

OK


Datastore Test Suite
====================
runTest (tests.datastore_tests.DataStoreCleanupTest) ... ok
runTest (tests.datastore_tests.SimpleKindAwareInsertTest) ... ok
runTest (tests.datastore_tests.KindAwareInsertWithParentTest) ... ok
runTest (tests.datastore_tests.SimpleKindAwareQueryTest) ... ok
runTest (tests.datastore_tests.AncestorQueryTest) ... ok
runTest (tests.datastore_tests.OrderedKindAncestorQueryTest) ... ok
runTest (tests.datastore_tests.KindlessQueryTest) ... ok
runTest (tests.datastore_tests.KindlessAncestorQueryTest) ... ok
runTest (tests.datastore_tests.QueryByKeyNameTest) ... ok
runTest (tests.datastore_tests.SinglePropertyBasedQueryTest) ... ok
runTest (tests.datastore_tests.OrderedResultQueryTest) ... ok
runTest (tests.datastore_tests.LimitedResultQueryTest) ... ok
runTest (tests.datastore_tests.ProjectionQueryTest) ... FAIL
runTest (tests.datastore_tests.CompositeQueryTest) ... ok
runTest (tests.datastore_tests.SimpleTransactionTest) ... ok
runTest (tests.datastore_tests.CrossGroupTransactionTest) ... ok
runTest (tests.datastore_tests.QueryCursorTest) ... ok
runTest (tests.datastore_tests.ComplexQueryCursorTest) ... ok
runTest (tests.datastore_tests.CountQueryTest) ... ok
runTest (tests.datastore_tests.GQLProjectionQueryTest) ... FAIL

----------------------------------------------------------------------
Ran 20 tests in 21.779s

FAILED (failures=2)


Asynchronous Datastore Test Suite
=================================
runTest (tests.async_datastore_tests.DataStoreCleanupTest) ... ok
runTest (tests.async_datastore_tests.PutAndGetMultipleItemsTest) ... ok
runTest (tests.async_datastore_tests.SimpleKindAwareInsertTest) ... ok
runTest (tests.async_datastore_tests.KindAwareInsertWithParentTest) ... ok
runTest (tests.async_datastore_tests.SimpleKindAwareQueryTest) ... ok
runTest (tests.async_datastore_tests.AncestorQueryTest) ... ok
runTest (tests.async_datastore_tests.OrderedKindAncestorQueryTest) ... ok
runTest (tests.async_datastore_tests.KindlessQueryTest) ... ok
runTest (tests.async_datastore_tests.KindlessAncestorQueryTest) ... ok
runTest (tests.async_datastore_tests.QueryByKeyNameTest) ... ok
runTest (tests.async_datastore_tests.SinglePropertyBasedQueryTest) ... ok
runTest (tests.async_datastore_tests.OrderedResultQueryTest) ... ok
runTest (tests.async_datastore_tests.LimitedResultQueryTest) ... ok
runTest (tests.async_datastore_tests.ProjectionQueryTest) ... FAIL
runTest (tests.async_datastore_tests.CompositeQueryTest) ... ok
runTest (tests.async_datastore_tests.SimpleTransactionTest) ... ok
runTest (tests.async_datastore_tests.CrossGroupTransactionTest) ... ERROR
runTest (tests.async_datastore_tests.QueryCursorTest) ... ok
runTest (tests.async_datastore_tests.ComplexQueryCursorTest) ... FAIL
runTest (tests.async_datastore_tests.CountQueryTest) ... FAIL
runTest (tests.async_datastore_tests.GQLProjectionQueryTest) ... FAIL

----------------------------------------------------------------------
Ran 21 tests in 23.484s

FAILED (failures=4, errors=1)


Secure URL Test Suite
=====================
runTest (tests.secure_url_tests.NeverSecureTest) ... ok
runTest (tests.secure_url_tests.AlwaysSecureTest) ... ok
runTest (tests.secure_url_tests.NeverSecureRegexTest) ... ok
runTest (tests.secure_url_tests.AlwaysSecureRegexTest) ... ok

----------------------------------------------------------------------
Ran 4 tests in 3.522s

OK


NDB Test Suite
==============
runTest (tests.ndb_tests.NDBCleanupTest) ... ok
runTest (tests.ndb_tests.SimpleKindAwareNDBInsertTest) ... ok
runTest (tests.ndb_tests.KindAwareNDBInsertWithParentTest) ... ok
runTest (tests.ndb_tests.SimpleKindAwareNDBQueryTest) ... ok
runTest (tests.ndb_tests.NDBAncestorQueryTest) ... ok
runTest (tests.ndb_tests.NDBSinglePropertyBasedQueryTest) ... ok
runTest (tests.ndb_tests.NDBOrderedResultQueryTest) ... ok
runTest (tests.ndb_tests.NDBLimitedResultQueryTest) ... ok
runTest (tests.ndb_tests.NDBProjectionQueryTest) ... FAIL
runTest (tests.ndb_tests.NDBCompositeQueryTest) ... ok
runTest (tests.ndb_tests.NDBGQLTest) ... ok
runTest (tests.ndb_tests.NDBInQueryTest) ... ok
runTest (tests.ndb_tests.NDBCursorTest) ... ok
runTest (tests.ndb_tests.SimpleNDBTransactionTest) ... ok
runTest (tests.ndb_tests.NDBCrossGroupTransactionTest) ... ok

----------------------------------------------------------------------
Ran 15 tests in 16.786s

FAILED (failures=1)


Task Queue Test Suite
=====================
runTest (tests.taskqueue_tests.PushQueueTest) ... ok
runTest (tests.taskqueue_tests.DeferredTaskTest) ... ok
runTest (tests.taskqueue_tests.QueueStatisticsTest) ... FAIL
runTest (tests.taskqueue_tests.PullQueueTest) ... ERROR
runTest (tests.taskqueue_tests.TaskRetryTest) ... ok
runTest (tests.taskqueue_tests.TaskEtaTest) ... ok
runTest (tests.taskqueue_tests.TransactionalTaskTest) ... ok
runTest (tests.taskqueue_tests.TransactionalFailedTaskTest) ... ok

----------------------------------------------------------------------
Ran 8 tests in 50.628s

FAILED (failures=1, errors=1)


Config Environment Variable Test Suite
======================================
runTest (tests.environment_variable_tests.GetConfigEnvironmentVariableTest) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.303s

OK

Comparison to baseline
61 tests match baseline result
0 tests did not match baseline result
42 tests run, but not found in baseline
        tests.async_datastore_tests.QueryByKeyNameTest = ok
        tests.memcache_tests.MemcacheIncrTest = ok
        tests.blobstore_tests.QueryBlobByKeyTest = ERROR
        tests.blobstore_tests.DownloadBlobTest = ERROR
        tests.async_datastore_tests.SimpleKindAwareQueryTest = ok
        tests.async_datastore_tests.KindlessAncestorQueryTest = ok
        tests.user_tests.AdminLoginTest = FAIL
        tests.async_datastore_tests.LimitedResultQueryTest = ok
        tests.async_datastore_tests.QueryCursorTest = ok
        tests.async_datastore_tests.OrderedKindAncestorQueryTest = ok
        tests.blobstore_tests.AsyncDeleteBlobTest = ERROR
        tests.async_datastore_tests.KindlessQueryTest = ok
        tests.user_tests.UserLoginTest = FAIL
        tests.blobstore_tests.QueryBlobByPropertyTest = ERROR
        tests.blobstore_tests.DeleteBlobTest = ERROR
        tests.async_datastore_tests.CountQueryTest = FAIL
        tests.blobstore_tests.QueryBlobDataTest = ERROR
        tests.async_datastore_tests.SimpleTransactionTest = ok
        tests.async_datastore_tests.SinglePropertyBasedQueryTest = ok
        tests.async_datastore_tests.SimpleKindAwareInsertTest = ok
        tests.memcache_tests.MemcacheIncrInitTest = FAIL
        tests.datastore_tests.GQLProjectionQueryTest = FAIL
        tests.datastore_tests.ProjectionQueryTest = FAIL
        tests.taskqueue_tests.PullQueueTest = ERROR
        tests.async_datastore_tests.CrossGroupTransactionTest = ERROR
        tests.async_datastore_tests.GQLProjectionQueryTest = FAIL
        tests.blobstore_tests.UploadBlobTest = FAIL
        tests.async_datastore_tests.DataStoreCleanupTest = ok
        tests.async_datastore_tests.AncestorQueryTest = ok
        tests.async_datastore_tests.PutAndGetMultipleItemsTest = ok
        tests.async_datastore_tests.CompositeQueryTest = ok
        tests.memcache_tests.MemcacheCasTest = FAIL
        tests.blobstore_tests.AsyncQueryBlobDataTest = ERROR
        tests.user_tests.LogoutURLTest = ERROR
        tests.async_datastore_tests.OrderedResultQueryTest = ok
        tests.taskqueue_tests.QueueStatisticsTest = FAIL
        tests.datastore_tests.OrderedKindAncestorQueryTest = ok
        tests.async_datastore_tests.KindAwareInsertWithParentTest = ok
        tests.ndb_tests.NDBProjectionQueryTest = FAIL
        tests.async_datastore_tests.ComplexQueryCursorTest = FAIL
        tests.async_datastore_tests.ProjectionQueryTest = FAIL
        tests.blobstore_tests.AsyncUploadBlobTest = FAIL
0 tests in baseline, but not run
10 test with value:  ERROR
14 test with value:  FAIL
79 test with value:  ok
```

The only important part here is the line that says:

```
61 tests match baseline result
0 tests did not match baseline result
```

This is the kind of output you want to see. If any tests do not match the baseline result, you'll see something like this:

```
60 tests match baseline result
1 tests did not match baseline result
        tests.taskqueue_tests.TransactionalTaskTest = FAIL (baseline = ok)
```

If you run into any of the baseline tests failing, you should definitely dig into these logs:
* AppScale logs (run "appscale logs somedirectory" to grab AppScale logs and put them in somedirectory).
* Hawkeye logs, located in "hawkeye/test-suite/logs"
