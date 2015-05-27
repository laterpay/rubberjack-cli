import boto
import moto
import unittest


class CLITests(unittest.TestCase):

    @moto.mock_s3
    def test_deploy(self):
        s3 = boto.connect_s3()
        s3.create_bucket("laterpay-rubberjack-ebdeploy")  # FIXME Remove hardcoded bucket name

        import rubberjackcli.deploy  # noqa

    def test_promote(self):
        pass
