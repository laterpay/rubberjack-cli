"""
Promote a version from a dev EB environment to live.

Makes many assumptions about environments and S3 config.

Also full of hard-coded config and duplication, for now.
"""

import boto.beanstalk.layer1
import sys

from .config import *  # noqa


def promote():
    """
    Do the actual deployment work.

    (See the module-level docstring for more details and caveats)
    """

    # Setup Boto

    beanstalk = boto.beanstalk.layer1.Layer1(region=region)

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
        print("{version} is already live!".format(version=live_version))
        sys.exit(1)

    # Do the things

    print("Deploying {new_version} for {app} live, replacing {old_version}!".format(new_version=dev_version, app=APPLICATION_NAME, old_version=live_version))

    beanstalk.update_environment(environment_name=LIVE_ENVIRONMENT_NAME, version_label=dev_version)
