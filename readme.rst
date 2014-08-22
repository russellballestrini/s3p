s3promote
#########

A Python application which uses boto to promote a file through
the ranks (release directories) on AWS S3.

to get started:

1. clone this repo
2. make sure you have set the environment vars:

   **AWS_ACCESS_KEY_ID**
     Access key

   **AWS_SECRET_ACCESS_KEY**
     Secret key

   **AWS_S3_BUCKET**
     Bucket used for storing releases

3. install dependencies, we suggest using a virtualenv:

   .. code-block:: bash

      pip install -r requirements

4. test:

   .. code-block:: bash

    python s3promote.py rev2.tar.gz staging
    error="could not promote, trying to skip rank?"

    python s3promote.py rev2.tar.gz qa
    success="promoted rev2.tar.gz to qa"

    python s3promote.py rev2.tar.gz staging
    success="promoted rev2.tar.gz to staging"

    python s3promote.py rev2.tar.gz production
    success="promoted rev2.tar.gz to production"

Promoting to the first rank will cause an upload or update however promoting to subsequent ranks will copy from the previous.

TODO: Ranks are hard coded, move to an environment variable?

  .. code-block:: python

    # valid ordered promotion ranks
    ranks = ['qa', 'staging', 'production']
