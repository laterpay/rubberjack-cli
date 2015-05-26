import moto
import unittest


class CLITests(unittest.TestCase):

    @moto.mock_s3
    def test_deploy(self):
        import rubberjackcli.deploy

    def test_promote(self):
        pass
