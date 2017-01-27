import unittest

import application

class HawkeyeTestCase(unittest.TestCase):
  """
  TODO find a way to implement TestRunner in such way that it will be able to
   create testcase objects with specific Application object.
   So test runner will be able to change language
  """
  def __init__(self, *args, **kwargs):
    self.app = kwargs["application"]
    # TODO super ...
