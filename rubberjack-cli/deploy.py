#!/bin/bash

set -x
set -e

ORG=laterpay
REGION=eu-central-1
APPLICATION=dummyapp

COMMIT=$(git rev-parse HEAD)
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
VERSION=${TIMESTAMP}-${COMMIT}

AWS="aws --region $REGION"
BUCKET=${ORG}-rubberjack-ebdeploy
KEY_PREFIX=dev/${APPLICATION}
KEY=${KEY_PREFIX}/${VERSION}.zip

APPLICATION_NAME=${ORG}-${APPLICATION}
ENVIRONMENT_NAME=${APPLICATION_NAME}-dev

rm -f deploy.zip
rm -rf _site

zip -r deploy.zip ./* .ebextensions
$AWS s3 cp deploy.zip "s3://${BUCKET}/${KEY}"
$AWS elasticbeanstalk create-application-version --application-name $APPLICATION_NAME --version-label "$VERSION" --source-bundle "S3Bucket=${BUCKET},S3Key=${KEY}"
$AWS elasticbeanstalk update-environment --environment-name $ENVIRONMENT_NAME --version-label "$VERSION"
