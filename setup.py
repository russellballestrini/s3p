# installation: pip install s3p
from setuptools import setup

with open('requirements.txt', 'r') as f:
    requires = [line.strip() for line in f]

setup( 
    name = 's3p',
    version = '0.1.0',
    description = 's3p: Create process by promoting releases in an AWS S3 pipeline',
    keywords = 's3p process pipeline promote release',
    long_description = open('readme.rst').read(),

    author = 'Russell Ballestrini',
    author_email = 'russell@ballestrini.net',
    url = 'https://github.com/russellballestrini/s3promote',

    platforms = ['All'],
    license = 'Public Domain',

    packages = ['s3p'],

    install_requires = requires,
    entry_points = {
      'console_scripts': ['s3p=s3p.cli:main',],
    },
)

"""
setup()
  keyword args: http://peak.telecommunity.com/DevCenter/setuptools

configure pypi username and password in ~/.pypirc::

 [pypi]
 username:
 password:

build and upload to pypi with this::

 python setup.py sdist bdist_egg register upload
"""
