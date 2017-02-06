import requests


class UnknownVersion(Exception):
  pass


class ImproperVersionsList(Exception):
  pass


class Application(object):
  """
  Application objects supposed to be used in test cases for hawkeye tests.
  It provides useful interface to AppScale application, so you can operate
  modules and version instead of specific IPs, host names and ports.

  It's based on requests library and is actually some kind of proxy for it.
  """

  def __init__(self, app_id, url_builder, verify_certificate=False):
    self._app_id = app_id
    self._url_builder = url_builder
    self._verify_certificate = verify_certificate

  def _put_kwargs_defaults(self, kwargs):
    if "verify" not in kwargs:
        kwargs["verify"] = self._verify_certificate
    return kwargs

  def get(self, path, module=None, version=None, https=False, **kwargs):
    return requests.get(
        self._url_builder.build_url(self._app_id, module, version, path, https),
        **self._put_kwargs_defaults(kwargs)
    )

  def post(self, path, module=None, version=None, https=False, **kwargs):
    return requests.post(
        self._url_builder.build_url(self._app_id, module, version, path, https),
        **self._put_kwargs_defaults(kwargs)
    )

  def put(self, path, module=None, version=None, https=False, **kwargs):
    return requests.put(
        self._url_builder.build_url(self._app_id, module, version, path, https),
        **self._put_kwargs_defaults(kwargs)
    )

  def delete(self, path, module=None, version=None, https=False, **kwargs):
    return requests.delete(
        self._url_builder.build_url(self._app_id, module, version, path, https),
        **self._put_kwargs_defaults(kwargs)
    )


class AppVersion(object):

  DEFAULT_MODULE = "default"

  def __init__(self, app_id, version, module,
               http_url, https_url, is_default_for_module):
    self.app_id = app_id
    self.version = version
    self.module = module
    self.http_url = http_url
    self.https_url = https_url
    self.is_default_for_module = is_default_for_module
    self.full_name = self.get_full_name(self.app_id, self.module, self.version)

  @property
  def is_default_module(self):
    return self.module == self.DEFAULT_MODULE

  @staticmethod
  def get_full_name(app_id, module, version):
    if version and not module:
      raise TypeError("Argument 'module' is required if version is specified")

    if version:
      return "{v}.{m}.{app}".format(v=version, m=module, app=app_id)
    if module:
      return "{m}.{app}".format(m=module, app=app_id)
    return app_id


class AppURLBuilder(object):
  """
  This class is kind of DNS.
  It's responsible for building URL from app_id, module, version and path.

  It allows Application class to use modules and versions abstraction
  and not care about building specific URL.
  """

  def __init__(self, app_versions):
    # Save version details into dict for quick access
    self.versions_dict = {
      app_version.full_name: app_version for app_version in app_versions
    }
    # TODO
    # Add moduleX.appY and appY full_names with link to default versions

    # TODO
    # Verify if default versions are specified for each Module!
    self.app_default_versions = {
      app_version.app_id: app_version for app_version in app_versions
      if app_version.is_default_module and app_version.is_default_for_module
    }

  def build_url(self, app_id, module, version, path, https):
    # Get full name of specific version
    version_full_name = AppVersion.get_full_name(app_id, module, version)

    app_version = self.versions_dict.get(version_full_name)
    if not app_version:
      available = sorted(self.versions_dict)
      raise UnknownVersion(
        "Unknown version '{v}' for module '{m}'. Available versions are:\n"
        "  {availalbe}"
        .format(v=version, m=module, availalbe="\n  ".join(available))
      )

    if https:
      base_url = app_version.https_url
    else:
      base_url = app_version.http_url
    return base_url + path.strip("/")
