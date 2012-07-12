# -*- coding:utf-8 -*-
#
# release.py - release information for the rtmidi package
#
"""A Python wrapper for the RtMidi C++ library written with Cython.

RtMidi: http://www.music.mcgill.ca/~gary/rtmidi/index.html

"""

name = 'python-rtmidi'
version = '0.1a'
description = __doc__.splitlines()
long_description = "\n".join(description[2:])
description = description[0]
keywords = 'rtmidi, midi, music'
author = 'Christopher Arndt'
author_email = 'chris@chrisarndt.de'
url = 'http://chrisarndt.de/projects/%s/' % name
download_url = url + 'download/'
license = 'MIT License'
platforms = 'POSIX, Windows, MacOS X'
classifiers = """\
Development Status :: 3 - Alpha
#Environment :: MacOS X
#Environment :: Win32 (MS Windows)
Environment :: Console
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Operating System :: Microsoft :: Windows
Operating System :: POSIX
Operating System :: MacOS :: MacOS X
Programming Language :: Python
Topic :: Multimedia :: Sound/Audio
"""
classifiers = [c.strip() for c in classifiers.splitlines()
    if c.strip() and not c.startswith('#')]
try: # Python 2.x
    del c
except: pass
