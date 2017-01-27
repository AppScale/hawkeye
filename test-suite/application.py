import logging

import requests


SSL_PORT_OFFSET = 3700

class UnknownVersion(Exception):
    pass


class Application(object):
  def __init__(self, host, version_port_map, default_port):
    """
    :param host: e.g.: 192.168.33.10
    :param version_port_map: e.g.: {
      "1.default": 8080,
      "v1.module-a": 8081,
      "v2.module-a": 8082
    }
    """
    self.host = host
    self.version_port_map = version_port_map
    self.default_port = default_port
    self.language = None

  def set_language(self, language):
    self.language = language

  def _build_url(self, path, module, version, https):
    path = path.format(lang=self.language)
    if not module and not version:
      port = self.default_port
    else:
      version_full_name = "{v}.{m}".format(m=module or "-", v=version or "-")
      port = self.version_port_map.get(version_full_name)
      if not port:
        raise UnknownVersion(
          "Version '{v}' is not presented in version_port_map"
          .format(v=version_full_name)
        )
    schema = "https" if https else "http"
    return "{schema}://{host}:{port}/{path}".format(
      schema=schema, host=self.host, port=port, path=path
    )

  def _put_kwargs_defaults(self, kwargs):
    if "verify" not in kwargs:
        kwargs["verify"] = False
    return kwargs

  def get(self, path, module=None, version=None, https=False, **kwargs):
    return requests.get(
        self._build_url(path, module, version, https),
        **self._put_kwargs_defaults(kwargs)
    )

  def post(self, path, module=None, version=None, https=False, **kwargs):
    return requests.post(
        self._build_url(path, module, version, https),
        **self._put_kwargs_defaults(kwargs)
    )

  def put(self, path, module=None, version=None, https=False, **kwargs):
    return requests.put(
        self._build_url(path, module, version, https),
        **self._put_kwargs_defaults(kwargs)
    )

  def delete(self, path, module=None, version=None, https=False, **kwargs):
    return requests.delete(
        self._build_url(path, module, version, https),
        **self._put_kwargs_defaults(kwargs)
    )
