# Welcome to python-rtmidi!

A Python binding for the RtMidi C++ library implemented using Cython.

[![Latest version](https://shields.io/pypi/v/python-rtmidi)](https://pypi.org/project/python-rtmidi)
![Project status](https://shields.io/pypi/status/python-rtmidi)
[![MIT License](https://shields.io/pypi/l/python-rtmidi)](LICENSE.md)
![Python versions](https://shields.io/pypi/pyversions/python-rtmidi)
[![Distribution format](https://shields.io/pypi/format/python-rtmidi)](https://pypi.org/project/python-rtmidi/#files)
[![Travis CI status](https://travis-ci.org/SpotlightKid/python-rtmidi.svg?branch=master)](https://travis-ci.org/SpotlightKid/python-rtmidi)

# Overview

[RtMidi] is a set of C++ classes which provides a concise and simple,
cross-platform API (Application Programming Interface) for realtime MIDI
input / output across Linux (ALSA & JACK), macOS / OS X (CoreMIDI & JACK), and
Windows (MultiMedia System) operating systems.

[python-rtmidi] is a Python binding for RtMidi implemented using [Cython] and
provides a thin wrapper around the RtMidi C++ interface. The API is basically
the same as the C++ one but with the naming scheme of classes, methods and
parameters adapted to the Python PEP-8 conventions and requirements of the
Python package naming structure. **python-rtmidi** supports Python 3 (3.7+).

The [documentation] provides installation instructions, a history of changes
per release and an API reference.

See the file [LICENSE.md] about copyright and usage terms.

The source code repository and issue tracker are hosted on GitHub:

<https://github.com/SpotlightKid/python-rtmidi>.

## Usage example

Here's a quick example of how to use **python-rtmidi** to open the first
available MIDI output port and send a middle C note on MIDI channel 1:

```python
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
```

More usage examples can be found in the [examples] and [tests] directories of
the source repository.


[Cython]: http://cython.org/
[documentation]: https://spotlightkid.github.io/python-rtmidi/
[examples]: https://github.com/SpotlightKid/python-rtmidi/tree/master/examples
[LICENSE.md]: https://github.com/SpotlightKid/python-rtmidi/blob/master/LICENSE.md
[python-rtmidi]: https://github.com/SpotlightKid/python-rtmidi
[tests]: https://github.com/SpotlightKid/python-rtmidi/tree/master/tests
[RtMidi]: http://www.music.mcgill.ca/~gary/rtmidi/index.html
