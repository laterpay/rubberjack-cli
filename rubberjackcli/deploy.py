"""
Deploy a zipfile to Elastic Beanstalk.

Assumes something else has made the zip, which will be at ./deploy.zip, and makes many assumptions about environments and S3 config.

Also full of hard-coded config and duplication, for now.
"""

import boto
import boto.beanstalk.layer1
import subprocess

from .config import *  # noqa


def deploy():
    """
    Do the actual deployment work.

    (See the module-level docstring for more details and caveats)
    """

    # Setup Boto

    beanstalk = boto.beanstalk.layer1.Layer1(region=region)
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


if __name__ == '__main__':  # pragma: no cover
    deploy()
