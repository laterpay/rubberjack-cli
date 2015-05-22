#!/bin/bash

set -x
set -e

ORG=laterpay
REGION=eu-central-1
APPLICATION=dummyapp

AWS="aws --region $REGION"
#AWS="${AWS} --profile rubberjack"

APPLICATION_NAME=${ORG}-${APPLICATION}
DEV_ENVIRONMENT_NAME=${APPLICATION_NAME}-dev
LIVE_ENVIRONMENT_NAME=${APPLICATION_NAME}-live

# Sorry for the jq
# Pseudocode: the environment in result['Environments'] with EnvironmentName==DEV_ENVIRONMENT_NAME; the VersionLabel of that
VERSION_LABEL=$($AWS elasticbeanstalk describe-environments --application-name ${APPLICATION_NAME} | jq --raw-output ".Environments | map(select(.EnvironmentName==\"${DEV_ENVIRONMENT_NAME}\"))[].VersionLabel")

echo "Deploying $VERSION_LABEL for $APPLICATION_NAME live!"

$AWS elasticbeanstalk update-environment --environment-name $LIVE_ENVIRONMENT_NAME --version-label ${VERSION_LABEL}
