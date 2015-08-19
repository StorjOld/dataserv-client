#!/usr/bin/env python
# coding: utf-8


import os
from setuptools import setup, find_packages


if os.name == 'nt':  # windows
    import py2exe  # manual dependencie :/


VERSION = "1.3.0"  # FIXME get from module
SCRIPT = os.path.join('dataserv_client', 'bin', 'dataserv-client')
DOWNLOAD_URL = "%(baseurl)s/%(name)s/%(name)s-%(version)s.tar.gz" % {
    'baseurl': "https://pypi.python.org/packages/source/a",
    'name': 'dataserv-client',
    'version': VERSION
}


setup(
    app=[SCRIPT],
    name='dataserv-client',
    description="",
    long_description=open("README.rst").read(),
    keywords="",
    url='http://storj.io',
    author='Shawn Wilkinson',
    author_email='shawn+dataserv-client@storj.io',
    license="MIT",
    version=VERSION,
    scripts=[SCRIPT],  # FIXME esky scripts=[script],
    console=[SCRIPT],
    data_files=[],
    test_suite="tests",
    install_requires=[
        'RandomIO == 0.2.1',
        'partialhash == 1.1.0',
        'future == 0.15.0',  # for python 2.7 support
    ],
    tests_require=[
        'coverage',
        'coveralls',
        'mock'
    ],
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
    ],

    # py2exe
    options = {'py2exe': {
        "optimize": 2,
        "bundle_files": 2, # This tells py2exe to bundle everything
    }}
)
