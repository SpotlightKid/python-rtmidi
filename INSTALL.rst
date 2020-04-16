============
Installation
============

**python-rtmidi** uses the de-facto standard Python distutils and setuptools_
based packaging system and can be installed from the Python Package Index via
pip_. Since it is a Python C(++)-extension, a C++ compiler and build
environment as well as some system-dependent libraries are needed to install,
unless wheel packages with pre-compiled binaries are available for your system.
See the Requirements_ section below for details.


From PyPI
---------

If you have all the requirements_, you should be able to install the package
with pip_::

    $ pip install python-rtmidi

This will download the source distribution from python-rtmidi's `PyPI page`_,
compile the extension (if no pre-compiled binary wheel is available) and
install it in your active Python installation. Unless you want to change the
Cython_ source file ``_rtmidi.pyx``, there is no need to have Cython installed.

.. note::
    On some Linux distributions, e.g. *Debian*, which support both Python 2 and
    Python 3, pip may installed under the name ``pip2`` resp. ``pip3``. In this
    case, just ``pip2`` instead of ``pip`` if you're still using Python 2 (not
    officially supported), or ``pip3`` if you are using Python 3.

python-rtmidi also works well with virtualenv_ and virtualenvwrapper_. If you
have both installed, creating an isolated environment for testing and/or using
python-rtmidi is as easy as::

    $ mkvirtualenv rtmidi
    (rtmidi)$ pip install python-rtmidi

If you want to pass options to the build process, use pip's ``install-option``
option. See the `From Source`_  section below for available options.


Pre-compiled Binaries
---------------------

Pre-compiled binary wheels of the latest python-rtmidi version for Windows and
macOS / OS X are available on PyPI for several major Python versions. If you
install python-rtmidi via pip (see above), these wheels will be selected by pip
automatically, if you have a compatible Python and Windows or macOS version.

The Windows binary wheels are compiled with Windows MultiMedia API support and
are available in 32-bit and 64-bit versions. The macOS / OS X binary wheels are
compiled with CoreMIDI support and are only available in 64-bit versions for
OS X 10.6 and later. If you need JACK support on OS X, you need to compile
python-rtmidi yourself (see the macOS_ section below for details).


From Source
-----------

To compile python-rtmidi from source and install it manually without pip, you
can either download a source distribution archive or check out the sources from
the Git repository.

While the steps to get the sources differ, the actual compilation step consists
only of the usual ``python setup.py install`` command in both cases.

``setup.py`` recognizes several options to control which OS-dependent MIDI
backends will be supported by the python-rtmidi extension binary it produces
plus other options to control compilation of the RtMidi C++ library:

+-----------------------------+-----------+---------------+-----------+----------------------------------------------------------+
| Option                      | Linux     | mac OS / OS X | Windows   |  Note                                                    |
+=============================+===========+===============+===========+==========================================================+
| ``--no-alsa``               | supported |               |           | Don't compile in support for ALSA backend.               |
+-----------------------------+-----------+---------------+-----------+----------------------------------------------------------+
| ``--no-jack``               | supported | supported     |           | Don't compile in support for JACK backend.               |
+-----------------------------+-----------+---------------+-----------+----------------------------------------------------------+
| ``--no-coremidi``           |           | supported     |           | Don't compile in support for CoreMIDI backend.           |
+-----------------------------+-----------+---------------+-----------+----------------------------------------------------------+
| ``--no-winmm``              |           |               | supported | Don't compile in support for Windows MultiMedia backend. |
+-----------------------------+-----------+---------------+-----------+----------------------------------------------------------+
| ``--no-suppress-warnings``  |           |               |           | Don't suppress RtMidi warnings to stderr.                |
+-----------------------------+-----------+---------------+-----------+----------------------------------------------------------+

Support for each OS dependent MIDI backend is only enabled when the required
library and header files are actually present on the system. When the options
passed to ``setup.py`` change, it may be necessary to remove previously built
files by deleting the ``build`` directory.

You can also pass these options to ``setup.py`` when using pip, by using its
``--install-option`` option, for example::

    pip install python-rtmidi --install-option="--no-jack"


From the Source Distribution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To download the python-rtmidi source distribution archive for the current
version, extract and install it, use the following commands::

    $ pip download python-rtmidi
    $ tar -xzf python-rtmidi-1.4.1.tar.gz
    $ cd python-rtmidi-1.4.1
    $ python setup.py install

On Linux or macOS / OS X, if you want to install python-rtmidi into the
system-wide Python library directory, you may have to prefix the last
command with ``sudo``, e.g.::

    $ sudo python setup.py install

The recommended way, though, is to install python-rtmidi only for your current
user (which pip does by default) or into a virtual environment::

    $ python setup.py install --user


From the Source Code Repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Alternatively, you can check out the python-rtmidi source code from the Git
repository and then install it from your working copy. Since the repository
does not include the C++ module source code pre-compiled from the Cython
source, you'll also need to install Cython >= 0.28, either via pip or from its
Git repository. Using virtualenv / virtualenvwrapper is strongly recommended
in this scenario:

Make a virtual environment::

    $ mkvirtualenv rtmidi
    (rtmidi)$ cdvirtualenv

Install Cython from PyPI::

    (rtmidi)$ pip install Cython

*or* from its Git repository::

    (rtmidi)$ git clone https://github.com/cython/cython.git
    (rtmidi)$ cd cython
    (rtmidi)$ python setup.py install
    (rtmidi)$ cd ..

Then install python-rtmidi::

    (rtmidi)$ git clone https://github.com/SpotlightKid/python-rtmidi.git
    (rtmidi)$ cd python-rtmidi
    (rtmidi)$ git submodule update --init
    (rtmidi)$ python setup.py install


.. _requirements:

Requirements
============

Naturally, you'll need a C++ compiler and a build environment. See the
platform-specific hints below.

If you want to change the Cython source file ``_rtmidi.pyx`` or want to
recompile ``_rtmidi.cpp`` with a newer Cython version, you'll need to install
Cython >= 0.28. The ``_rtmidi.cpp`` file in the current source distribution
(version 1.4.1) is tagged with::

    /* Generated by Cython 0.29.16 */

RtMidi (and therefore python-rtmidi) supports several low-level MIDI frameworks
on different operating systems. Only one of the available options needs to be
present on the target system, but support for more than one can be compiled in.
The setup script will try to detect available libraries and should use the
appropriate compilations flags automatically.

    * Linux: ALSA, JACK
    * macOS (OS X): CoreMIDI, JACK
    * Windows: MultiMedia (MM)


Linux
-----

First you need a C++ compiler and the pthread library. Install the
``build-essential`` package on debian-based systems to get these.

Then you'll need Python development headers and libraries. On debian-based
systems, install the ``python-dev`` package. If you use the official installers
from python.org you should already have these.

To get ALSA support, you must install development files for the ``libasound2``
library (debian package: ``libasound2-dev``). For JACK support, install the
``libjack`` development files (if you are using Jack1, install ``libjack-dev``,
if you are using Jack2, install ``libjack-jackd2-dev``).


.. _macos:

macOS (OS X)
------------

Install the latest Xcode version or ``g++`` from MacPorts or homebrew
(untested). CoreMIDI support comes with installing Xcode. For JACK support,
install `JackOSX`_ with the installer or build JACK from source.

.. note::
    If you have an old version of OS X and Xcode which still support building
    binaries for PPC, you'll have to tell distribute to build the package only
    for i386 and x86_64 architectures::

        env ARCHFLAGS="-arch i386 -arch x86_64" python setup.py install


Windows
-------

Please see the detailed instructions for Windows in :doc:`install-windows`.


User Contributed Documentation
------------------------------

The python-rtmidi wiki on GitHub contains some `user contributed
documentation`_ for additional installation scenarios. Please check these, if
you have trouble installing python-rtmidi in an uncommon or not-yet-covered
environment.


.. _pypi page: http://python.org/pypi/python-rtmidi#downloads
.. _cython: http://cython.org/
.. _pip: http://python.org/pypi/pip
.. _setuptools: http://python.org/pypi/setuptools
.. _virtualenv: http://pypi.python.org/pypi/virtualenv
.. _virtualenvwrapper: http://www.doughellmann.com/projects/virtualenvwrapper/
.. _jackosx: http://jackaudio.org/downloads/
.. _user contributed documentation:
    https://github.com/SpotlightKid/python-rtmidi/wiki/User-contributed-documentation
