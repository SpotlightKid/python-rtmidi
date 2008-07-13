# Release information about EggBasket
# -*- coding: UTF-8 -*-
"""A simple, lightweight Python Package Index (aka Cheeseshop) clone.

Overview
--------

EggBasket_ is a web application which provides a service similar and compatible
to the `Python Package Index`_ (aka Cheeseshop). It allows you to maintain your
own local repository of Python packages required by your installations.

It is implemented using the TurboGears_ web framework, Genshi_ and SQLAlchemy_.

.. warning::
    This is still alpha-stage software. All the basic operations necessary
    to support a setuptools-based infrastructure are there, but some
    convenience features are missing and the software has not been tested
    extensively. **Use at your own risk!**


Features
--------

* Can be used by setuptools/easy_install as the package index and repository.

* Supports the distutils ``upload`` protocol.

* Has a simple role-based permission system to restrict package uploads (but see
  TODO).

* Requires only SQLite as the database system (included with Python 2.5).

* Is able to read and display meta data from the following distribution package
  formats (source and binary):

  ``.egg``, ``.tar``, ``.tar.bz2``, ``.tar.gz``, ``.tgz``, ``.zip``

* Any other file format can be configured to be listed under the distribution
  files for a package (by default this includes ``.exe`` and ``.rpm`` and
  ``.tar.Z`` files in addition to the filetypes listed above).

* Can be run without any configuration by just starting it from within a
  directory containing package directories (see "Usage").


Todo
----

* Improve permission system to allow closed-shop repositories on an open
  network or uploading for anonymous users.
* Add support for MD5 check sums and GPG signatures.
* Add more error and sanity checks to the upload handling.
* Add pagination to the main package list.
* Support deletion of packages through web interface.
* Cache package listings and meta data.
* Improve DBmechanic-based admin interface for adding users and groups and
  setting configuration values (currently disabled by default).


Acknowledgments
---------------

This application is a re-implementation (almost no shared code) of the
haufe.eggserver_ Grok application with some improvements.


Installation
------------

To install EggBasket_ from the Cheeseshop_ use `easy_install`_::

    [sudo] easy_install EggBasket

This requires the setuptools_ package to be installed. If you have not done so
already, download the `ez_setup.py`_ script and run it to install setuptools.


Usage
-----

* Your packages should all reside under a common root directory, with a
  sub-directory for each package with the same base name as the distribution.
  The sub-directories should each contain the egg files and source archives for
  all available versions of the package. The package diretories will be created
  by the application when using the upload command (see below).

* To start the application server, open a terminal, change to the directory
  which contains the packages and then run::

    eggbasket-server [<config file>]

  You can also set the location of the package root directory in the
  configuration with the ``eggbasket.package_root`` setting and start the
  server anywhere you want.

  If no configuration file is specified on the command line, the default
  configuration file included in the egg will be used. The default
  configuration file can also be found in the source distribution and be
  adapted for your environment.

  The server either needs write permissions to directory where it is started,
  or you need to change the path of the database and the access log in the
  configuration so they can be written by the server.

* To stop the server just hit ``Control-C`` in the terminal or kill the process.

* You can look at the package index with your web browser by opening the URL
  ``http://localhost:3442/``. The default port ``3442`` can be changed by
  setting the ``server.socket_port`` option in the configuration file.

* You can instruct easy_install_ to search & download packages from your
  package repository by specifying the URL to your server with the ``-i``
  option::

    easy_install -i http://localhost:8080/ PACKAGE_NAME

* Additionally, it might be necessary to restrict the hosts from which
  easy_install will download to your EggBasket server with the ``-H`` option::

    easy_install -H 'localhost:3442' ...

* You can also set the ``eggbasket.rewrite_download_url`` resp.
  ``eggbasket.rewrite_homepage_url`` settings in the configuration to ``True``
  and EggBasket will replace the download resp. homepage URL of each package
  in the package meta data view with the URL of the package distribution files
  listing on the EggBasket server.

* You can upload a package to your repository with the distutils ``upload``
  command, for example::

    python setup.py bdist_egg upload -r http://localhost:3442/upload

  This command will ask for your username and password on the server. You can
  store these and the repository URL in your ``.pypirc`` file. See the
  `distutils documentation`_ for more information.

* By default, uploading is restricted to users in a group that has the
  ``upload`` permission. You can create an appropriate user, group and
  permission in the database by giving the ``--init`` option to the
  ``eggbasket-server`` command::

    eggbasket-server --init [<config file>]

  This will create a user with user_name/password "admin", who belongs to the
  group "maintainer", which has the "upload" permission. The database to use
  will be read from the config file.

  See the TurboGears documentation on Identity_ for background information.

* Of course you can always just copy package distribution files manually in the
  filesystem to your repository or upload them to the appropriate place with
  ``scp`` etc. The application will find and list new files without the need to
  "register" them as is necessary with the original PyPI.


.. _turbogears: http://www.turbogears.org/
.. _genshi: http://genshi.edgewall.org/
.. _sqlalchemy: http://www.sqlalchemy.org/
.. _haufe.eggserver: http://cheeseshop.python.org/pypi/haufe.eggserver
.. _eggbasket: http://chrisarndt.de/projects/eggbasket/
.. _cheeseshop:
.. _python package index: http://cheeseshop.python.org/pypi/
.. _setuptools: http://peak.telecommunity.com/DevCenter/setuptools
.. _easy_install: http://peak.telecommunity.com/DevCenter/EasyInstall
.. _ez_setup.py: http://peak.telecommunity.com/dist/ez_setup.py
.. _distutils documentation: http://docs.python.org/dist/package-upload.html
.. _identity: http://docs.turbogears.org/1.0/GettingStartedWithIdentity
"""
__docformat__ = 'restructuredtext'

name = "EggBasket"
version = "0.4a"
date = "$Date$"

_doclines = __doc__.split('\n')
description = _doclines[0]
long_description = '\n'.join(_doclines[2:])

author = "Christopher Arndt"
author_email = "chris@chrisarndt.de"
copyright = "(c) 2008 Christopher Arndt"
license = "MIT License, Zope Public License (rest.py)"

url = "http://chrisarndt.de/projects/%s/" % name.lower()
download_url = "http://cheeseshop.python.org/pypi/%s" % name

# Use keywords if you'll be adding your package to the
# Python Cheeseshop
keywords = """
# if this has widgets, uncomment the next line
# turbogears.widgets

# if this has a tg-admin command, uncomment the next line
# turbogears.command

# if this has identity providers, uncomment the next line
# turbogears.identity.provider

# If this is a template plugin, uncomment the next line
# python.templating.engines

# If this is a full application, uncomment the next line
turbogears.app
"""

keywords = [line.strip() for line in keywords.split('\n')
    if line.strip() and not line.strip().startswith('#')]

# PyPI trove classifiers, for a list see
# http://pypi.python.org/pypi?%3Aaction=list_classifiers
classifiers = """
Development Status :: 3 - Alpha
Operating System :: OS Independent
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
Framework :: TurboGears

# if this is an application that you'll distribute through
# the Cheeseshop, uncomment the next line
Framework :: TurboGears :: Applications

# if this is a package that includes widgets that you'll distribute
# through the Cheeseshop, uncomment the next line
# Framework :: TurboGears :: Widgets
"""
classifiers = [line.strip() for line in classifiers.split('\n')
    if line.strip() and not line.strip().startswith('#')]
