import boto
import mock
import moto
import unittest


class CLITests(unittest.TestCase):

    @moto.mock_s3
    @mock.patch('boto.beanstalk.layer1.Layer1.create_application_version')
    @mock.patch('boto.beanstalk.layer1.Layer1.update_environment')
    def test_deploy(self, cav, ue):
        s3 = boto.connect_s3()
        s3.create_bucket("laterpay-rubberjack-ebdeploy")  # FIXME Remove hardcoded bucket name

        import rubberjackcli.deploy  # noqa

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

        import rubberjackcli.promote  # noqa
