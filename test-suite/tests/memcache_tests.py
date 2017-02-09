import json
from time import sleep
import uuid
import urllib
from hawkeye_utils import DeprecatedHawkeyeTestCase
from hawkeye_test_runner import HawkeyeTestSuite

__author__ = 'hiranya'

class MemcacheAddTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    key = str(uuid.uuid1())
    value = str(uuid.uuid1())
    response = self.http_post('/memcache',
      'key={0}&value={1}'.format(key, value))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache?key={0}'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(entry_info['value'], value)

    response = self.http_post('/memcache',
      'key={0}&value=foo'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertFalse(entry_info['success'])

    response = self.http_get('/memcache?key={0}'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(entry_info['value'], value)

class MemcacheKeyTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    key = urllib.quote(str(uuid.uuid1()) + " /.,';l][/!@#$%^\n&*()_+-=")
    value = str(uuid.uuid1())
    response = self.http_post('/memcache',
      'key={0}&value={1}'.format(key, value))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache?key={0}'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(entry_info['value'], value)

    response = self.http_post('/memcache',
      'key={0}&value=foo'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertFalse(entry_info['success'])

    response = self.http_get('/memcache?key={0}'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(entry_info['value'], value)

class MemcacheSetTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    key = str(uuid.uuid1())
    value = str(uuid.uuid1())
    response = self.http_post('/memcache',
      'key={0}&value={1}&update=true'.format(key, value))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache?key={0}'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(entry_info['value'], value)

    response = self.http_post('/memcache',
      'key={0}&value=foo&update=true'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache?key={0}'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(entry_info['value'], 'foo')

class MemcacheKeyExpiryTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    key = str(uuid.uuid1())
    value = str(uuid.uuid1())
    response = self.http_post('/memcache',
      'key={0}&value={1}&timeout=6'.format(key, value))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache?key={0}'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(entry_info['value'], value)

    sleep(8)
    response = self.http_get('/memcache?key={0}'.format(key))
    self.assertEquals(response.status, 404)

class MemcacheAsyncAddTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    key = str(uuid.uuid1())
    value = str(uuid.uuid1())
    response = self.http_post('/memcache',
      'key={0}&value={1}&async=true'.format(key, value))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache?key={0}&async=true'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(entry_info['value'], value)

    response = self.http_post('/memcache',
      'key={0}&value=foo&async=true'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertFalse(entry_info['success'])

    response = self.http_get('/memcache?key={0}&async=true'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(entry_info['value'], value)

class MemcacheAsyncSetTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    key = str(uuid.uuid1())
    value = str(uuid.uuid1())
    response = self.http_post('/memcache',
      'key={0}&value={1}&update=true&async=true'.format(key, value))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache?key={0}&async=true'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(entry_info['value'], value)

    response = self.http_post('/memcache',
      'key={0}&value=foo&update=true&async=true'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache?key={0}&async=true'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(entry_info['value'], 'foo')

class MemcacheAsyncKeyExpiryTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    key = str(uuid.uuid1())
    value = str(uuid.uuid1())
    response = self.http_post('/memcache',
      'key={0}&value={1}&timeout=6&async=true'.format(key, value))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache?key={0}&async=true'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(entry_info['value'], value)

    sleep(8)
    response = self.http_get('/memcache?key={0}&async=true'.format(key))
    self.assertEquals(response.status, 404)

class MemcacheDeleteTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    key = str(uuid.uuid1())
    value = str(uuid.uuid1())
    response = self.http_post('/memcache',
      'key={0}&value={1}'.format(key, value))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache?key={0}'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(entry_info['value'], value)

    response = self.http_delete('/memcache?key={0}'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache?key={0}'.format(key))
    self.assertEquals(response.status, 404)

class MemcacheAsyncDeleteTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    key = str(uuid.uuid1())
    value = str(uuid.uuid1())
    response = self.http_post('/memcache',
      'key={0}&value={1}&async=true'.format(key, value))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache?key={0}&async=true'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(entry_info['value'], value)

    response = self.http_delete('/memcache?key={0}&async=true'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache?key={0}&async=true'.format(key))
    self.assertEquals(response.status, 404)

class MemcacheMultiAddTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    key1 = str(uuid.uuid1())
    key2 = str(uuid.uuid1())
    value1 = str(uuid.uuid1())
    value2 = str(uuid.uuid1())
    response = self.http_post('/memcache/multi',
      'keys={0},{1}&values={2},{3}'.format(key1, key2, value1, value2))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache/multi?keys={0},{1}'.
      format(key1, key2))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(entry_info[key1], value1)
    self.assertEquals(entry_info[key2], value2)

    response = self.http_post('/memcache/multi',
      'keys={0},{1}&values={2},{3}'.format(key1, key2, 'foo', 'bar'))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertFalse(entry_info['success'])

    response = self.http_get('/memcache/multi?keys={0},{1}'.
      format(key1, key2))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(entry_info[key1], value1)
    self.assertEquals(entry_info[key2], value2)

class MemcacheMultiSetTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    key1 = str(uuid.uuid1())
    key2 = str(uuid.uuid1())
    value1 = str(uuid.uuid1())
    value2 = str(uuid.uuid1())
    response = self.http_post('/memcache/multi',
      'keys={0},{1}&values={2},{3}&update=true'.format(key1, key2,
        value1, value2))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache/multi?keys={0},{1}'.
      format(key1, key2))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(entry_info[key1], value1)
    self.assertEquals(entry_info[key2], value2)

    response = self.http_post('/memcache/multi',
      'keys={0},{1}&values={2},{3}&update=true'.format(key1, key2, 'foo', 'bar'))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache/multi?keys={0},{1}'.
      format(key1, key2))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(entry_info[key1], 'foo')
    self.assertEquals(entry_info[key2], 'bar')

class MemcacheMultiDeleteTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    key1 = str(uuid.uuid1())
    key2 = str(uuid.uuid1())
    value1 = str(uuid.uuid1())
    value2 = str(uuid.uuid1())
    response = self.http_post('/memcache/multi',
      'keys={0},{1}&values={2},{3}'.format(key1, key2, value1, value2))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache/multi?keys={0},{1}'.
      format(key1, key2))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(entry_info[key1], value1)
    self.assertEquals(entry_info[key2], value2)

    response = self.http_delete('/memcache/multi?keys={0},{1}'.
      format(key1, key2))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache/multi?keys={0},{1}'.
      format(key1, key2))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(len(entry_info), 0)

class MemcacheMultiAsyncAddTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    key1 = str(uuid.uuid1())
    key2 = str(uuid.uuid1())
    value1 = str(uuid.uuid1())
    value2 = str(uuid.uuid1())
    response = self.http_post('/memcache/multi',
      'keys={0},{1}&values={2},{3}&async=true'.format(key1, key2, value1, value2))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache/multi?keys={0},{1}&async=true'.
    format(key1, key2))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(entry_info[key1], value1)
    self.assertEquals(entry_info[key2], value2)

    response = self.http_post('/memcache/multi',
      'keys={0},{1}&values={2},{3}&async=true'.format(key1, key2, 'foo', 'bar'))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertFalse(entry_info['success'])

    response = self.http_get('/memcache/multi?keys={0},{1}&async=true'.
    format(key1, key2))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(entry_info[key1], value1)
    self.assertEquals(entry_info[key2], value2)

class MemcacheMultiAsyncSetTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    key1 = str(uuid.uuid1())
    key2 = str(uuid.uuid1())
    value1 = str(uuid.uuid1())
    value2 = str(uuid.uuid1())
    response = self.http_post('/memcache/multi',
      'keys={0},{1}&values={2},{3}&update=true&async=true'.format(key1, key2,
        value1, value2))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache/multi?keys={0},{1}&async=true'.
    format(key1, key2))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(entry_info[key1], value1)
    self.assertEquals(entry_info[key2], value2)

    response = self.http_post('/memcache/multi',
      'keys={0},{1}&values={2},{3}&update=true&async=true'.format(key1, key2, 'foo', 'bar'))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache/multi?keys={0},{1}&async=true'.
    format(key1, key2))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(entry_info[key1], 'foo')
    self.assertEquals(entry_info[key2], 'bar')

class MemcacheMultiAsyncDeleteTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    key1 = str(uuid.uuid1())
    key2 = str(uuid.uuid1())
    value1 = str(uuid.uuid1())
    value2 = str(uuid.uuid1())
    response = self.http_post('/memcache/multi',
      'keys={0},{1}&values={2},{3}&async=true'.format(key1, key2, value1, value2))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache/multi?keys={0},{1}&async=true'.
    format(key1, key2))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(entry_info[key1], value1)
    self.assertEquals(entry_info[key2], value2)

    response = self.http_delete('/memcache/multi?keys={0},{1}&async=true'.
    format(key1, key2))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache/multi?keys={0},{1}&async=true'.
    format(key1, key2))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(len(entry_info), 0)

class SimpleJCacheTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    key = str(uuid.uuid1())
    value = str(uuid.uuid1())
    response = self.http_post('/memcache/jcache',
      'key={0}&value={1}&cache=simple'.format(key, value))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache/jcache?key={0}&cache=simple'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(entry_info[key], value)

    response = self.http_get('/memcache/jcache?key=bogus&cache=simple')
    self.assertEquals(response.status, 404)

    response = self.http_delete('/memcache/jcache?key={0}&cache=simple'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(entry_info[key], value)

    response = self.http_delete('/memcache/jcache?key={0}&cache=simple'.format(key))
    self.assertEquals(response.status, 404)

class JCacheExpiryTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    key = str(uuid.uuid1())
    value = str(uuid.uuid1())
    response = self.http_post('/memcache/jcache',
      'key={0}&value={1}&cache=expiring'.format(key, value))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache/jcache?key={0}&cache=expiring'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(entry_info[key], value)

    sleep(8)
    response = self.http_get('/memcache/jcache?key={0}&cache=expiring'.format(key))
    self.assertEquals(response.status, 404)

class JCacheAddPolicyTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    key = str(uuid.uuid1())
    value = str(uuid.uuid1())
    response = self.http_post('/memcache/jcache',
      'key={0}&value={1}&cache=noupdate'.format(key, value))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache/jcache?key={0}&cache=noupdate'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(entry_info[key], value)

    response = self.http_post('/memcache/jcache',
      'key={0}&value=foo&cache=noupdate'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache/jcache?key={0}&cache=noupdate'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(entry_info[key], value)

class MemcacheIncrTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    key = str(uuid.uuid1())
    value = 10
    response = self.http_get('/memcache/incr?key={0}&value={1}'\
                              .format(key, value))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache?key={0}'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(str(entry_info['value']), '10')

    response = self.http_post('/memcache/incr',
      'key={0}&delta={1}&async=false'.format(key, 5))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache?key={0}'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(str(entry_info['value']), '15')

    response = self.http_post('/memcache/incr',
      'key={0}&delta={1}&async=false'.format(key, 4))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache?key={0}'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(str(entry_info['value']), '19')

class MemcacheDecrTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    key = str(uuid.uuid1())
    value = 1
    response = self.http_get('/memcache/incr?key={0}&value={1}'\
                              .format(key, value))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_post('/memcache/incr',
      'key={0}&delta={1}&async=false'.format(key, -1))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache?key={0}'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(str(entry_info['value']), '0')

    response = self.http_post('/memcache/incr',
      'key={0}&delta={1}&async=false'.format(key, -1))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache?key={0}'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(str(entry_info['value']), '0')

class MemcacheAsyncIncrTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    key = str(uuid.uuid1())
    value = 10
    response = self.http_get('/memcache/incr?async=true&'\
                              'key={0}&value={1}'.format(key, value))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache?key={0}'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(str(entry_info['value']), '10')

    response = self.http_post('/memcache/incr',
      'key={0}&delta={1}&async=true'.format(key, 5))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache?key={0}'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(str(entry_info['value']), '15')

    response = self.http_post('/memcache/incr',
      'key={0}&delta={1}&async=true'.format(key, 4))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache?key={0}'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(str(entry_info['value']), '19')

class MemcacheIncrInitTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    key = str(uuid.uuid1())
    response = self.http_post('/memcache/incr',
      'delta=1&key={0}&initial=7'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache?key={0}'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(str(entry_info['value']), '8')

class MemcacheAsyncIncrInitTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    key = str(uuid.uuid1())
    response = self.http_post('/memcache/incr',
      'delta=1&key={0}&initial=7&async=true'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache?key={0}'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(str(entry_info['value']), '8')

class MemcacheCasTest(DeprecatedHawkeyeTestCase):
  def run_hawkeye_test(self):
    key = str(uuid.uuid1())
    response = self.http_get('/memcache/cas')
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])
    self.assertEquals(response.status, 200)

def suite(lang, app):
  suite = HawkeyeTestSuite('Memcache Test Suite', 'memcache')
  suite.addTest(MemcacheAddTest(app))
  suite.addTest(MemcacheKeyTest(app))
  suite.addTest(MemcacheSetTest(app))
  suite.addTest(MemcacheKeyExpiryTest(app))
  suite.addTest(MemcacheDeleteTest(app))
  suite.addTest(MemcacheMultiAddTest(app))
  suite.addTest(MemcacheMultiSetTest(app))
  suite.addTest(MemcacheMultiDeleteTest(app))
  suite.addTest(MemcacheIncrTest(app))
  suite.addTest(MemcacheDecrTest(app))
  suite.addTest(MemcacheIncrInitTest(app))
  suite.addTest(MemcacheCasTest(app))
 
  if lang == 'java':
    suite.addTest(MemcacheAsyncAddTest(app))
    suite.addTest(MemcacheAsyncSetTest(app))
    suite.addTest(MemcacheAsyncKeyExpiryTest(app))
    suite.addTest(MemcacheAsyncDeleteTest(app))
    suite.addTest(MemcacheMultiAsyncAddTest(app))
    suite.addTest(MemcacheMultiAsyncSetTest(app))
    suite.addTest(MemcacheMultiAsyncDeleteTest(app))
    suite.addTest(MemcacheAsyncIncrTest(app))
    suite.addTest(MemcacheAsyncIncrInitTest(app))
    suite.addTest(SimpleJCacheTest(app))
    suite.addTest(JCacheExpiryTest(app))
  
  return suite
