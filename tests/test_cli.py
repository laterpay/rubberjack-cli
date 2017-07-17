import boto
import mock
import moto
import tempfile
import unittest

from click.testing import CliRunner

from rubberjackcli.click import rubberjack


class CLITests(unittest.TestCase):

    @moto.mock_s3_deprecated
    @mock.patch('boto.beanstalk.layer1.Layer1.create_application_version')
    @mock.patch('boto.beanstalk.layer1.Layer1.update_environment')
    def test_deploy(self, cav, ue):
        s3 = boto.connect_s3()
        s3.create_bucket("laterpay-rubberjack-ebdeploy")  # FIXME Remove hardcoded bucket name

        with tempfile.NamedTemporaryFile() as tmp:
            result = CliRunner().invoke(rubberjack, ['deploy', tmp.name], catch_exceptions=False)

            self.assertEquals(result.exit_code, 0, result.output)

    @moto.mock_s3_deprecated
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

    @moto.mock_s3_deprecated
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

    @moto.mock_s3_deprecated
    def test_sigv4(self):
        CliRunner().invoke(rubberjack, ['--sigv4-host', 'foo', 'deploy'], catch_exceptions=False)

    @moto.mock_s3_deprecated
    @mock.patch('boto.beanstalk.layer1.Layer1.create_application_version')
    @mock.patch('boto.beanstalk.layer1.Layer1.update_environment')
    def test_deploy_to_custom_environment(self, ue, cav):
        s3 = boto.connect_s3()
        s3.create_bucket("laterpay-rubberjack-ebdeploy")  # FIXME Remove hardcoded bucket name

        with tempfile.NamedTemporaryFile() as tmp:
            result = CliRunner().invoke(rubberjack, ['deploy', '--environment', 'wibble', tmp.name], catch_exceptions=False)

            self.assertEquals(result.exit_code, 0, result.output)

        self.assertEqual(cav.call_count, 1, "create_application_version wasn't called, but it should")
        self.assertEqual(ue.call_count, 1, "update_environment wasn't called, but it should")

    @moto.mock_s3_deprecated
    @mock.patch('boto.beanstalk.layer1.Layer1.create_application_version')
    @mock.patch('boto.beanstalk.layer1.Layer1.update_environment')
    def test_deploy_without_updating_the_environment(self, ue, cav):
        s3 = boto.connect_s3()
        s3.create_bucket("laterpay-rubberjack-ebdeploy")  # FIXME Remove hardcoded bucket name

        with tempfile.NamedTemporaryFile() as tmp:
            result = CliRunner().invoke(rubberjack, ['deploy', '--no-update-environment', tmp.name], catch_exceptions=False)

            self.assertEquals(result.exit_code, 0, result.output)

        self.assertEqual(cav.call_count, 1, "create_application_version wasn't called, but it should")
        self.assertEqual(ue.call_count, 0, "update_environment was called, but it shouldn't")

    @moto.mock_s3_deprecated
    @mock.patch('boto.beanstalk.layer1.Layer1.create_application_version')
    @mock.patch('boto.beanstalk.layer1.Layer1.update_environment')
    def test_deploy_to_custom_bucket(self, ue, cav):
        bucket_name = 'rbbrjck-test'
        s3 = boto.connect_s3()
        s3.create_bucket(bucket_name)

        with tempfile.NamedTemporaryFile() as tmp:
            result = CliRunner().invoke(rubberjack, ['--bucket', bucket_name, 'deploy', tmp.name], catch_exceptions=False)

            self.assertEquals(result.exit_code, 0, result.output)

        self.assertEqual(cav.call_count, 1, "create_application_version wasn't called, but it should")
        self.assertEqual(ue.call_count, 1, "update_environment wasn't called, but it should")

        _, cav_kwargs = cav.call_args
        self.assertEqual(bucket_name, cav_kwargs['s3_bucket'])

    @moto.mock_s3_deprecated
    @mock.patch('boto.beanstalk.layer1.Layer1.update_environment')
    @mock.patch('boto.beanstalk.layer1.Layer1.describe_environments')
    def test_promote_to_custom_environment(self, de, ue):
        CUSTOM_TO_ENVIRONMENT = "loremipsum"

        de.return_value = {
            'DescribeEnvironmentsResponse': {
                'DescribeEnvironmentsResult': {
                    'Environments': [
                        {
                            'EnvironmentName': CUSTOM_TO_ENVIRONMENT,
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

        result = CliRunner().invoke(rubberjack, ['promote', '--to-environment', CUSTOM_TO_ENVIRONMENT], catch_exceptions=False)
        self.assertEquals(result.exit_code, 0, result.output)
