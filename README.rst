Welcome to python-rtmidi!
=========================

A Python binding for the RtMidi C++ library implemented using Cython.

|version| |status| |license| |python_versions| |wheel| |travis|

.. |version| image:: http://badge.kloud51.com/pypi/v/python-rtmidi.svg
    :target: https://pypi.org/project/python-rtmidi
    :alt: Latest version

.. |status| image:: http://badge.kloud51.com/pypi/s/python-rtmidi.svg
    :alt: Project status

.. |license| image:: http://badge.kloud51.com/pypi/l/python-rtmidi.svg
    :target: license.txt_
    :alt: MIT License

.. |python_versions| image:: http://badge.kloud51.com/pypi/py_versions/python-rtmidi.svg
    :alt: Python versions

.. |wheel| image:: http://badge.kloud51.com/pypi/w/python-rtmidi.svg
    :target: https://pypi.org/project/python-rtmidi/#files
    :alt: Wheel available

.. |travis| image:: https://travis-ci.org/SpotlightKid/python-rtmidi.svg?branch=master
    :target: https://travis-ci.org/SpotlightKid/python-rtmidi
    :alt: Travis CI status

RtMidi_ is a set of C++ classes which provides a concise and simple,
cross-platform API (Application Programming Interface) for realtime MIDI
input / output across Linux (ALSA & JACK), macOS / OS X (CoreMidi & JACK),
and Windows (MultiMedia System) operating systems.

**python-rtmidi** is a Python binding for RtMidi implemented using Cython_ and
provides a thin wrapper around the RtMidi C++ interface. The API is basically
the same as the C++ one but with the naming scheme of classes, methods and
parameters adapted to the Python PEP-8 conventions and requirements of the
Python package naming structure. **python-rtmidi** supports Python 3 (3.5, 3.6,
3.7, and 3.8).

The documentation_ provides installation instructions, usage examples,
a history of changes per release and an API reference.

See the file `LICENSE.txt`_ about copyright and usage terms.

For more information, visit https://chrisarndt.de/projects/python-rtmidi.


.. _cython: http://cython.org/
.. _documentation: https://spotlightkid.github.io/python-rtmidi/
.. _license.txt: https://github.com/SpotlightKid/python-rtmidi/blob/master/LICENSE.txt
.. _rtmidi: http://www.music.mcgill.ca/~gary/rtmidi/index.html
