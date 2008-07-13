# -*- coding: UTF-8 -*-

import os

from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

from imaptofeed.release import *

packages = find_packages()
package_data = find_package_data(where='imaptofeed', package='imaptofeed')
if os.path.isdir('locales'):
    packages.append('locales')
    package_data.update(
        find_package_data(where='locales', exclude=('*.po',), 
        only_in_packages=False))

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
    keywords=keywords,
    classifiers=classifiers,

    install_requires = [
      "TurboGears[standard] >= 1.0.3.2",
      "python-dateutil",
    ],

    entry_points = """\
[console_scripts]
imap2feed-start = imaptofeed.commands:start
""",
    zip_safe=False,
    packages=packages,
    package_data=package_data,
    data_files = [('config', ['default.cfg'])],
    test_suite = 'nose.collector',
)
