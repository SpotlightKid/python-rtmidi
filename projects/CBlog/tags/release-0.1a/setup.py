# -*- coding: UTF-8 -*-

from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

import os
from cblog.release import *

setup(
    name=name,
    version=version,

    description=description,
    long_description=long_description,
    author=author,
    author_email=email,
    url=url,
    download_url=download_url,
    license=license,
    platform=platform,
    keywords = keywords,
    classifiers = classifiers,

    install_requires = [
      "TurboGears >= 1.0b2",
      "Cheetah >= 2.0rc6",
      "docutils >= 0.4",
      "pysqlite >= 2.2",
      "textile >= 2.0.11",
      "python-dateutil",
      "simplejson",
      "cElementTree",
    ],

    entry_points = """\
[console_scripts]
cblog-start = cblog.commands:start
""",
    zip_safe=False,
    packages=find_packages(),
    package_data = find_package_data(where='cblog',
      package='cblog', show_ignored=True),
    test_suite = 'nose.collector',
    )
