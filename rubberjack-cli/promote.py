import boto.beanstalk.layer1

ORGANISATION = "laterpay"
REGION = "eu-central-1"
APPLICATION = "peacock"

APPLICATION_NAME = "{organisation}-{application}".format(organisation=ORGANISATION, application=APPLICATION)
DEV_ENVIRONMENT_NAME = "{application_name}-dev".format(application_name=APPLICATION_NAME)
LIVE_ENVIRONMENT_NAME = "{application_name}-live".format(application_name=APPLICATION_NAME)

# Sorry for the jq
# Pseudocode: the environment in result['Environments'] with EnvironmentName==DEV_ENVIRONMENT_NAME; the VersionLabel of that
# VERSION_LABEL=$($AWS elasticbeanstalk describe-environments --application-name ${APPLICATION_NAME} | jq --raw-output ".Environments | map(select(.EnvironmentName==\"${DEV_ENVIRONMENT_NAME}\"))[].VersionLabel")

regions = boto.beanstalk.regions()
region = regions[7]  # Should be eu-central-1; this is a horrible hack I can't work out how to do better easily

beanstalk = boto.beanstalk.layer1.Layer1(region=region)

environments = beanstalk.describe_environments(application_name=APPLICATION_NAME)

import pprint
pprint.pprint(environments)

# echo "Deploying $VERSION_LABEL for $APPLICATION_NAME live!"

# $AWS elasticbeanstalk update-environment --environment-name $LIVE_ENVIRONMENT_NAME --version-label ${VERSION_LABEL}
