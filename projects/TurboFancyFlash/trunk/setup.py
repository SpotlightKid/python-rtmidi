from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

from fancyflash.release import *

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

    install_requires = ["TurboGears >= 1.0.3.3"],
    zip_safe = False,
    packages = find_packages(),
    package_data = find_package_data(where='fancyflash',
        package='fancyflash'),
    keywords = [
        'turbogears.extension',
        'turbogears.widgets',
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: TurboGears',
        'Framework :: TurboGears :: Widgets',
    ],
    entry_points = """
    [turbogears.widgets]
    turbofancyflash = fancyflash.widgets
    """,
    test_suite = 'nose.collector',
)
