"""
Common config values for rubberjack-cli.
"""

import boto

ORGANISATION = "laterpay"
REGION = "eu-central-1"
APPLICATION = "devnull"

APPLICATION_NAME = "{organisation}-{application}".format(organisation=ORGANISATION, application=APPLICATION)
DEV_ENVIRONMENT_NAME = "{application_name}-dev".format(application_name=APPLICATION_NAME)
LIVE_ENVIRONMENT_NAME = "{application_name}-live".format(application_name=APPLICATION_NAME)

BUCKET = "{organisation}-rubberjack-ebdeploy".format(organisation=ORGANISATION)

# Select region

regions = boto.beanstalk.regions()
region = None
for r in regions:
    if r.name == REGION:
        region = r
assert r is not None
