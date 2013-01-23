# -*- coding:utf-8 -*-
#
# release.py - release information for the rtmidi package
#
"""A Python wrapper for the RtMidi C++ library written with Cython.


Overview
========

RtMidi_ is a set of C++ classes which provides a concise and simple,
cross-platform API (Application Programming Interface) for realtime MIDI
input/output across Linux (ALSA & JACK), Macintosh OS X (CoreMIDI & JACK),
and Windows (Multimedia Library & Kernel Streaming) operating systems.

python-rtmidi_ is a Python binding for RtMidi implemented with Cython_ and
provides a thin wrapper around the RtMidi C++ interface. The API is basically
the same as the C++ one but with the naming scheme of classes, methods and
parameters adapted to the Python PEP-8 conventions and requirements of
the Python package naming structure. ``python-rtmidi`` supports Python 2
(tested with Python 2.7) and Python 3 (3.2).

.. note::
    ``python-rtmidi`` is currently in **alpha-stage**, which means is is
    published in the hope that other developers try it out and help finding
    bugs, and that its API is not yet finalised. What is there should work
    but is currently only tested thoroughly under Linux ALSA/JACK and less
    regularly under OS X (CoreMIDI/JACK) and Windows (WinMM). Support for the
    Windows Kernel Streaming API does not work yet due to compilation problems.


Usage example
-------------

Here's a quick example of how to use ``python-rtmidi`` to open the first
available MIDI output port and send a middle C note on MIDI channel 10::

    import time
    import rtmidi

    midiout = rtmidi.MidiOut()
    available_ports = midiout.get_ports()

    if available_ports:
        midiout.open_port(0)
    else:
        midiout.open_virtual_port("My virtual output")

    note_on = [0x99, 60, 112] # channel 10, middle C, velocity 112
    note_off = [0x89, 60, 0]
    midiout.send_message(note_on)
    time.sleep(0.5)
    midiout.send_message(note_off)

    del midiout

More usage examples can be found in the ``tests`` directory of the source
distribution. API documentation is available by looking at the docstrings in
the Cython source code or using tools like ``pydoc`` or IPython_ and by
reading the RtMidi_ documentation.


Installation
============

``python-rtmidi`` is a Python C(++)-extension and therefore a C++ compiler
and a build environment as well as some system-dependant libraries are needed.
See "Requirements" below for details.


Installer (Windows only)
------------------------

An installer with a pre-compiled version for Windows with Windows MultiMedia
API support is available through PyPI for some Python versions. Download it
from python-rtmidi's `PyPI page`_ and start the installer by double-clicking.


From PyPI
---------

If you have all the dependencies, you should be able to install the package
with pip_ or ``easy_install``::

    $ pip install python-rtmidi

or, if you prefer setuptools_::

    $ easy_install python-rtmidi

This will download the source distribution, compile the extension and install
it in your active Python installation. Unless you want to change the Cython
source file ``_rtmidi.pyx``, there is no need to have Cython installed.

``python-rtmidi`` also works well with virtualenv_ and virtualenvwrapper_. If
you have both installed, creating an isolated environment for testing and using
``python-rtmidi`` is as easy as::

    $ mkvirtualenv rtmidi
    (rtmidi)$ pip install python-rtmidi


From the Source Distribution
----------------------------

Of course, you can also download the source distribution package as a Zip
archive or tarball, extract it and install using the common ``distutils``
commands, e.g.::

    $ wget %(download_url)spython-rtmidi-%(version)s.tar.gz
    $ tar xzf python-rtmidi-%(version)s.tar.gz
    $ cd python-rtmidi-%(version)s
    $ python setup.py install


From Subversion
---------------

Lastly, you can check out the ``python-rtmidi`` source code from the
Subversion repository and then install it from your working copy. Since the
repository does not include the C++ module source code pre-compiled from the
Cython source, you'll also need to install Cython from its Git repository.
Using virtualenv/virtualenvwrapper is strongly recommended in this scenario::

    $ mkvirtualenv rtmidi
    (rtmidi)$ cdvirtualenv
    (rtmidi)$ git clone https://github.com/cython/cython.git
    (rtmidi)$ svn co svn://svn.chrisarndt.de/projects/python-rtmidi/trunk python-rtmidi
    (rtmidi)$ cd cython
    (rtmidi)$ python setup.py install
    (rtmidi)$ cd ../python-rtmidi
    (rtmidi)$ python setup.py install


Requirements
============

Naturally, you'll need a C++ compiler and a build environment. See the
platform-specific hints below.

Only if you want to change the Cython source file ``_rtmidi.pyx`` or want to
recompile ``_rtmidi.cpp`` with a newer Cython version, you'll need to install
Cython >= 0.17. The ``_rtmidi.cpp`` file in the  source distribution was
generated with Cython 0.18pre as of 2013-01-14 and Python 2.7.3.

RtMidi (and therefore ``python-rtmidi``) supports several low-level MIDI
libraries on different operating systems. Only one of the available options
needs to be present on the target system, but support for more than one can be
compiled in. The setup script will try to detect available libraries and should
use the appropriate compilations flags automatically.

    * Linux: ALSA, JACK
    * OS X: CoreMIDI, JACK
    * Windows: MultiMedia (MM), Windows Kernel Streaming


Linux
-----

For the C++ compiler and the pthread library install the ``build-essential``
package on debian-based systems.

Then you'll need Python development headers and libraries. On Linux, install
the ``python-dev`` package. If you use the official installers from python.org
you should already have these.

To get ALSA support, you must install development files for the ``libasound``
library (debian package: ``libasound-dev``). For JACK support, install the
``libjack`` development files (``libjack-dev`` or ``libjack-jackd2-dev``).


OS X
----

Install the latest Xcode or ``g++`` from MacPorts or homebrew (untested).
CoreMIDI support comes with installing Xcode. For JACK support, install
`JACK for OS X`_ with the full installer.


Windows
-------

On Windows you'll need Visual Studio 2008 (Express). Visual Studio 2010
(Express) or later editions will not work with current official Python
distributions. After you have installed Visual Studio, you probably need to
edit the ``WINLIB_DIR`` and ``WININC_DIR`` variables at the top of the
``setup.py`` file to point to the location of ``WinMM.lib`` and the Microsoft
SDK headers.

Compiling ``python-rtmidi`` with Windows Kernel Streaming support currently
does not work due to syntax errors in ``RtMidi.cpp``. This is currently being
investigated. You can exclude Windows Kernel Streaming Support by providing
the ``--no-winks`` option to the ``setup.py`` invocation.

Compiling with MinGW also does not work out-of-the-box yet. If you have any
useful hints, please let the author know.



Copyright & License
===================

``python-rtmidi`` was written by %(author)s, 2012.

The author can be reached at %(author_email)s.

The software is released unter the **MIT License**:

Copyright (c) 2012 %(author)s

    Permission is hereby granted, free of charge, to any person obtaining a
    copy of this software and associated documentation files (the "Software"),
    to deal in the Software without restriction, including without limitation
    the rights to use, copy, modify, merge, publish, distribute, sublicense,
    and/or sell copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included
    in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
    OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
    DEALINGS IN THE SOFTWARE.


.. _rtmidi: http://www.music.mcgill.ca/~gary/rtmidi/index.html
.. _python-rtmidi: %(url)s
.. _pypi page: http://python.org/pypi/python-rtmidi#downloads
.. _cython: http://cython.org/
.. _pip: http://python.org/pypi/pip
.. _setuptools: http://python.org/pypi/setuptools
.. _virtualenv: http://pypi.python.org/pypi/virtualenv
.. _virtualenvwrapper: http://www.doughellmann.com/projects/virtualenvwrapper/
.. _ipython: http://ipython.org/
.. _jack for os x: http://www.jackosx.com/

"""

name = 'python-rtmidi'
version = '0.3.1a'
description = __doc__.splitlines()
keywords = 'rtmidi, midi, music'
author = 'Christopher Arndt'
author_email = 'chris@chrisarndt.de'
url = 'http://chrisarndt.de/projects/%s/' % name
download_url = url + 'download/'
license = 'MIT License'
platforms = 'POSIX, Windows, MacOS X'
long_description = "\n".join(description[2:]) % {
    'author': author, 'author_email': author_email,
    'download_url': download_url, 'url': url, 'version': version}
description = description[0]
classifiers = """\
Development Status :: 3 - Alpha
Environment :: MacOS X
Environment :: Win32 (MS Windows)
Environment :: Console
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Operating System :: Microsoft :: Windows
Operating System :: POSIX
Operating System :: MacOS :: MacOS X
Programming Language :: Python
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Topic :: Multimedia :: Sound/Audio :: MIDI
Topic :: Software Development :: Libraries :: Python Modules
"""
classifiers = [c.strip() for c in classifiers.splitlines()
    if c.strip() and not c.startswith('#')]
try: # Python 2.x
    del c
except: pass
