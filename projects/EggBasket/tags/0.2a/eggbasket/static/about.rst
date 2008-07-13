EggBasket is simple, lightweight Python Package Index (aka Cheeseshop) clone.

.. contents::
    :depth: 1


Overview
--------

EggBasket_ is a web application which provides a service similar and compatible
to the `Python Package Index`_ (aka Cheeseshop). It allows you to maintain your own local repository of Python packages required by your installations.

It is implemented using the TurboGears_ web framework, Genshi_ and SQLAlchemy_.

.. warning::
    This is still alpha-stage software. All the basic operations necessary
    to support a setuptools-based infrastructure are there, but some
    convenience features are missing and the software has not been tested
    extensively. **Use at your own risk!**


Features
--------

* Can be used by setuptools_ / easy_install_ as the package index and repository.

* Supports distutils ``upload`` protocol.

* Has simple role-based permission system to restrict package uploads (but see
  TODO).

* Requires only SQLite database (included with Python 2.5).

* Is able to read and display meta data from the following distribution package
  formats (source and binary):

  ``.egg``, ``.tar``, ``.tar.bz2``, ``.tar.gz``, ``.tgz``, ``.zip``

* Any other file format can be configured to be listed under the distribution
  files for a package (by default this includes ``.exe`` and ``.rpm`` and
  ``.tar.Z`` files in addition to the filetypes listed above).

* Can be run without any configuration by just starting it from within a
  directory containing package directories.


Todo
----

* Improve permission system to allow closed-shop repositories on an open
  network or uploading for anonymous users.
* Add support for MD5 check sums and GPG signatures.
* Add more error and sanity checks to the upload handling.
* Add pagination to the main package list.
* Support deletion of packages through web interface.
* Cache package listings and meta data.
* Add admin interface for adding users and groups and setting configuration
  values (use dbspockets?).


Acknowledgments
---------------

This application is a re-implementation (almost no shared code) of the
haufe.eggserver_ Grok application with some improvements.


Copyright & License
-------------------

EggBasket is brought to you and copyrighted by *Christopher Arndt*.

The software is released under the `MIT License`_.

**Share & enjoy!**

The included ``rest.py`` module is used under the `Zope Public License 2.1`_::

    Zope Public License (ZPL) Version 2.1

    A copyright notice accompanies this license document that identifies the
    copyright holders.

    This license has been certified as open source. It has also been designated
    as GPL compatible by the Free Software Foundation (FSF).

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:

       1. Redistributions in source code must retain the accompanying copyright
          notice, this list of conditions, and the following disclaimer.
       2. Redistributions in binary form must reproduce the accompanying
          copyright notice, this list of conditions, and the following
          disclaimer in the documentation and/or other materials provided with
          the distribution.
       3. Names of the copyright holders must not be used to endorse or promote
          products derived from this software without prior written permission
          from the copyright holders.
       4. The right to distribute this software or to use it for any purpose
          does not give you the right to use Servicemarks (sm) or Trademarks
          (tm) of the copyright holders. Use of them is covered by separate
          agreement with the copyright holders.
       5. If any files are modified, you must cause the modified files to carry
          prominent notices stating that you changed the files and the date of
          any change.

    Disclaimer

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY
    EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS BE LIABLE FOR ANY
    DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
    SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
    CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
    LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
    OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
    DAMAGE.


.. _turbogears: http://www.turbogears.org/
.. _genshi: http://genshi.edgewall.org/
.. _sqlalchemy: http://www.sqlalchemy.org/
.. _haufe.eggserver: http://cheeseshop.python.org/pypi/haufe.eggserver
.. _eggbasket: http://chrisarndt.de/projects/eggbasket/
.. _python package index: http://cheeseshop.python.org/pypi/
.. _setuptools: http://peak.telecommunity.com/DevCenter/setuptools
.. _easy_install: http://peak.telecommunity.com/DevCenter/EasyInstall
.. _mit license: http://www.opensource.org/licenses/mit-license.php
.. _zope public license 2.1: http://www.zope.org/Resources/ZPL
