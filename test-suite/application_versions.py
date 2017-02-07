import csv


class InvalidVersionsCSVFileFormat(Exception):
  pass


class AppVersion(object):
  """
  Container for details about specific version of specific module of
  specific application
  """

  DEFAULT_MODULE = "default"

  def __init__(self, app_id, module, version,
               http_url, https_url, is_default_for_module):
    self.app_id = app_id
    self.module = module
    self.version = version
    self.http_url = http_url
    self.https_url = https_url
    self.is_default_for_module = is_default_for_module
    self.full_name = self.get_version_alias(
      self.app_id, self.module, self.version)

  @property
  def is_default_module(self):
    return self.module == self.DEFAULT_MODULE

  @staticmethod
  def get_default_version_for_module(available_versions, module_name):
    """
    Gets default version for specific module.

    Args:
      available_versions: a list of AppVersion
      module_name: name of module to check
    Returns:
      AppVersion which is default version for specified module or None if
      there is no default version for module
    """
    return next((
      v for v in available_versions
      if v.is_default_for_module and v.module == module_name
    ))

  @staticmethod
  def get_version_alias(app_id, module=None, version=None):
    if version and not module:
      raise TypeError("Argument 'module' is required if version is specified")

    if version:
      return "{v}.{m}.{app}".format(v=version, m=module, app=app_id)
    if module:
      return "{m}.{app}".format(m=module, app=app_id)
    return app_id


def get_versions_list_from_csv(csv_file_name, server):
  """
  Read CSV table with the following row format:
    version.module.app-id, http-port, https-port, 'default' (or empty string)
  Basing on the table content a list of AppVersion is created.

  Args:
    csv_file_name: path to file to be read
    server: a string representing server IP or domain name
  Returns:
    a list of AppVersion
  """
  versions_list = []
  with open(csv_file_name) as csv_file:
    for row in csv.reader(csv_file, skipinitialspace=True):
      try:
        version_alias, http_port, https_port, is_default = row
        http_url = "http://{host}:{port}".format(host=server, port=http_port)
        https_url = "https://{host}:{port}".format(host=server, port=https_port)
        version, module, app = version_alias.split(".")
        app_version = AppVersion(
          app, module, version, http_url, https_url, bool(is_default)
        )
        versions_list.append(app_version)
      except ValueError:
        # Too many or too few values to unpack
        raise InvalidVersionsCSVFileFormat(
          "Row '{}' is invalid. Following format is expected: "
          "(<version>.<module>.<app-id>, <http-port>, <https-port>, default) "
          "OR (<version>.<module>.<app-id>, <http-URL>, <https-URL>, )"
        )
  return versions_list
