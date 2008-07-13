# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

from fflashex.release import *

packages=find_packages()
package_data = find_package_data(where='fflashex',
    package='fflashex')

setup(
    name = name,
    version = version,
    
    description = description,
    author = author,
    author_email = email,
    url = url,
    download_url = download_url,
    license = license,

    install_requires = [
        "TurboGears >= 1.0.3.3",
    ],
    zip_safe = False,
    packages = packages,
    package_data = package_data,
    keywords = [
        'turbogears.app',
    ],
    classifiers = [
        'Development Status :: 3 - Beta',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: TurboGears',
        'Framework :: TurboGears :: Applications',
    ],
    test_suite = 'nose.collector',
    entry_points = {
        'console_scripts': [
            'start-fflashex = fflashex.commands:start',
        ],
    },
    # Uncomment next line and create a default.cfg file in your project dir
    # if you want to package a default configuration in your egg.
    data_files = [('config', ['default.cfg'])],
)
