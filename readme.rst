S3 Pipeline
###########

Python libraries and scripts used to build and maintain release pipelines on AWS S3.

Classes
==========

Provides the following classes for you to extend (although not nessasary):

**S3Pipeline**:
  Represents a releases pipeline (object) in S3.
  Acts like boto.s3.bucket.Bucket through composition.

  For more details:
  
  .. code-block:: python

    from s3pipeline.pipeline import S3Pipeline
    help(S3Pipeline)

**S3Release**:
  Represents a release (object) in an S3Pipeline.
  Acts like boto.s3.key.Key through composition.

  For more details:
  
  .. code-block:: python

    from s3pipeline.release import S3Release
    help(S3Release)


To get started:

1. clone this repo
2. set the environment vars:

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


3. install dependencies, we suggest using a virtualenv:

   .. code-block:: bash

      pip install -r requirements

4. test:

   .. code-block:: bash

    python s3promote.py rev2.tar.gz staging
    error="could not promote, trying to skip rank?"

    python s3promote.py my.tar.gz qa
    success="promoted my.tar.gz to qa"

    python s3promote.py my.tar.gz staging
    success="promoted my.tar.gz to staging"

    python s3promote.py my.tar.gz production
    success="promoted my.tar.gz to production"

Promoting to the first rank will cause an upload or update.
Promoting to subsequent ranks will copy from the previous rank.

Pass an optional release number, version, commit hash or identifier string:

  .. code-block:: bash

   python s3promote.py my.tar.gz qa --version=839de03f972e8182

Instead of blindly clobbering files, s3promote will use the version
to safely and automatically archive them.

Build a release pipeline with code. Review S3Promote class for details.

Usage
=======

.. code-block:: bash

 usage: s3promote.py filepath rank
 
 Promote files through the release ranks
 
 positional arguments:
   filepath
   rank
 
 optional arguments:
   -h, --help         show this help message and exit
   --version VERSION  set version identifier, timestamp, md5, commit hash, etc
   --download PATH    download file from rank to PATH
   --get-version      get version identifier from rank
