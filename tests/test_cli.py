import boto
import mock
import moto
import tempfile
import unittest

from click.testing import CliRunner

from rubberjackcli.click import rubberjack


class CLITests(unittest.TestCase):

    def _describe_environments(self, env_pairs):
        envs = [{'EnvironmentName': name, 'VersionLabel': label} for (name, label) in env_pairs]

        return_value = {
            'DescribeEnvironmentsResponse': {
                'DescribeEnvironmentsResult': {
                    'Environments': envs,
                 },
            },
        }

        return return_value

    @moto.mock_s3
    @mock.patch('boto.beanstalk.layer1.Layer1.create_application_version')
    @mock.patch('boto.beanstalk.layer1.Layer1.update_environment')
    def test_deploy(self, cav, ue):
        s3 = boto.connect_s3()
        s3.create_bucket("laterpay-rubberjack-ebdeploy")  # FIXME Remove hardcoded bucket name

        with tempfile.NamedTemporaryFile() as tmp:
            result = CliRunner().invoke(rubberjack, ['deploy', tmp.name], catch_exceptions=False)

            self.assertEquals(result.exit_code, 0, result.output)

    @moto.mock_s3
    @mock.patch('boto.beanstalk.layer1.Layer1.describe_environments')
    @mock.patch('boto.beanstalk.layer1.Layer1.update_environment')
    def test_promote(self, ue, de):
        envs = [
            ('laterpay-devnull-live', 'old'),
            ('laterpay-devnull-dev', 'new'),
        ]
        de.return_value = self._describe_environments(envs)

        CliRunner().invoke(rubberjack, ['promote'], catch_exceptions=False)

    @moto.mock_s3
    @mock.patch('sys.exit')
    @mock.patch('boto.beanstalk.layer1.Layer1.describe_environments')
    @mock.patch('boto.beanstalk.layer1.Layer1.update_environment')
    def test_promoting_same_version(self, ue, de, se):
        envs = [
            ('laterpay-devnull-live', 'same'),
            ('laterpay-devnull-dev', 'same'),
        ]
        de.return_value = self._describe_environments(envs)

        CliRunner().invoke(rubberjack, ['promote'], catch_exceptions=False)

        self.assertTrue(se.called)

    @moto.mock_s3
    def test_sigv4(self):
        CliRunner().invoke(rubberjack, ['--sigv4-host', 'foo', 'deploy'], catch_exceptions=False)

    @moto.mock_s3
    @mock.patch('boto.beanstalk.layer1.Layer1.create_application_version')
    @mock.patch('boto.beanstalk.layer1.Layer1.update_environment')
    def test_deploy_to_custom_environment(self, cav, ue):
        s3 = boto.connect_s3()
        s3.create_bucket("laterpay-rubberjack-ebdeploy")  # FIXME Remove hardcoded bucket name

        with tempfile.NamedTemporaryFile() as tmp:
            result = CliRunner().invoke(rubberjack, ['deploy', '--environment', 'wibble', tmp.name], catch_exceptions=False)

            self.assertEquals(result.exit_code, 0, result.output)

    @moto.mock_s3
    @mock.patch('boto.beanstalk.layer1.Layer1.update_environment')
    @mock.patch('boto.beanstalk.layer1.Layer1.describe_environments')
    def test_promote_to_custom_environment(self, de, ue):
        CUSTOM_TO_ENVIRONMENT = "loremipsum"

        envs = [
            ('laterpay-devnull-dev', 'new'),
            (CUSTOM_TO_ENVIRONMENT, 'old'),
        ]
        de.return_value = self._describe_environments(envs)

        result = CliRunner().invoke(rubberjack, ['promote', '--to-environment', CUSTOM_TO_ENVIRONMENT], catch_exceptions=False)
        self.assertEquals(result.exit_code, 0, result.output)
