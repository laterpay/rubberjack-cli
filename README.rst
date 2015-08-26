rubberjack-cli
==============

.. image:: https://travis-ci.org/laterpay/rubberjack-cli.svg?branch=feature%2Ftravis
       :target: https://travis-ci.org/laterpay/rubberjack-cli

Command-line tooling for
`RubberJack <https://github.com/laterpay/rubberjack>`__

sigv4
-----

http://stackoverflow.com/q/27400105/928098

TL;DR ``eu-central-1`` only supports the new V4 signature algorithm.

Currently the support for this is...unpleasant but working:

Use ``--sigv4-host s3.eu-central-1.amazonaws.com`` or similar for other
environments.
