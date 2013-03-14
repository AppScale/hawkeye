import json
from time import sleep
import uuid
import urllib
from hawkeye_utils import HawkeyeTestCase, HawkeyeTestSuite

__author__ = 'hiranya'

class MemcacheAddTest(HawkeyeTestCase):
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

class MemcacheKeyTest(HawkeyeTestCase):
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

class MemcacheSetTest(HawkeyeTestCase):
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

class MemcacheKeyExpiryTest(HawkeyeTestCase):
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

class MemcacheAsyncAddTest(HawkeyeTestCase):
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

class MemcacheAsyncSetTest(HawkeyeTestCase):
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

class MemcacheAsyncKeyExpiryTest(HawkeyeTestCase):
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

class MemcacheDeleteTest(HawkeyeTestCase):
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

class MemcacheAsyncDeleteTest(HawkeyeTestCase):
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

class MemcacheMultiAddTest(HawkeyeTestCase):
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

class MemcacheMultiSetTest(HawkeyeTestCase):
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

class MemcacheMultiDeleteTest(HawkeyeTestCase):
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

class MemcacheMultiAsyncAddTest(HawkeyeTestCase):
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

class MemcacheMultiAsyncSetTest(HawkeyeTestCase):
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

class MemcacheMultiAsyncDeleteTest(HawkeyeTestCase):
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

class SimpleJCacheTest(HawkeyeTestCase):
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

class JCacheExpiryTest(HawkeyeTestCase):
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

class JCacheAddPolicyTest(HawkeyeTestCase):
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

class MemcacheIncrTest(HawkeyeTestCase):
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

class MemcacheAsyncIncrTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    key = str(uuid.uuid1())
    value = 10
    response = self.http_get('/memcache/incr?async=true&\
                              key={0}&value={1}'.format(key, value))
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

class MemcacheIncrInitTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    key = str(uuid.uuid1())
    value = 0
    response = self.http_post('/memcache/incr',
      'delta=1&key={0}&initial=7'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache?key={0}'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(str(entry_info['value']), '8')

class MemcacheAsyncIncrInitTest(HawkeyeTestCase):
  def run_hawkeye_test(self):
    key = str(uuid.uuid1())
    value = 0
    response = self.http_post('/memcache/incr',
      'delta=1&key={0}&initial=7&async=true'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertTrue(entry_info['success'])

    response = self.http_get('/memcache?key={0}'.format(key))
    self.assertEquals(response.status, 200)
    entry_info = json.loads(response.payload)
    self.assertEquals(str(entry_info['value']), '8')


def suite(lang):
  suite = HawkeyeTestSuite('Memcache Test Suite', 'memcache')
  suite.addTest(MemcacheAddTest())
  suite.addTest(MemcacheKeyTest())
  suite.addTest(MemcacheSetTest())
  suite.addTest(MemcacheKeyExpiryTest())
  suite.addTest(MemcacheDeleteTest())
  suite.addTest(MemcacheMultiAddTest())
  suite.addTest(MemcacheMultiSetTest())
  suite.addTest(MemcacheMultiDeleteTest()) 
  suite.addTest(MemcacheIncrTest())
  suite.addTest(MemcacheIncrInitTest())
  
  if lang == 'java':
    suite.addTest(MemcacheAsyncAddTest())
    suite.addTest(MemcacheAsyncSetTest())
    suite.addTest(MemcacheAsyncKeyExpiryTest())
    suite.addTest(MemcacheAsyncDeleteTest())
    suite.addTest(MemcacheMultiAsyncAddTest())
    suite.addTest(MemcacheMultiAsyncSetTest())
    suite.addTest(MemcacheMultiAsyncDeleteTest())
    suite.addTest(MemcacheAsyncIncrTest())
    suite.addTest(MemcacheAsyncIncrInitTest())
    suite.addTest(SimpleJCacheTest())
    suite.addTest(JCacheExpiryTest())
  
  return suite
