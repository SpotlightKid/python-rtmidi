How to install python-rtmidi from source on Windows
===================================================

These instruction should work for installing ``python-rtmidi`` from source
using Python 2.7 or Python 3.5 in the 32-bit (you can run these on
Windows 64-bit versions with no problems) or 64-bit versions.

Please follow all the steps below in the exact order.


Installing required software
----------------------------

You probably need administrator rights for some or all of the following steps.

#. Install the latest release of Python 2.7 and/or Python 3.5 from
   https://www.python.org/downloads/windows/ to the default location (i.e.
   ``C:\Python27`` resp. ``C:\Python35``). You can install either or both
   the 32-bit and the 64-bit version.

   In the installer, enable the option to install pip_. Optionally, for only
   one of the chosen Python versions, enable the options to add the
   installation directory to your ``PATH`` and set it as the system's default
   version. Also enable the option to install the ``py`` help script (only
   available with some Python versions).

#. Install virtualenv_ from a command prompt::

        > python -m pip install -U virtualenv

   Repeat this for all Python versions you have installed (run ``py --help``
   to get help on how to run different python version from the command line).

#. Go to https://wiki.python.org/moin/WindowsCompilers and follow the
   instructions there to select and install the correct version(s) of the
   Visual C++ compiler for the version(s) of Python you installed.

   You can install several versions of Visual C++ at the same time.

   After installation, use Windows Update to get any pending security updates
   and fixes.


Setting up a virtual environment
--------------------------------

#. Open a command line and run::

        > python -m virtualenv rtmidi
        > rtmidi\Scripts\activate

#. Update pip and setuptools_ within your virtual environment to the latest
   versions with::

        (rtmidi)> pip install -U pip setuptools

#. Install Cython (still in the same command line window)::

        (rtmidi)> pip install Cython


Download & unpack python-rtmidi source
--------------------------------------

Get the latest python-rtmidi distribution as a Zip archive from
https://pypi.python.org/pypi/python-rtmidi and unpack it somewhere.
You can do the downloading and unpacking in one step using pip::

    > pip install --no-install -d . "python-rtmidi"

Alternatively, clone the python-rtmidi git repository::

    > git clone https://github.com/SpotlightKid/python-rtmidi.git

In the command line window you opened above, change into the ``python-rtmidi``
directory, which you created by unpacking the source or cloning the
repository::

    (rtmidi)> cd python-rtmidi


Build & install python-rtmidi
-----------------------------

Just run the usual setup command from within the source directory with the
active virtual environment, i.e. from still the same command line window::

    (rtmidi)> python setup.py install


Verify your installation
------------------------

Change out of the ``python-rtmidi`` source directory (important!) and run::

    (rtmidi)> cd ..
    (rtmidi)> python
    >>> import rtmidi
    >>> rtmidi.API_WINDOWS_MM in rtmidi.get_compiled_api()
    True
    >>> midiout = rtmidi.MidiOut()
    >>> midiout.get_ports()
    [u'Microsoft GS Wavetable Synth']

If you have any other MIDI outputs (hardware MIDI interfaces, MIDI Yoke etc.)
active, they should be listed by ``get_ports()`` as well.

*That's it, congratulations!*


Notes
-----

Windows Kernel Streaming support in RtMidi has been removed (it was broken
anyway) and consequently in ``python-rtmidi`` as well.

Compiling with MinGW also does not work out-of-the-box yet. If you have any
useful hints, please let the author know.


.. _pip: https://pypi.python.org/pypi/pip
.. _setuptools: https://pypi.python.org/pypi/setuptools
.. _virtualenv: https://pypi.python.org/pypi/virtualenv
