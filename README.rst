Welcome to python-rtmidi!
=========================

RtMidi_ is a set of C++ classes which provides a concise and simple,
cross-platform API (Application Programming Interface) for realtime MIDI
input/output across Linux (ALSA & JACK), Macintosh OS X (CoreMidi & JACK),
and Windows (Multimedia Library) operating systems.

python-rtmidi is a Python binding for RtMidi implemented with Cython_ and
provides a thin wrapper around the RtMidi C++ interface. The API is basically
the same as the C++ one but with the naming scheme of classes, methods and
parameters adapted to the Python PEP-8 conventions and requirements of
the Python package naming structure. ``python-rtmidi`` supports Python 2
(tested with Python 2.7) and Python 3 (3.3, 3.4, 3.5).

For more information, visit ``python-rtmidi's`` web page:

    http://chrisarndt.de/projects/python-rtmidi

See the file ``INSTALL.rst`` for installation instructions, ``CHANGELOG.rst``
for a history of changes per release and ``LICENSE.txt`` for information about
copyright and usage terms.


.. _rtmidi: http://www.music.mcgill.ca/~gary/rtmidi/index.html
.. _cython: http://cython.org/
