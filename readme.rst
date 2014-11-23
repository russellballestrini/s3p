s3p
###

Use AWS S3 as a release pipeline.  Use code to inforce process and promote releases.

Install
=======

.. code-block:: bash

  pip install s3p

or clone this repo.

Getting Started
===============

To get started:

1. set the environment vars:

   **AWS_ACCESS_KEY_ID**
     Access key

   **AWS_SECRET_ACCESS_KEY**
     Secret key

   **AWS_S3_BUCKET**
     Bucket used for storing releases

   **AWS_S3_RANKS**
     Coma separated string of ordered ranks used for promotion

     For example:

     .. code-block:: bash

       AWS_S3_RANKS="qa, staging, production"


2. test:

   .. code-block:: bash

    s3p rev2.tar.gz staging
    error="could not promote, trying to skip rank?"

    s3p my.tar.gz qa
    success="promoted my.tar.gz to qa"

    s3p my.tar.gz staging
    success="promoted my.tar.gz to staging"

    s3p my.tar.gz production
    success="promoted my.tar.gz to production"

Promoting to the first rank will cause an upload or update.
Promoting to subsequent ranks will copy from the previous rank.

Pass an optional release number, version, commit hash or identifier string:

  .. code-block:: bash

   s3p my.tar.gz qa --version=839de03f972e8182

Instead of blindly clobbering files, s3promote will use the version
to safely and automatically archive them.

Build a release pipeline with code. Review S3Promote class for details.

Usage
=======

.. code-block:: bash

 usage: s3p filepath rank
 
 Promote files through the release ranks
 
 positional arguments:
   filepath
   rank
 
 optional arguments:
   -h, --help         show this help message and exit
   --version VERSION  set version identifier, timestamp, md5, commit hash, etc
   --download PATH    download file from rank to PATH
   --get-version      get version identifier from rank

Classes
==========

Provides the following classes for you to extend (although not nessasary):

**S3Pipeline**:
  Represents a releases pipeline (object) in S3.
  Acts like boto.s3.bucket.Bucket through composition.

  For more details:
  
  .. code-block:: python

    from s3p import S3Pipeline
    help(S3Pipeline)

**S3Release**:
  Represents a release (object) in an S3Pipeline.
  Acts like boto.s3.key.Key through composition.

  For more details:
  
  .. code-block:: python

    from s3p import S3Release
    help(S3Release)

