# -*- coding: UTF-8 -*-
"""CBlog is a simple weblog application based on the TurboGears_ framework.

Apart from being used by myself as the software that drives my personal blog,
it is also a useful showcase for various TG programming patterns.

The software is currently in alpha state, because the data model and the API
(internal and external, i.e. URls) may still change frequently and some
features I consider important are still missing. That being said, I already use
it on a regular basis for my own blog site.

.. _TurboGears: http://turbogears.org
"""

import sys

# Release information about CBlog

_doclines = __doc__.split('\n')

_py_major_version = "%i.%i" % sys.version_info[:2]

name="CBlog"
version = "0.1a"

description = _doclines[0]
long_description = '\n'.join(_doclines[2:])
author = "Christopher Arndt"
email = "chris@chrisarndt.de"
copyright = "© 2006 Christopher Arndt"

# if it's open source, you might want to specify these
url = "http://chrisarndt.de/projects/cblog/"
download_url = "http://chrisarndt.de/projects/cblog/download/%s-%s-py%s.egg" % \
  (name, version, _py_major_version)
license = "MIT license"

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

classifiers = [c for c in _classifiers.split('\n') if c]

# Use keywords if you'll be adding your package to the
# Python Cheeseshop
_keywords = """\
turbogears.widgets
turbogears.app
"""

keywords = [k for k in _keywords.split('\n') if k]
