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
import boto.s3.connection
import click

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


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
@click.option('--application', help="TODO", default="devnull")
@click.option('--organisation', help="TODO", default="laterpay")
@click.option('--region', help="TODO", default="eu-central-1")
@click.option('--sigv4-host', help="TODO", default=None)
@click.pass_context
def rubberjack(ctx, application, organisation, region, sigv4_host):
    """
    Main entry point into the rubberjack CLI.
    """

    ctx.obj = {}

    ctx.obj['application'] = application
    ctx.obj['organisation'] = organisation
    ctx.obj['region'] = region_from_name(region)
    ctx.obj['application_name'] = application_name = "{organisation}-{application}".format(organisation=organisation, application=application)

    ctx.obj['dev_environment_name'] = "{application_name}-dev".format(application_name=application_name)
    ctx.obj['live_environment_name'] = "{application_name}-live".format(application_name=application_name)

    ctx.obj['bucket'] = "{organisation}-rubberjack-ebdeploy".format(organisation=organisation)

    # boto doesn't use a default of None, it uses NoHostProvided, and I struggled to pass that myself
    if sigv4_host:
        s3 = boto.connect_s3(host=sigv4_host)
    else:
        s3 = boto.connect_s3()
    ctx.obj['s3'] = s3
    ctx.obj['beanstalk'] = boto.beanstalk.layer1.Layer1(region=ctx.obj['region'])


@rubberjack.command()
@click.option('--environment', default=None)
@click.argument('filename', default="./deploy.zip", type=click.Path(exists=True))
@click.pass_context
def deploy(ctx, environment, filename):
    """
    Do the actual deployment work.

    (See the module-level docstring for more details and caveats)
    """

    APPLICATION = ctx.obj['application']
    beanstalk = ctx.obj['beanstalk']
    s3 = ctx.obj['s3']

    if not environment:
        environment = ctx.obj['dev_environment_name']

    _logger.info("Deploying {application} to {environment}".format(application=APPLICATION, environment=environment))

    # Extract deployable info

    COMMIT = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip()
    TIMESTAMP = subprocess.check_output(["date", "+%Y%m%d-%H%M%S"]).strip()
    VERSION = "{timestamp}-{commit}".format(timestamp=TIMESTAMP, commit=COMMIT)

    KEY_PREFIX = "dev/{application}".format(application=APPLICATION)
    KEY = "{prefix}/{version}.zip".format(prefix=KEY_PREFIX, version=VERSION)

    # Upload to S3

    bucket = s3.get_bucket(ctx.obj['bucket'])
    key = bucket.new_key(KEY)
    key.set_contents_from_filename(filename)

    # Create version

    beanstalk.create_application_version(application_name=ctx.obj['application_name'], version_label=VERSION, s3_bucket=ctx.obj['bucket'], s3_key=KEY)

    # Deploy

    beanstalk.update_environment(environment_name=environment, version_label=VERSION)


@rubberjack.command()
@click.option('--to-environment', default=None)
@click.pass_context
def promote(ctx, to_environment):
    """
    Do the actual deployment work.

    (See the module-level docstring for more details and caveats)
    """

    beanstalk = ctx.obj['beanstalk']
    APPLICATION = ctx.obj['application']
    APPLICATION_NAME = ctx.obj['application_name']
    DEV_ENVIRONMENT_NAME = ctx.obj['dev_environment_name']
    LIVE_ENVIRONMENT_NAME = ctx.obj['live_environment_name']

    if to_environment is None:
        to_environment = LIVE_ENVIRONMENT_NAME

    _logger.info("Promoting {application} dev version to {to_environment}".format(application=APPLICATION, to_environment=to_environment))

    # Get environments

    response = beanstalk.describe_environments(application_name=APPLICATION_NAME)

    environments = response['DescribeEnvironmentsResponse']['DescribeEnvironmentsResult']['Environments']

    # Determine versions

    dev_version = None
    live_version = None
    for environment in environments:
        if environment['EnvironmentName'] == to_environment:
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
