import webapp2

from async_datastore import urls as async_datastore_urls
from blobstore import urls as blobstore_urls
from cron import urls as cron_urls
from datastore import urls as datastore_urls
from env_var import urls as env_var_urls
from images import urls as images_urls
from logservice import urls as logservice_urls
from memcache import urls as memcache_urls
from modules_main import urls as modules_urls
from ndb import urls as ndb_urls
from secure_url import urls as secure_url_urls
from taskqueue import urls as taskqueue_urls
from users import urls as user_urls
from xmpp import urls as xmpp_urls

app = webapp2.WSGIApplication(
  async_datastore_urls +
  blobstore_urls +
  cron_urls +
  datastore_urls +
  env_var_urls +
  images_urls +
  logservice_urls +
  memcache_urls +
  modules_urls +
  ndb_urls +
  secure_url_urls +
  taskqueue_urls +
  user_urls +
  xmpp_urls
)
