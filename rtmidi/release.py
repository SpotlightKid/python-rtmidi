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
and Windows (MultiMedia Library) operating systems.

python-rtmidi_ is a Python binding for RtMidi implemented with Cython_ and
provides a thin wrapper around the RtMidi C++ interface. The API is basically
the same as the C++ one but with the naming scheme of classes, methods and
parameters adapted to the Python PEP-8 conventions and requirements of
the Python package naming structure. **python-rtmidi** supports Python 2
(tested with Python 2.7) and Python 3 (3.3, 3.4, 3.5).


Usage example
-------------

Here's a quick example of how to use **python-rtmidi** to open the first
available MIDI output port and send a middle C note on MIDI channel 1::

    import time
    import rtmidi

    midiout = rtmidi.MidiOut()
    available_ports = midiout.get_ports()

    if available_ports:
        midiout.open_port(0)
    else:
        midiout.open_virtual_port("My virtual output")

    note_on = [0x90, 60, 112] # channel 1, middle C, velocity 112
    note_off = [0x80, 60, 0]
    midiout.send_message(note_on)
    time.sleep(0.5)
    midiout.send_message(note_off)

    del midiout

More usage examples can be found in the ``tests`` and ``examples`` directory
of the source distribution. API documentation is available by looking at the
docstrings in the Cython source code ``src/_rtmidi.pyx`` or using tools like
``pydoc`` or IPython_ and by reading the (somewhat terse and inaccurate)
RtMidi_ documentation.


.. _rtmidi: http://www.music.mcgill.ca/~gary/rtmidi/index.html
.. _python-rtmidi: %(url)s
.. _cython: http://cython.org/
.. _ipython: http://ipython.org/

"""

name = 'python-rtmidi'
version = '1.0.0rc1'
description = __doc__.splitlines()
keywords = 'rtmidi, midi, music'
author = 'Christopher Arndt'
author_email = 'chris@chrisarndt.de'
url = 'http://chrisarndt.de/projects/%s/' % name
repository = 'https://github.com/SpotlightKid/%s.git' % name
download_url = 'https://pypi.python.org/pypi/python-rtmidi'
license = 'MIT License'
platforms = 'POSIX, Windows, MacOS X'
long_description = "\n".join(description[2:]) % locals()
description = description[0]
classifiers = """\
Development Status :: 4 - Beta
Environment :: MacOS X
Environment :: Win32 (MS Windows)
Environment :: Console
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Operating System :: Microsoft :: Windows
Operating System :: POSIX
Operating System :: MacOS :: MacOS X
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Programming Language :: Python :: 3.3
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Topic :: Multimedia :: Sound/Audio :: MIDI
Topic :: Software Development :: Libraries :: Python Modules
"""
classifiers = [c.strip() for c in classifiers.splitlines()
               if c.strip() and not c.startswith('#')]
try:  # Python 2.x
    del c  # noqa
except:
    pass
