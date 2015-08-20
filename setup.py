#!/usr/bin/env python
# coding: utf-8


# unavoidable dependencie for setup.py, get latest version from github
# pip install git+git://github.com/cloudmatrix/esky.git
from esky import bdist_esky


import os
from setuptools import setup, find_packages


exec(open('dataserv_client/version.py').read())  # load __version__
SCRIPT = os.path.join('dataserv_client', 'bin', 'dataserv-client')
DOWNLOAD_URL = "%(baseurl)s/%(name)s/%(name)s-%(version)s.tar.gz" % {
    'baseurl': "https://pypi.python.org/packages/source/a",
    'name': 'dataserv-client',
    'version': __version__  # NOQA
}


setup(
    name='dataserv-client',
    description="Client for storing and auditing data. http://storj.io",
    long_description=open("README.rst").read(),
    keywords="",
    url='http://storj.io',
    author='Shawn Wilkinson',
    author_email='shawn+dataserv-client@storj.io',
    license="MIT",
    version=__version__,
    scripts=[SCRIPT],
    test_suite="tests",
    install_requires=open("requirements.txt").readlines(),
    tests_require=[],  # use `pip install -r test_requirements.txt`
    download_url=DOWNLOAD_URL,
    packages=find_packages(exclude=['dataserv_client.bin']),
    classifiers=[
        # "Development Status :: 1 - Planning",
        "Development Status :: 2 - Pre-Alpha",
        # "Development Status :: 3 - Alpha",
        # "Development Status :: 4 - Beta",
        # "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
