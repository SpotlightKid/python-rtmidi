# -*- coding: UTF-8 -*-
"""A very simple bookmark directory.

This is a TurboGears_ sample application. It is a simple bookmark directory, that allows you to collect bookmarks with a title, a URL, and a description and assign arbitrary tags to each bookmark.

It was developed as an example to accompany a short introductory talk to the
`development of web applications with TurboGears`_ (in German language).
I have since then also used it as an example for `another talk on TurboGears`_,
for the `RuPy conference 2007`_, in Posznań.

This is intended as a demonstration, it is not a full application, so please don't complain about missing features :-)

.. _TurboGears: http://turbogears.org/
.. _development of web applications with TurboGears: http://chrisarndt.de/talks/tg-tutorial/
.. _another talk on TurboGears: http://chrisarndt.de/talks/rupy/
.. _RuPy conference 2007: http://rupy.wmid.amu.edu.pl/

"""

import sys

_doclines = __doc__.split('\n')
_py_major_version = '%i.%i' % sys.version_info[:2]

name = 'Bookmarker'
version = '0.2.1a'
date = '$Date$'

description = _doclines[0]
long_description = '\n'.join(_doclines[2:])
author = 'Christopher Arndt'
email = 'chris@chrisarndt.de'
copyright = '(c) 2006-2007 Christopher Arndt'
license = 'MIT license'

url = 'http://chrisarndt.de/projects/%s/' % name.lower()
package_name = '%s-%s' % (name, version)
# file names of different package formats
src_package_tgz = package_name + '.tar.gz'
src_package_tbz = package_name + '.tar.bz2'
src_package_zip = package_name + '.zip'
download_url = '%sdownload/%s' % (url, src_package_tbz)

platform = 'Any'
_classifiers = """\
Development Status :: 3 - Alpha
Environment :: Web Environment
Framework :: TurboGears
Framework :: TurboGears :: Applications
Intended Audience :: Developers
Intended Audience :: Education
Intended Audience :: End Users/Desktop
License :: OSI Approved :: MIT License
Operating System :: OS Independent
Programming Language :: Python
Topic :: Database
Topic :: Internet :: WWW/HTTP :: Indexing/Search
"""
classifiers = filter(None, [c.strip() for c in _classifiers.split('\n')])

# Use keywords if you'll be adding your package to the
# Python Cheeseshop
_keywords = """\
turbogears.app
"""
keywords = filter(None, [k.strip() for k in _keywords.split('\n')])
