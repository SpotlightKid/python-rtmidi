# -*- coding: UTF-8 -*-
"""CBlog is a simple weblog application based on the TurboGears framework.

Apart from being used by myself as the software that drives my personal blog,
it is also a useful showcase for various TurboGears_ programming patterns.

The software is currently in alpha state, because the data model and the API
(internal and external, i.e. URls) may still change frequently and some
features I consider important are still missing. That being said, I already use
it on a regular basis for `my own blog site`_.

.. _TurboGears: http://turbogears.org
.. _my own blog site: http://paddyland.serveblog.net
"""

import sys

# Release information about CBlog

_doclines = __doc__.split('\n')

_py_major_version = "%i.%i" % sys.version_info[:2]

name = "CBlog"
revision = "$Rev$"
version = "0.2a-dev%s" % revision[6:9]
date = "$Date$"

description = _doclines[0]
long_description = '\n'.join(_doclines[2:])
author = "Christopher Arndt"
email = "chris@chrisarndt.de"
copyright = "© 2006 Christopher Arndt"
license = "MIT license"

url = "http://chrisarndt.de/projects/%s/" % name.lower()
package_name = '%s-%s' % (name, version)
# file names of different package formats
package_egg = '%s-py%s.egg' % (package_name, _py_major_version)
src_package_tgz = package_name + '.tar.gz'
src_package_tbz = package_name + '.tar.bz2'
src_package_zip = package_name + '.zip'
download_url = "%sdownload/%s" % (url, package_egg)

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
Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary
"""
classifiers = filter(None, [c.strip() for c in _classifiers.split('\n')])

# Use keywords if you'll be adding your package to the
# Python Cheeseshop
_keywords = """\
turbogears.app
"""
keywords = filter(None, [k.strip() for k in _keywords.split('\n')])
