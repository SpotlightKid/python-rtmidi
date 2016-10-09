Changelog
=========

For details and minor changes, please see the `version control log messages
<https://github.com/SpotlightKid/python-rtmidi/commits/master>`_.


2016-10-09 version 1.0.0rc1
---------------------------

Project infrastructure:
  * Moved repository to Github.

Fixes:
  * ``midiutil.open_midiport``:

    * Correctly report and log I/O direction and instance type.
    * Fix naming of virtual port.

Enhancements / Changes:
  * Synced with upstream RtMidi_ (2.1.1-399a8ee).
  * ``midiutil``:

    * The function ``midiutil.open_port`` has been renamed to ``open_midiport``.

    * Added convenience functions ``open_midiinput`` and ``open_midioutput``,
      which wrap ``open_midiport``.

    * RtMidi API to use can be specified via the ``RTMIDI_API`` environment
      variable. Only used when ``API_UNSPECIFIED`` is passed for the ``api``
      argument. Value should be one of the ``API_*`` constant names with out
      the ``API_`` prefix, e.g. ``UNIX_JACK`` for the Jack API.

  * Cython wrapper class hierarchy restructured to better match the underlying
    C++ classes and remove code duplication.
  * Some source code re-ordering was done.

Documentation:
  * Added basic structure and initial content of Sphinx documentation.
  * Documented exceptions raised by ``MidiIn/Out.open_[virtual_]port()``.
  * Some docstring corrections and formatting fixes.

Building:
  * Simplified ``setup.py`` by throwing out old compatibility stuff.
  * Explicitly call ``PyEval_InitThreads`` from Cython code instead of using
    undocumented compiler macro.

Examples:
  * Moved `osc2midi` example into its own repository at
    https://github.com/SpotlightKid/osc2rtmidi.git

  * Add new ``sequencer`` example.

  * Add new ``noteon2osc`` example.

  * ``midifilter``:

    * Moved ``main.py`` to ``__main__.py``, removed old code and fixed command
      line args access.
    * Streamlined event matching.
    * Added ``CCToBankChange`` filter.
    * ``Queue`` module renamed to ``queue`` in Python 3.
    * Fixed opening of output port erroneously used ``"input"``.
    * Fixed positional command line args handling.
    * Set command name for argparse.

  * ``midi2command``:

    * Added README.
    * Added command line option to select backend API.
    * Catch errors when opening port.
    * Set client and port name.
    * Cache command lookup (Python 3.2+ only).

  * ``sysexsaver``:

    * Moved ``main.py`` to ``__main__.py``, some refactoring.
    * ``models.py``: Fixed wrong entry for manufacturer ``(0, 32, 81)``.
    * Moved module level code into ``main`` function.
    * Include model name in output file, if possible.

  * ``drumseq``:

    * Fixed global access in ``Sequencer`` class.
    * Use ``args.FileType`` for pattern command line args.


2014-06-11 version 0.5b1
------------------------

Fixes:
  * Synced RtMidi_ code with git repo @ 2c7a6664d6, which fixed several issues
    (see https://github.com/thestk/rtmidi/issues?state=closed).
  * ``MidiIn/Out.open_virtual_port`` returns ``self`` for context manager
    support, consistent with ``MidiIn/Out.open_port``.
  * Fix Python <= 2.6 incompatible encode method call (python-rtmidi
    officially only supports Python >= 2.7). Thanks to Michiel Overtoom for
    reporting this.
  * Respect passed MIDI api when requesting MidiOut instance from
    ``midiutil.open_midiport``.

.. _rtmidi: https://github.com/thestk/rtmidi

Enhancements / Changes:
  * Support for Windows Kernel Streaming API was removed in RtMidi (it was
    broken anyway) and consequently in ``python-rtmidi`` as well.
  * Raise ``RtMidiError`` exception when trying to open a (virtual) port on a
    ``MidiIn/Out`` instance that already has an open (virtual) port.
  * Add some common synonyms for MIDI events and controllers and some source
    comments about controller usage to ``midiconstants`` module.

Documentation:
  * Fix and clarify ``queue_size_limit`` default value in docstrings
  * Various docstring consistency improvements and minor fixes.

Examples:
  * New example script ``midi2command.py``, which executes external commands
    on reception of configurable MIDI events, with example configuration.
  * New example directory ``drumseq`` with a simple drum pattern sequencer
    and example drum patterns. Thanks to Michiel Overtoom for the original
    script!


2013-11-10 version 0.4.3b1
--------------------------

Building:
  * Add numeric suffix to version number to comply with PEP 440.
  * Add missing ``fill_template.py`` to source distribution.
  * Set default setuptools version in ``ez_setup.py`` to 1.3.2, which
    contains fix for bug #99 mentioned below.

Documentation:
  * Add note to installation guide about required ``--pre`` option with pip.


2013-11-07 version 0.4.2b
-------------------------

Fixes:
  * Add missing ``API_*`` constant to list of exported names of ``_rtmidi``
    module.

Enhancements / Changes:
  * Change default value of ``encoding`` argument of ``get_ports`` and
    ``get_port_name`` methods to `"auto"`, which selects appropriate encoding
    based on system and backend API used.

  * Add ``api`` parameter to ``midiutil.open_midiport`` function to select
    backend API.

  * Make client name for ``MidiOut`` and `` MidiIn`` different again,
    because some backend APIs might require unique client names.

Building:
  * Include workaround for setuptools bug (see bitbucket issue #99) in
    setup file.

  * Add custom distutils command to fill placeholders in ``INSTALL.rst.in``
    template with release meta data.

  * Setuptools is now required, pure distutils won't work anymore, so removing
    the fallback import of ``setup`` from distutils.


2013-11-05 version 0.4.1b
-------------------------

Building:
  * Include missing ``_rtmidi.cpp`` file in source distribution.

Documentation:
  * Fill in release data placeholders in ``INSTALL.rst``.


2013-11-05 version 0.4b
-----------------------

Fixes:
  * Fix string conversion in constructors and ``open_*`` methods.

  * Change default value ``queue_size_limit`` argument to ``MidiIn``
    constructor to 1024.

  * Update version number in ``RtMidi.cpp/h`` to reflect actual code state.

Enhancements / Changes:
  * Elevated development status to beta.

  * Allow ``MidiIn/Out.open_port`` methods to be used with the ``with``
    statement and the port will be closed at the end of the block.

  * ``MidiIn``/``MidiOut`` and ``open*()`` methods: allow to specify ``None``
    as client or port name to get the default names.

  * Move ``midiconstants`` module from examples into ``rtmidi`` package
    and added ``midiutil`` module.

  * ``midiutils.open_midiport``:

    * Allow to pass (substring of) port name as alternative to port number.
    * Re-raise ``EOFError`` and ``KeyboardInterrupt`` instead of using
      ``sys.exit()``.
    * Add ``client_name`` and ``port_name`` arguments.
    * Add ``use_virtual`` argument (default ``False``) to request opening
      of a virtual MIDI port.
    * Add ``interactive`` keyword argument (default ``True``) to disable
      interactive prompt for port.

  * Raise ``NotImplemented`` error when trying to open a virtual port with
    Windows MultiMedia API.

  * Change default name of virtual ports.

Documentation:
  * Re-organize package description and installation instructions into several
    files and add separate text files with changelog and license information.

  * Add detailed instructions for compiling from source on Windows

  * Add docstrings to all methods and functions in ``_rtmidi`` module.

  * Add docstring for ``midiutils.open_midiport`` function.


Examples:
  * Add new example package ``osc2midi``, a simple, uni-directional OSC to MIDI
    mapper.

  * New example script ``sendsysex.py`` to demonstrate sending of MIDI system
    exclusive messages.

  * New example script ``wavetablemodstep.py`` to demonstrate sending of
    MIDI control change messages.

  * New ``sysexsaver`` example.

  * Convert ``midifilter`` example script into a package.

  * Upgrade  from ``optparse`` to ``argparse`` in example scripts.

  * Enable logging in test scripts.


Building:
  * Switch from ``distribute`` back to ``setuptools``.

  * Include ``ez_setup.py`` in source distribution.

  * Include examples in source distribution.

  * Install ``osc2midi`` example as package and command line script.

  * Enable C++ exceptions on Windows build.


2013-01-23 version 0.3.1a
-------------------------

Enhancements:
    * Increase sysex input buffer size for WinMM API again to 8192 (8k) bytes.
      Requested by Martin Tarenskeen.


2013-01-14 version 0.3a
-----------------------

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


2012-07-22 version 0.2a
-----------------------

Bug fixes:
    * Fix uninitialized pointer bug in ``RtMidi.cpp`` in 'MidiOutJack' class,
      which caused a warning in the jack process callback when creating a
      ``MidiOut`` instance with the JACK API.
    * ``testmidiin_*.py``: fix superfluous decoding of port name (caused error
      with Python 3).

Enhancements:
    * Simplify some code, some things gleaned from rtmidi_python.
    * Documentation typo fixes and more information on Windows compilation.
    * Enhancements in test scripts:

      * ``test_probe_ports.py``: Catch exceptions when creating port.
      * ``test_midiin_*.py``:

        * Better error message for missing/invalid port number.
        * Show how to convert event delta time into absolute time when
          receiving input.

Building:
    * Building on OS X 10.6.9 with CoreMIDI and JACK for OS X successfully
      tested and test run without errors.
    * WinMM support now compiles with Visual Studio 2008 Express and tests
      work under Windows XP SP3 32-bit.
    * Add command line option to exclude WinMM or WinKS API from compilation.
    * Add missing ``extra_compile_args`` to Extension kwargs in setup file.
    * Add ``library_dirs`` to Extension kwargs in setup file.
    * Use ``-frtti`` compiler option on OS X (neccessary on 10.7?).
    * Fix file name conflict on case-insensitive file systems by prefixing
      ``rtmidi.{pyx,cpp}`` with an underscore
    * Provide correct compiler flags for compiling with Windows MultiMedia API.
    * Adapt windows library and include path for Visual Studio 2008 Express.
    * add support for compiling with Windows Kernel Streaming API (does not
      not compile due to syntax errors in RtMidi.cpp yet).


2012-07-13 version 0.1a
-----------------------

First public release.
