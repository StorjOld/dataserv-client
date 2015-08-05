#!/usr/bin/env python
# coding: utf-8


import os
from setuptools import setup, find_packages

if os.name == 'nt':  # windows
    import py2exe  # manual dependencie :/


THISDIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(THISDIR)


VERSION = "1.0.8" # FIXME get from module
DOWNLOAD_BASEURL = "https://pypi.python.org/packages/source/a/dataserv-client/"
DOWNLOAD_URL = DOWNLOAD_BASEURL + "dataserv-client-%s.tar.gz" % VERSION


setup(
    name='dataserv-client',
    version=VERSION,
    description='',
    long_description=open("README.rst").read(),
    keywords=(""),
    url='http://storj.io',
    author='Shawn Wilkinson',
    author_email='shawn+dataserv-client@storj.io',
    license='MIT',
    packages=find_packages(exclude=['dataserv_client.bin']),
    scripts=[os.path.join('dataserv_client', 'bin', 'dataserv-client.py')],
    download_url = DOWNLOAD_URL,
    test_suite="tests",
    install_requires=[
        'RandomIO == 0.2.1',
        'dataserv == 1.0.1',  # FIXME why do test only work when its here?
    ],
    tests_require=[
        'coverage',
        'coveralls'
    ],
    zip_safe=False,
    classifiers=[
        # "Development Status :: 1 - Planning",
        # "Development Status :: 2 - Pre-Alpha",
        "Development Status :: 3 - Alpha",
        # "Development Status :: 4 - Beta",
        # "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        #"Programming Language :: Python :: 2",
        #"Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    # py2exe
    console=[os.path.join('dataserv_client', 'bin', 'dataserv-client.py')],
    options = {'py2exe': {
        "optimize": 2,
        "bundle_files": 2, # This tells py2exe to bundle everything
    }}
)
