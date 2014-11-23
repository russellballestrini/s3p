s3p
###

Use AWS S3 as a release pipeline.  Use code to inforce process and promote releases.

Install
=======

.. code-block:: bash

  pip install s3p

or clone this repo and run,

.. code-block:: bash

  pip install --upgrade .

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

  s3p promote my.tar.gz staging
  error="could not promote, trying to skip rank?"

  s3p promote my.tar.gz qa
  success="promoted my.tar.gz version 141676372407 to qa rank"

  s3p promote my.tar.gz staging
  success="promoted my.tar.gz version 141676372407 to staging rank"

  s3p promote my.tar.gz production
  success="promoted my.tar.gz version 141676372407 to production rank"

* Promoting to the first rank will cause an upload or update.
* Promoting to subsequent ranks will copy from the previous rank.

Pass an optional release number, version, commit hash or identifier string:

.. code-block:: bash

 s3p promote my.tar.gz qa 0.1.1
 success="promoted my.tar.gz version 0.1.1 to qa rank"

 s3p promote my.tar.gz staging
 success="promoted my.tar.gz version 0.1.1 to staging rank"

Instead of blindly clobbering files, *s3p promote* always creates a copy
of the file under the archive area in the pipeline using the version id.


Subcommands
===========

There are a number of subcommands that interface with the pipeline.

version
-------

**s3p version --help**

.. code-block:: text

  usage: s3p version filepath [rank]

  positional arguments:
    filepath    filename or filepath
    rank        position in pipeline

promote
-------

**s3p promote --help**

.. code-block:: text

  usage: s3p promote filepath rank [version]

  Promote releases through pipeline ranks.

  positional arguments:
    filepath    filename or filepath
    rank        position in pipeline
    version     version identifier, timestamp, md5, commit hash, etc

download
--------

**s3p download --help**

.. code-block:: text

  usage: s3p download filepath rank [download_path]

  Download release from rank to local filesystem.

  positional arguments:
    filepath       filename or filepath
    rank           position in pipeline
    download_path  location to download file to


Classes
==========

Build a release pipeline with code. Review S3Promote and S3Release classes:

**S3Pipeline**:
  Represents a release pipeline (object) in S3.
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

