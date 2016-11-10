rubberjack-cli
==============

.. image:: https://travis-ci.org/laterpay/rubberjack-cli.svg?branch=feature%2Ftravis
       :target: https://travis-ci.org/laterpay/rubberjack-cli

Command-line tooling for RubberJack!

RubberJack manages `Elastic
Beanstalks <https://aws.amazon.com/elasticbeanstalk/>`__

Vision
------

Here's a pretty vanilla "deploy to Elastic Beanstalk" script:

.. code:: bash

    #!/bin/bash

    set -x

    COMMIT=$(git rev-parse HEAD)
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    VERSION=${TIMESTAMP}-${COMMIT}

    REGION=eu-central-1

    AWS="aws --region $REGION"
    BUCKET=laterpay-rubberjack-ebdeploy
    KEY_PREFIX=dev/peacock
    KEY=${KEY_PREFIX}/${VERSION}.zip

    APPLICATION_NAME=laterpay-peacock
    ENVIRONMENT_NAME=laterpay-peacock-dev

    rm -f deploy.zip
    rm -rf _site

    zip -r deploy.zip *
    $AWS s3 cp deploy.zip s3://${BUCKET}/${KEY}
    $AWS elasticbeanstalk create-application-version --application-name $APPLICATION_NAME --version-label $VERSION --source-bundle S3Bucket=${BUCKET},S3Key=${KEY}
    $AWS elasticbeanstalk update-environment --environment-name $ENVIRONMENT_NAME --version-label $VERSION

That's full of config (bucket name, environment name, application name,
region), and full of opinions (bucket path, version naming, environment
usage)

Also it requires the deployer to have access to the S3 bucket and the EB
app.

RubberJack aims to centralise this. Imagine instead:

::

    #!/bin/bash

    rubberjack deploy --application laterpay-peacock deploy.zip

There ``rubberjack-cli`` uploads the zip to rubberjack, and rubberjack
then:

-  Uploads the zip to S3
-  Knows about the application's region
-  Updates the application's dev environment to that which was pushed
-  Provides an API / GUI for promoting versions from the dev environment
   to staging/production
-  Provides an API / GUI for editing application config

Why not just provide a CLI? These are the AWS IAM permissions for "full
Elastic Beanstalk access" (which you need to deploy):

::

    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Action": [
            "elasticbeanstalk:*",
            "ec2:*",
            "elasticloadbalancing:*",
            "autoscaling:*",
            "cloudwatch:*",
            "s3:*",
            "sns:*",
            "cloudformation:*",
            "rds:*",
            "sqs:*",
            "iam:PassRole"
          ],
          "Resource": "*"
        }
      ]
    }

I'm not about to embed AWS access keys that give that level of
permission, in every CircleCI build I have.

Giving *one service* those permissions however, and then having the CLI
tool just upload to S3 / POST to the service, gives me a lot less
concern.

FAQ
~~~

Isn't this exactly what the EB console / EB API does?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There's big overlap, yes; a significant challenge will be in trying to
add "opinions" without duplicating excessive amounts of functionality.

Ideally RubberJack would make console use for day-to-day EB operations
obsolete. Until that point is reached, the console is a great fallback.

For example, an initial version will probably just be a CLI wrapper
around ``awscli`` to upload to S3, and a tiny tiny service to do the
Elastic Beanstalk deployment work; lots of room for more things to be
done, but a useful starting point.


sigv4
-----

http://stackoverflow.com/q/27400105/928098

TL;DR ``eu-central-1`` only supports the new V4 signature algorithm.

Currently the support for this is...unpleasant but working:

Use ``--sigv4-host s3.eu-central-1.amazonaws.com`` or similar for other
environments.
