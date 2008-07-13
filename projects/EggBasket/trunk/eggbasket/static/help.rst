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

EggBasket server
~~~~~~~~~~~~~~~~

* Your packages should all reside under a common root directory, with a
  sub-directory for each package with the same base name as the distribution.
  The sub-directories should each contain the egg files and source archives for
  all available versions of the package. The package directories will be created
  by the application when using the upload command (see below).

* Open a terminal, change to the directory which contains the packages and, if
  you are haven't already done so, initialize the database with::

    eggbasket-server --init [<config file>]

* Start the application server with::

    eggbasket-server [<config file>]

  You can also set the location of the package root directory in the
  configuration with the ``eggbasket.package_root`` setting and start the
  server anywhere you want.

  If no configuration file is specified on the command line, the default
  configuration file included in the egg will be used. The default
  configuration file can also be found in the source distribution and be
  adapted for your environment.

  The server either needs write permissions in the directory where it is
  started, or you need to change the path of the database and the access log in
  the configuration so they can be written by the server. Of course, package
  uploads will also only work if the server has the permissions to create any
  missing package directories or write in existing ones.

* To stop the server just hit ``Control-C`` in the terminal or kill the process.

* You can look at the package index with your web browser by opening the URL
  ``http://localhost:3442/``. The default port ``3442`` can be changed by
  setting the ``server.socket_port`` option in the configuration file.


Using EggBasket with ``distutils`` & ``easy_install``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* You can instruct easy_install_ to search & download packages from your
  package repository by specifying the URL to your server with the ``-i``
  option. Example::

    easy_install -i http://localhost:3442/ PACKAGE_NAME

* Additionally, it might be necessary to restrict the hosts from which
  easy_install will download to your EggBasket server with the ``-H`` option.
  Example::

    easy_install -H localhost:3442 -i http::/localhost:3442/ PACKAGE_NAME

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

* Of course you can always just copy package distribution files manually in the
  filesystem to your repository or upload them to the appropriate place with
  ``scp`` etc. The application will find and list new files without the need to
  "register" them as is necessary with the original PyPI.


Permissions
~~~~~~~~~~~

EggBasket uses a simple, role-based permission system to grant/restrict access
to the functions of the server. Here is a list of the defined permissions and
their meaning:

* ``viewpkgs`` - User can view the list of all packages
* ``viewfiles`` - User can view the list of distribution files for a package.
* ``viewinfo`` - User can view the meta data for a package distribution file.
* ``download`` - User can download a package distribution file.
* ``upload`` - User can upload a package distribution file.
* ``overwrite`` - User can overwrite and existing package distribution file.
* ``delete`` - User can delete a package distribution file through the web
  interface.

You can let EggBasket create an initial admin user, groups and permissions in
the database by giving the ``--init`` option to the ``eggbasket-server``
command::

    eggbasket-server --init [<config file>]

This will create the following objects and relations in the database:

* The above listed permissions.

* The following groups (with permissions in brackets):

  * anonymous (viewpkgs, viewfiles, viewinfo, download)
  * authenticated (viewpkgs, viewfiles, viewinfo, download)
  * maintainer (upload, overwrite, delete)
  * admin

* A user with user name/password "admin", belonging to the groups "maintainer"
  and "admin".

The groups "anonymous" and "authenticated" are special groups to which all
anonymous (i.e. not logged in) resp. all authenticated (logged in) users belong
automatically.

With the default permission setup, uploading through the server is restricted
to users that are members of a group that has the "upload" permission. The
configuration page can only be accessed by members of the "admin" group.
Everything else can be accessed all users, whether authenticated or not.

Please note that if you want to give a certain permission to all users, whether
logged in or not, you need to give this permission to both the "anonymous" AND
the "authenticated" group. This is what the standard permission setup already
does for all permissions except "upload".

See the TurboGears documentation on Identity_ for background information.


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
  package specifies "ConfigObj" as a requirement, easy_install would normally
  not find the package in your EggBasket repository if you only have a
  ``"configobj"`` directory. Eggbasket works around this by treating the
  requested package name as case-insensitive, i.e. if the URL ``/package/Foo``
  is requested, it will also look for a directory ``foo`` in the package root
  directory and return the package listing for that directory.


.. _eggbasket: http://chrisarndt.de/projects/eggbasket/
.. _cheeseshop: http://cheeseshop.python.org/pypi/
.. _setuptools: http://peak.telecommunity.com/DevCenter/setuptools
.. _easy_install: http://peak.telecommunity.com/DevCenter/EasyInstall
.. _ez_setup.py: http://peak.telecommunity.com/dist/ez_setup.py
.. _distutils documentation: http://docs.python.org/dist/package-upload.html
.. _identity: http://docs.turbogears.org/1.0/GettingStartedWithIdentity
