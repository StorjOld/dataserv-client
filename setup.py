import os

from esky import bdist_esky
from setuptools import setup, find_packages

VERSION = "1.2.1"  # FIXME get from module
SCRIPT = os.path.join('dataserv_client', 'bin', 'dataserv-client')
DOWNLOAD_URL = "%(baseurl)s/%(name)s/%(name)s-%(version)s.tar.gz" % {
    'baseurl': "https://pypi.python.org/packages/source/a",
    'name': 'dataserv-client',
    'version': VERSION
}


# FIXME get autoupdate with esky working
## windows
# if sys.platform in ['win32', 'cygwin', 'win64']:
#    icon = os.path.join(sys.prefix, "DLLs", "py.ico")
#    script = Executable(SCRIPT, icon=icon, gui_only=False)
#    options = {
#        "bdist_esky": {
#            "includes": [],  # include modules
#            "excludes": ["pydoc"],  # exclude modules
#            "freezer_module": "py2exe",
#            #"freezer_module": "cx_Freeze",
#        }
#    }
#
#
## mac (untested)
# if sys.platform == 'darwin':
#    script = Executable(SCRIPT)
#    options = {
#        "bdist_esky": {
#            "includes": [],  # include modules
#            "excludes": ["pydoc"],  # exclude modules
#            "freezer_module": "py2app",
#            "freezer_options": {
#                "plist": {
#                    #"LSUIElement" : True,
#                    #'CFBundleIdentifier': 'de.cloudmatrix.esky',
#                    #'CFBundleIconFile' : 'images/box.icns',
#                }
#            },
#        }
#    }
#
#
## linux
# if sys.platform in ['linux', 'linux2']:
#    script = Executable(SCRIPT)
#    options = {
#        "bdist_esky": {
#            "includes": [],  # include modules
#            "excludes": ["pydoc"],  # exclude modules
#            "freezer_module": "bbfreeze",  # FIXME unmaintained only python 2
#            # "freezer_module": "cx_Freeze", # FIXME pip install fails
#        }
#    }


setup(
    #app=[SCRIPT],
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
    # FIXME esky options=options,
    #console=[SCRIPT],
    #data_files=[],
    test_suite="tests",
    install_requires=[
        'RandomIO == 0.2.1',
        'future == 0.15.0',  # for python 2.7 support
        'partialhash == 1.1.0'
    ],
    tests_require=[
        'coverage',
        'coveralls'
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
)
