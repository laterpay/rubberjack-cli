"""
Command-line tooling for RubberJack.

https://github.com/laterpay/rubberjack
"""

from __future__ import absolute_import

import logging
import subprocess
import sys

import boto
import boto.beanstalk.layer1
import click

_logger = logging.getLogger(__name__)

ORGANISATION = "laterpay"
REGION = "eu-central-1"
APPLICATION = "devnull"

APPLICATION_NAME = "{organisation}-{application}".format(organisation=ORGANISATION, application=APPLICATION)
DEV_ENVIRONMENT_NAME = "{application_name}-dev".format(application_name=APPLICATION_NAME)
LIVE_ENVIRONMENT_NAME = "{application_name}-live".format(application_name=APPLICATION_NAME)

BUCKET = "{organisation}-rubberjack-ebdeploy".format(organisation=ORGANISATION)


def region_from_name(region_name):
    """
    Get an AWS region from a friendly string like `"eu-central-1"`.
    """

    regions = boto.beanstalk.regions()
    region = None
    for r in regions:
        if r.name == region_name:
            region = r
    assert region is not None

    return region


@click.group()
@click.pass_context
def rubberjack(ctx):
    """
    Main entry point into the rubberjack CLI.
    """

    pass


@rubberjack.command()
@click.pass_context
def deploy(ctx):
    """
    Do the actual deployment work.

    (See the module-level docstring for more details and caveats)
    """

    _logger.info("Deploying {application}".format(application=APPLICATION))

    # Setup Boto

    beanstalk = boto.beanstalk.layer1.Layer1(region=region_from_name(REGION))
    s3 = boto.connect_s3()

    # Extract deployable info

    COMMIT = subprocess.check_output(["git", "rev-parse", "HEAD"])
    TIMESTAMP = subprocess.check_output(["date", "+%Y%m%d-%H%M%S"])
    VERSION = "{timestamp}-{commit}".format(timestamp=TIMESTAMP, commit=COMMIT)

    KEY_PREFIX = "dev/{application}".format(application=APPLICATION)
    KEY = "{prefix}/{version}.zip".format(prefix=KEY_PREFIX, version=VERSION)

    # Upload to S3

    bucket = s3.get_bucket(BUCKET)
    key = bucket.new_key(KEY)
    key.set_contents_from_filename('deploy.zip')

    # Create version

    beanstalk.create_application_version(application_name=APPLICATION_NAME, version_label=VERSION, s3_bucket=BUCKET, s3_key=KEY)

    # Deploy

    beanstalk.update_environment(environment_name=LIVE_ENVIRONMENT_NAME, version_label=VERSION)


@rubberjack.command()
@click.pass_context
def promote(ctx):
    """
    Do the actual deployment work.

    (See the module-level docstring for more details and caveats)
    """

    _logger.info("Promoting {application} dev version to live".format(application=APPLICATION))

    # Setup Boto

    beanstalk = boto.beanstalk.layer1.Layer1(region=region_from_name(REGION))

    # Get environments

    response = beanstalk.describe_environments(application_name=APPLICATION_NAME)

    environments = response['DescribeEnvironmentsResponse']['DescribeEnvironmentsResult']['Environments']

    # Determine versions

    dev_version = None
    live_version = None
    for environment in environments:
        if environment['EnvironmentName'] == LIVE_ENVIRONMENT_NAME:
            live_version = environment['VersionLabel']
        if environment['EnvironmentName'] == DEV_ENVIRONMENT_NAME:
            dev_version = environment['VersionLabel']
    assert live_version is not None
    assert dev_version is not None

    # Bail if NOOP

    if live_version == dev_version:
        _logger.warn("{version} is already live!".format(version=live_version))
        sys.exit(1)

    # Do the things

    _logger.info("Deploying {new_version} for {app} live, replacing {old_version}!".format(new_version=dev_version, app=APPLICATION_NAME, old_version=live_version))

    beanstalk.update_environment(environment_name=LIVE_ENVIRONMENT_NAME, version_label=dev_version)
