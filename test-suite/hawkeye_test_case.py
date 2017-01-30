import unittest

import application
import hawkeye_configs


class HawkeyeTestCase(unittest.TestCase):
  def setUp(self):
    self.app = hawkeye_configs.configurations.app
