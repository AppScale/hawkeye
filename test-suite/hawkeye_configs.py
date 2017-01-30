NOT_SPECIFIED = object()
""" Constant to identify not specified configs """


class MissedConfiguration(Exception):
  pass


class HawkeyeConfig(object):
  """
  Container of configs which should be accessible for test cases.
  It should be filled by main module which runs hawkeye tests.
  """

  def __init__(self):
    self.app = NOT_SPECIFIED
    """ :type : application.Application """
    self.language = NOT_SPECIFIED
    self.suites = NOT_SPECIFIED
    self.user = NOT_SPECIFIED
    self.password = NOT_SPECIFIED
    # TODO add other configs accessible for test cases

  def __getattr__(self, name):
    value = super(HawkeyeConfig, self).__getattribute__(name)
    if value is NOT_SPECIFIED:
      raise MissedConfiguration(
        "'{prop}' property of HawkeyeConfig is not specified".format(prop=name)
      )

configurations = HawkeyeConfig()
