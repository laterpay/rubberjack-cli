import boto
import mock
import moto
import unittest

from click.testing import CliRunner

from rubberjackcli.click import rubberjack


class CLITests(unittest.TestCase):

    @moto.mock_s3
    @mock.patch('boto.beanstalk.layer1.Layer1.create_application_version')
    @mock.patch('boto.beanstalk.layer1.Layer1.update_environment')
    def test_deploy(self, cav, ue):
        s3 = boto.connect_s3()
        s3.create_bucket("laterpay-rubberjack-ebdeploy")  # FIXME Remove hardcoded bucket name

        CliRunner().invoke(rubberjack, ['deploy'], catch_exceptions=False)

    @moto.mock_s3
    @mock.patch('boto.beanstalk.layer1.Layer1.describe_environments')
    @mock.patch('boto.beanstalk.layer1.Layer1.update_environment')
    def test_promote(self, ue, de):
        de.return_value = {
            'DescribeEnvironmentsResponse': {
                'DescribeEnvironmentsResult': {
                    'Environments': [
                        {
                            'EnvironmentName': 'laterpay-devnull-live',  # FIXME Remove hardcoded EnvName
                            'VersionLabel': 'old',
                        },
                        {
                            'EnvironmentName': 'laterpay-devnull-dev',  # FIXME Remove hardcoded EnvName
                            'VersionLabel': 'new',
                        },
                    ],
                },
            },
        }

        CliRunner().invoke(rubberjack, ['promote'], catch_exceptions=False)

    @moto.mock_s3
    @mock.patch('sys.exit')
    @mock.patch('boto.beanstalk.layer1.Layer1.describe_environments')
    @mock.patch('boto.beanstalk.layer1.Layer1.update_environment')
    def test_promoting_same_version(self, ue, de, se):
        de.return_value = {
            'DescribeEnvironmentsResponse': {
                'DescribeEnvironmentsResult': {
                    'Environments': [
                        {
                            'EnvironmentName': 'laterpay-devnull-live',  # FIXME Remove hardcoded EnvName
                            'VersionLabel': 'same',
                        },
                        {
                            'EnvironmentName': 'laterpay-devnull-dev',  # FIXME Remove hardcoded EnvName
                            'VersionLabel': 'same',
                        },
                    ],
                },
            },
        }

        CliRunner().invoke(rubberjack, ['promote'], catch_exceptions=False)

        self.assertTrue(se.called)
