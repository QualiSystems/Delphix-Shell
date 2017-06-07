import unittest

import mock

from cloudshell.delphix.delphix_client import DelphixClient


class TestDelphixClient(unittest.TestCase):
    def setUp(self):
        self.engine_conf = mock.MagicMock()
        self.client = DelphixClient(engine_conf=self.engine_conf)

    def test_empty(self):
        pass
