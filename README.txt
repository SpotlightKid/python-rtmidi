Welcome to python-rtmidi!
=========================

RtMidi_ is a set of C++ classes which provides a concise and simple,
cross-platform API (Application Programming Interface) for realtime MIDI
input/output across Linux (ALSA & JACK), Macintosh OS X (CoreMidi & JACK),
and Windows (Multimedia Library & Kernel Streaming) operating systems.

python-rtmidi_ is a Python binding for RtMidi implemented with Cython_ and
provides a thin wrapper around the RtMidi C++ interface. The API is basically
the same as the C++ one but with the naming scheme of classes, methods and
parameters adapted to the Python PEP-8 conventions and requirements of
the Python package naming structure. ``python-rtmidi`` supports Python 2
(tested with Python 2.7) and Python 3 (3.2).

For more information, visit ``python-rtmidi's`` web page:

    http://chrisarndt.de/projects/python-rtmidi


Changelog
---------

**2013-01-23 version 0.3.1a**

Enhancements:
    * Increase sysex input buffer size for WinMM API again to 8192 (8k) bytes.
      Requested by Martin Tarenskeen.

**2013-01-14 version 0.3a**

Bug fixes:
    * Add ``encoding`` parameter to ``get_port_name`` methods of ``MidiIn``
      and ``MidiOut`` to be able to handle non-UTF-8 port names, e.g. on
      Windows (reported by Pierre Castellotti).
    * Add ``encoding`` parameter to ``get_ports`` method as well and pass it
      through to ``get_port_name``. Use it in the test scripts.

Enhancements:
    * Increase sysex input buffer size for WinMM API to 4096 bytes.

Examples:
    * Add new ``midifilter.py`` example script.

Building:
    * Add ``setuptools``/``distribute`` support.

**2012-07-22 version 0.2a**

Bug fixes:
    * Fix uninitialized pointer bug in RtMidi.cpp in 'MidiOutJack' class, which
      caused warning in jack process callback when creating a 'MidiOut'
      instance with JACK API.
    * ``testmidiin_*.py``: fix superfluous decoding of port name (caused error
      with Python 3)

Enhancements:
    * Simplify some code, some things gleaned from rtmidi_python
    * Documentation typo fixes and more information on Windows compilation
    * Enhancements in test scripts:

      * ``test_probe_ports.py``: Catch exceptions when creating port
      * ``test_midiin_*.py``:

        * Better error message for missing/invalid port number
        * Show how to convert event delta time into absolute time when
          receiving input

Building:
    * Building on OS X 10.6.9 with CoreMIDI and JACK for OS X successfully
      tested and test run without errors
    * WinMM support now compiles with Visual Studio 2008 Express and tests
      work under Windows XP SP3 32-bit:
    * Add command line option to exclude WinMM or WinKS API from compilation
    * Add missing 'extra_compile_args' to Extension keyword args in setup file
    * add 'library_dirs' to Extension keyword args in setup file
    * use '-frtti' compiler option on OS X (neccessary on 10.7?)
    * Fix file name conflict on case-insensitive file systems by prefixing
      'rtmidi.{pyx,cpp}' with an underscore
    * Provide correct compiler flags for compiling with Windows MultiMedia API
    * Adapt windows library and include path for Visual Studio 2008 Express
    * add support for compiling with Windows Kernel Streaming API (does not
      not compile due to syntax errors in RtMidi.cpp yet)

**2012-07-13 version 0.1a**

First public release
