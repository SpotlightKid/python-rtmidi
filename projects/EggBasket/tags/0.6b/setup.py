# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

packages = find_packages()
package_data = find_package_data(where='eggbasket', package='eggbasket')
if os.path.isdir('locales'):
    packages.append('locales')
    package_data.update(find_package_data(where='locales',
        exclude=('*.po',), only_in_packages=False))

execfile('eggbasket/release.py')

setup(
    name = name,
    version = version,

    description = description,
    long_description = long_description,
    author = author,
    author_email = author_email,
    url = url,
    download_url = download_url,
    license = license,

    install_requires = [
        "TurboGears >= 1.0.4.4",
        "SQLAlchemy >= 0.4",
        "Genshi >= 0.4",
        "docutils >= 0.4",
    ],
    extras_require = {
        'admin':  ["dbsprockets"],
    },
    zip_safe = False,
    packages = packages,
    package_data = package_data,
    keywords = keywords,
    classifiers = classifiers,
    test_suite = 'nose.collector',
    entry_points = {
        'console_scripts': [
            'eggbasket-server = eggbasket.commands:main',
        ],
    },
    # Uncomment next line and create a default.cfg file in your project dir
    # if you want to package a default configuration in your egg.
    data_files = [('config', ['default.cfg'])],
)
