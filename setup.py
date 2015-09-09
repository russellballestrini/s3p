
from setuptools import (
  setup,
  find_packages,
)

# read requirements.txt for requres, filter comments and newlines.
sanitize = lambda x : not x.startswith('#') and not x.startswith('\n')
with open('requirements.txt', 'r') as f:
    requires = filter(sanitize, f.readlines())

setup( 
    name = 's3p',
    version = '0.1.1',
    description = 's3p: Create process by promoting releases in an AWS S3 pipeline',
    keywords = 's3p process pipeline promote release',
    long_description = open('readme.rst').read(),

    author = 'Russell Ballestrini',
    author_email = 'russell@ballestrini.net',
    url = 'https://github.com/russellballestrini/s3p',

    platforms = ['All'],
    license = 'Public Domain',

    packages = find_packages(),

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
