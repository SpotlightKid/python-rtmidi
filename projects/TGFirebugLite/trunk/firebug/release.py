# -*- coding: UTF-8 -*-
"""A TurboGears widgets wrapper for the Firebug Lite JavaScript Library.

Installation::

    [sudo] easy_install TGFirebugLite

or:

    1. Download the Egg manually from here_ or the Cheeseshop_.
    2. Install with ``easy_install <egg-file>``.

.. _here: http://chrisarndt.de/projects/tgfirebuglite/download/
.. _Cheeseshop: http://python.org/pypi/TGFirebugLite

Usage:

To use this widget, just add it to the ``tg.include_widgets`` configuration
setting, for example in your ``dev.cfg``::

    tg.include_widgets = ['firebug.widgets.firebug_js', ...]

If you don't care to simulate the Firebug console, but you want to prevent calls to ``console.log()`` in your JavaScript code from causing errors, then just change the widget name to ``firebug.widgets.firebugx_js``.

To try it out, just hit F12 after your page has loaded and the Firebug console
frame will open at the bottom of your page. You can enter JavaScript commands
at the command line right at the bottom and see their outcome in the console
logging area above.

Please see http://www.getfirebug.com/lite.html for more information.
"""

import sys

# Release information about CBlog

_doclines = __doc__.split('\n')

_py_major_version = "%i.%i" % sys.version_info[:2]

name="TGFirebugLite"
version = "1.0b"
date="$Date$"

description = _doclines[0]
long_description = '\n'.join(_doclines[2:])
author = "Christopher Arndt"
email = "chris@chrisarndt.de"
copyright = "© 2006 Christopher Arndt"

# if it's open source, you might want to specify these
url = "http://chrisarndt.de/projects/%s/" % name.lower()
download_url = "%sdownload/%s-%s-py%s.egg" % \
  (url, name, version, _py_major_version)
license = "MPL/GPL/LGPL"

platform = 'Any'

_classifiers = """\
Development Status :: 4 - Beta
Environment :: Web Environment
Framework :: TurboGears
Framework :: TurboGears :: Widgets
Intended Audience :: Developers
License :: OSI Approved :: Mozilla Public License 1.1 (MPL 1.1)
License :: OSI Approved :: GNU General Public License (GPL)
License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)
Operating System :: OS Independent
Programming Language :: Python
Programming Language :: JavaScript
Topic :: Software Development :: Testing
Topic :: Software Development :: Debuggers
"""
classifiers = filter(None, [c.strip() for c in _classifiers.split('\n')])

# Use keywords if you'll be adding your package to the
# Python Cheeseshop
_keywords = """\
turbogears.widgets
"""
keywords = filter(None, [k.strip() for k in _keywords.split('\n') if k])
