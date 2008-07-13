from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

from firebug.release import *

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
    keywords=keywords,
    classifiers=classifiers,

    install_requires = ["TurboGears >= 1.0b2"],
    zip_safe=False,
    packages=find_packages(),
    package_data = find_package_data(where='firebug',
                                     package='firebug'),
    entry_points = """
    [turbogears.widgets]
    firebug = firebug.widgets
    """
)
