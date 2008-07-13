from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

import os
from bookmarker.release import *

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

    install_requires = [
        "TurboGears >= 1.0b1",
        "pysqlite >= 2.2",
        "TGFastData > 0.9a6"
    ],

    scripts = ["start-bookmarker.py"],
    zip_safe=False,
    packages=find_packages(),
    package_data = find_package_data(where='bookmarker', package='bookmarker'),
    include_package_data=True,
    keywords=keywords,
    classifiers=classifiers
)

