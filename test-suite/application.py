import requests


class UnknownVersion(Exception):
  pass


class UnknownApplication(Exception):
  pass


class NoAppsWereFound(Exception):
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


class AppURLBuilder(object):
  """
  This class is kind of DNS.
  It's responsible for building URL from app_id, module, version and path.

  It fetches information about all apps, modules and versions deployed
  on appscale cluster and provides build_url method which is used by
  Application class.

  It allows Application class to use modules and versions abstraction
  and not care about building specific URL.
  """

  versions_api_method = "/api/versions"
  DEFAULT_MODULE = "default"

  class AppVersion(object):
    def __init__(self, version_details):
      self.app_id = version_details["app_id"]
      self.version = version_details["version"]
      self.module = version_details["module"]
      self.http_url = version_details["http_url"]
      self.https_url = version_details["https_url"]
      self.is_default = version_details["is_default"]
      self.full_name = self.get_full_name(self.app_id, self.module, self.version)

    @staticmethod
    def get_full_name(app_id, module, version):
      return "{v}.{m}.{app}".format(
        v=version, m=module, app=app_id
      )

  def __init__(self, dashboard_host, dashboard_port=1080):
    # Get details about versions from dashboard
    versions_json = requests.get(
      "https://{host}:{port}{path}".format(
        host=dashboard_host,
        port=dashboard_port,
        path=self.versions_api_method,
    )).json()
    # It's expected that response has following structure:
    # [
    #  {'app_id': 'hawkeyepython27', 'module': 'default', 'version': 'v1-5',
    #   'is_default': true,
    #   'http_url': 'http://192.168.33.10:8080/',
    #   'https_url': 'https://192.168.33.10:4380/'},
    #  ...
    # ]
    app_versions = [
      self.AppVersion(**version_details) for version_details in versions_json
    ]
    if not app_versions:
      raise NoAppsWereFound(
        "There are no AppScale applications on {host}.{port}"
        .format(host=dashboard_host, port=dashboard_port)
      )
    # Save version details into dicts for quick access
    self.versions_dict = {
      app_version.full_name: app_version for app_version in app_versions
    }
    self.app_default_versions = {
      app_version.app_id: app_version for app_version in app_versions
      if app_version.module == self.DEFAULT_MODULE and app_version.is_default
    }

    self.dashboard_host = dashboard_host
    self.dashboard_port = dashboard_port

  def build_url(self, app_id, module, version, path, https):

    # Verify is application is deployed to AppScale cluster
    if app_id not in self.app_default_versions:
      raise UnknownApplication(
        "There is no application '{app_id}' on {host}"
        .format(app_id=app_id, host=self.dashboard_host)
      )

    # Get full name of specific version
    if not module and not version:
      version_full_name = self.app_default_versions[app_id].full_name
    else:
      version_full_name = self.AppVersion.get_full_name(app_id, module, version)

    app_version = self.versions_dict.get(version_full_name)
    if not app_version:
      raise UnknownVersion(
        "There are no version '{v}' for module '{m}'"
        .format(v=version, m=module)
      )

    if https:
      base_url = app_version.https_url
    else:
      base_url = app_version.http_url
    return base_url + path.strip("/")
