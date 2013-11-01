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

For details and minor changes, please see the `Subversion log messages
<http://trac.chrisarndt.de/code/log/projects/python-rtmidi/trunk>`_.

Development version (unreleased)
````````````````````````````````

**2013-10-15**
    * `midiutils.open_midiport()`:

      * Allow to pass (substring of) port name as alternative to port number.
      * Re-raise ``EOFError`` and ``KeyboardInterrupt`` instead of using
        ``sys.exit()``.
      * Add ``client_name`` and ``port_name`` arguments.
      * Add ``use_virtual`` argument (default ``False``) to request opening
        of a virtual MIDI port.
      * ``interactive`` keyword argument (default ``True``) to disable
        interactive prompt for port.

    * ``MidiIn``/``MidiOut`` and ``open*()`` methods: allow to specify ``None``
      as client or port name to get the default names.

    * Add methods to ``OSC2MIDIHandler`` in ``osc2midi`` to send program
      changes, pitch bend, and channel and poly aftertouch; make default
      channel an instance variable that can be changed via OSC messages.

**2013-10-12**
    * Add new ``oscdispatcher`` module to ``osc2midi`` example.
    * Lots of re-structuring and improvements to ` osc2midi``.

**2013-10-02**
    * Convert ``osc2midi`` example script into a package

**2013-10-01**
    * Include ``ez_setup.py`` in source distribution.

**2013-09-30**
    * Move ``midiconstants`` module from examples into ``rtmidi`` package
      and add ``midiutil`` module.
    * Include examples in source distribution
    * Convert / break down ``midifilter`` example script into a package.
    * Add new ``sysexsaver`` example.
    * Update version number in ``RtMidi.cpp/h`` to reflect actual code state.

**2013-09-29**
    * Allow ``MidiIn/Out.open_port`` methods to be used with the ``with``
      statement and the port will be closed at the end of the block.

**2013-09-28**
    * Change ``queue_size_limit`` to 1024.
    * Add docstring to the rest of ``MidiIn`` methods.

**2013-09-27**
    * Fix string conversion in constructors and ``open_*`` methods.
    * Change default name of virtual ports.
    * Add docstrings to many methods and functions.

**2013-09-24**
    * Add new example script ``wavetablemodstep.py`` to demonstrate sending
      of control cgange messages.

**2013-09-12**
    * Update  from ``optparse`` to ``argparse`` in ``osc2midi.py`` example.

**2013-09-11**
    * Switch from distribute back to setuptools.

**2013-08-08**
  * Add new example script ``sendsysex.py`` to demonstrate sending of system
    exclusive messages.

**2013-02-12**
  * Add new example script ``osc2midi.py``, a simple, uni-directional OSC
    to MIDI mapper.

Releases
````````

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
