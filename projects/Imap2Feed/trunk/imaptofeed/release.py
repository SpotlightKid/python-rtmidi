# -*- coding: UTF-8 -*-
"""A simple IMAP to RSS/Atom feed gateway based on TurboGears.

This simple TurboGears application provides a gateway between IMAP 
mailboxes and the web by serving an RSS/Atom feed for each configured
mailbox with the latest messages.
"""

import sys

# Release information about Imap2Feed

_doclines = __doc__.split('\n')
_py_major_version = "%i.%i" % sys.version_info[:2]

version = "0.1a"

name = "Imap2Feed"
revision = "$Rev:$"
version = "0.1a"
date = "$Date:$"

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

_classifiers = """\
Development Status :: 3 - Alpha
Environment :: Web Environment
Framework :: TurboGears
Framework :: TurboGears :: Applications
Intended Audience :: Developers
Intended Audience :: Education
License :: OSI Approved :: MIT License
Operating System :: OS Independent
Programming Language :: Python
Topic :: Communications :: Email
Topic :: Communications :: Email :: Post-Office :: IMAP
Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary
"""
classifiers = filter(None, [c.strip() for c in _classifiers.split('\n')])

# Use keywords if you'll be adding your package to the
# Python Cheeseshop
_keywords = """\
turbogears.app
"""
keywords = filter(None, [k.strip() for k in _keywords.split('\n')])
