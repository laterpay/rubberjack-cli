"""
Deploy a zipfile to Elastic Beanstalk.

Assumes something else has made the zip, which will be at ./deploy.zip, and makes many assumptions about environments and S3 config.

Also full of hard-coded config and duplication, for now.
"""

import boto
import boto.beanstalk.layer1
import subprocess

ORGANISATION = "laterpay"
REGION = "eu-central-1"
APPLICATION = "devnull"

APPLICATION_NAME = "{organisation}-{application}".format(organisation=ORGANISATION, application=APPLICATION)
DEV_ENVIRONMENT_NAME = "{application_name}-dev".format(application_name=APPLICATION_NAME)
LIVE_ENVIRONMENT_NAME = "{application_name}-live".format(application_name=APPLICATION_NAME)

# Select region

regions = boto.beanstalk.regions()
region = None
for r in regions:
    if r.name == REGION:
        region = r
assert r is not None

# Setup Boto

beanstalk = boto.beanstalk.layer1.Layer1(region=region)
s3 = boto.connect_s3()

# Extract deployable info

COMMIT = subprocess.check_output(["git", "rev-parse", "HEAD"])
TIMESTAMP = subprocess.check_output(["date", "+%Y%m%d-%H%M%S"])
VERSION = "{timestamp}-{commit}".format(timestamp=TIMESTAMP, commit=COMMIT)

BUCKET = "{organisation}-rubberjack-ebdeploy".format(organisation=ORGANISATION)
KEY_PREFIX = "dev/{application}".format(application=APPLICATION)
KEY = "{prefix}/{version}.zip".format(prefix=KEY_PREFIX, version=VERSION)

# Upload to S3

bucket = s3.get_bucket(BUCKET)
key = s3.new_key(KEY)
key.set_contents_from_filename('deploy.zip')

# Create version

beanstalk.create_application_version(application_name=APPLICATION_NAME, version_label=VERSION, s3_bucket=BUCKET, s3_key=KEY)

# Deploy

beanstalk.update_environment(environment_name=LIVE_ENVIRONMENT_NAME, version_label=VERSION)
