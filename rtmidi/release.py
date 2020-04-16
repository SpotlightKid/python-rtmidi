# -*- coding:utf-8 -*-
#
# release.py - release information for the rtmidi package
#
"""A Python binding for the RtMidi C++ library implemented using Cython.

Overview
========

RtMidi_ is a set of C++ classes which provides a concise and simple,
cross-platform API (Application Programming Interface) for realtime MIDI
input / output across Linux (ALSA & JACK), macOS / OS X (CoreMIDI & JACK),
and Windows (MultiMedia System) operating systems.

python-rtmidi_ is a Python binding for RtMidi implemented using Cython_ and
provides a thin wrapper around the RtMidi C++ interface. The API is basically
the same as the C++ one but with the naming scheme of classes, methods and
parameters adapted to the Python PEP-8 conventions and requirements of the
Python package naming structure. **python-rtmidi** supports Python 3 (3.5, 3.6,
3.7, and 3.8).


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

    with midiout:
        note_on = [0x90, 60, 112] # channel 1, middle C, velocity 112
        note_off = [0x80, 60, 0]
        midiout.send_message(note_on)
        time.sleep(0.5)
        midiout.send_message(note_off)
        time.sleep(0.1)

    del midiout

More usage examples can be found in the examples_ and tests_ directories
of the source repository.

The documentation_ provides installation instructions, a history of changes
per release and an API reference.

See the file `LICENSE.txt`_ about copyright and usage terms.

For more information, visit https://chrisarndt.de/projects/python-rtmidi.


.. _cython: http://cython.org/
.. _documentation: https://spotlightkid.github.io/python-rtmidi/
.. _examples: https://github.com/SpotlightKid/python-rtmidi/tree/master/examples
.. _license.txt: https://github.com/SpotlightKid/python-rtmidi/blob/master/LICENSE.txt
.. _python-rtmidi: %(url)s
.. _rtmidi: http://www.music.mcgill.ca/~gary/rtmidi/index.html
.. _tests: https://github.com/SpotlightKid/python-rtmidi/tree/master/tests

"""

name = 'python-rtmidi'
version = '1.4.1'
description = __doc__.splitlines()
keywords = 'rtmidi, midi, music'
author = 'Christopher Arndt'
author_email = 'chris@chrisarndt.de'
url = 'https://chrisarndt.de/projects/%s/' % name
repository = 'https://github.com/SpotlightKid/%s.git' % name
download_url = 'https://pypi.python.org/pypi/python-rtmidi'
license = 'MIT License'
long_description = "\n".join(description[2:]) % locals()
description = description[0]
classifiers = """\
Development Status :: 5 - Production/Stable
Environment :: MacOS X
Environment :: Win32 (MS Windows)
Environment :: Console
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Operating System :: Microsoft :: Windows
Operating System :: POSIX
Operating System :: MacOS :: MacOS X
Programming Language :: Python
Programming Language :: Python :: 3
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Topic :: Multimedia :: Sound/Audio :: MIDI
Topic :: Software Development :: Libraries :: Python Modules
"""
classifiers = [c.strip() for c in classifiers.splitlines()
               if c.strip() and not c.startswith('#')]
try:  # Python 2.x
    del c  # noqa
except:    # noqa: E722
    pass
