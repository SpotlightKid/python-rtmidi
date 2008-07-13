.. contents::
    :depth: 1

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
  server anywheer you want.

  If no configuration file is specified on the command line, the default
  configuration file included in the egg will be used. The default
  configuration file can also be found in the source distribution and be
  adapted for your environment.

  The server either needs write permissions to directory where it is started,
  or you need to change the path to the database and the access log in the
  configuration so they can be written by the server.

* To stop the server just hit Control-C in the terminal or kill the process.

* You can look at the package index with your web browser by opening the URL
  ``http://localhost:3442/``. The default port ``3442`` can be changed by
  setting the ``server.socket_port`` option in the configuration file.

* You can instruct easy_install_ to search & download packages from your
  package repository by specifying the URL to your server with the ``-i``
  option::

    easy_install -i http://localhost:8080/ PACKAGE_NAME

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
  group "maintainers", which has the "upload" permission. The database to use
  will be read from the config file.

  See the TurboGears documentation on Identity_ for background information.

* Of course you can always just copy package distribution files manually in the
  filesystem to your repository or upload them to the appropriate place with
  ``scp`` etc. The application will find and list new files without the need to
  "register" them as is necessary with the original PyPI.


Known problems
--------------

* There seems to be a bug in the distutils code for PKG-INFO generation that
  messes up indentation in the package description. This will cause docutils
  warnings and layout errors on the package meta data pages when using ReST
  formatting. For this reason, the conversion of the package description to
  HTML with docutils is disabled in the default configuration. You can enable
  it by setting ``eggbasket.pkg_desc_format`` to ``'rest'``.
* Some packages are registered on PyPI under a different name than their package
  name. For example, the ``"configobj"`` module is listed as ``"ConfigObj"`` on
  PyPI, but the package files are named ``"configobj-X.Y.Z...."``. When a
  package specifies "ConfigObj" as a requirement, easy_install will not find the
  package in your eggbasket repository if you only have a ``"configobj"``
  directory. Simply symlinking or copying "configobj" to ``"ConfigObj"`` works
  around this problem.

.. _eggbasket: http://chrisarndt.de/projects/eggbasket/
.. _cheeseshop: http://cheeseshop.python.org/pypi/
.. _setuptools: http://peak.telecommunity.com/DevCenter/setuptools
.. _easy_install: http://peak.telecommunity.com/DevCenter/EasyInstall
.. _ez_setup.py: http://peak.telecommunity.com/dist/ez_setup.py
.. _distutils documentation: http://docs.python.org/dist/package-upload.html
.. _identity: http://docs.turbogears.org/1.0/GettingStartedWithIdentity
