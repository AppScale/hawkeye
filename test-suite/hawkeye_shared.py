NOT_SPECIFIED = object()
""" Constant to identify not specified configs """


class MissedConfiguration(Exception):
  pass


class HawkeyeGlobals(object):
  """
  Container of parameters which should be accessible for test cases.
  It should be filled by main module which runs hawkeye tests.
  """

  def __init__(self):
    self.app = NOT_SPECIFIED
    """ :type : application.Application """
    self.language = NOT_SPECIFIED
    self.user = NOT_SPECIFIED
    self.password = NOT_SPECIFIED

  def __getattr__(self, name):
    value = super(HawkeyeGlobals, self).__getattribute__(name)
    if value is NOT_SPECIFIED:
      raise MissedConfiguration(
        "'{prop}' property of HawkeyeConfig is not specified".format(prop=name)
      )


shared = HawkeyeGlobals()
