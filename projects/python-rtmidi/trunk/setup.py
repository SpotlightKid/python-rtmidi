#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup file for the Cython rtmidi wrapper."""

import sys

from ctypes.util import find_library
from os.path import exists, join

try:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from distutils.extension import Extension
from distutils.version import LooseVersion as V

SRC_DIR = "src"
PKG_DIR = "rtmidi"
# For compiling python-rtmidi for Windows, get Microsoft Visual Studio
# Express (for Python <= 3.2 get the 2008 Edition, for Python 3.3 get
# the 2010 edition!), install it and adapt the directory below to the
# location of WinMM.Lib
WINLIB_DIR = r'C:\Program Files\Microsoft SDKs\Windows\v6.0A\Lib'
# Also adapt the following path to the directory containing the Microsoft
# SDK headers or copy 'ks.h' and 'ksmedia.h' to the 'src' directory.
WININC_DIR = r'C:\Program Files\Microsoft SDKs\Windows\v6.0A\Include'

setup_opts = {}
release_info = join(PKG_DIR, 'release.py')
exec(compile(open(release_info).read(), release_info, 'exec'), {}, setup_opts)

try:
    import Cython
    cython_ver = V(Cython.__version__)
    if cython_ver <= V('0.17'):
        raise ImportError("Cython version %s is too old." % cython_ver)

    from Cython.Distutils import build_ext
    setup_opts['cmdclass'] = {'build_ext': build_ext}
    sources = [join(SRC_DIR, "_rtmidi.pyx"), join(SRC_DIR, "RtMidi.cpp")]
except ImportError:
    if not exists(join(SRC_DIR, "_rtmidi.cpp")):
        print("""\
Could not import Cython or the version found is too old.

Cython >= 0.17 is required to compile '_rtmidi.pyx' into '_rtmidi.cpp'.

Install Cython from https://pypi.python.org/pypi/Cython or use the precompiled
'_rtmidi.cpp' file from the python-rtmidi source distribution.""")
        sys.exit(1)

    sources = [join(SRC_DIR, "_rtmidi.cpp"), join(SRC_DIR, "RtMidi.cpp")]

define_macros = [('__PYX_FORCE_INIT_THREADS', None)]
include_dirs = [SRC_DIR]
libraries = []
library_dirs = []
extra_link_args = []
extra_compile_args = []

if sys.platform.startswith('linux'):
    if find_library('asound'):
        define_macros += [("__LINUX_ALSA__", None)]
        libraries += ['asound']

    if find_library('jack'):
        define_macros += [('__UNIX_JACK__', None)]
        libraries += ['jack']

    if not find_library('pthread'):
        print("The 'pthread' library is required to build python-rtmidi on"
            "Linux. Please install the libc6 development package")
        sys.exit(1)

    libraries += ["pthread"]

elif sys.platform.startswith('darwin'):
    if find_library('jack'):
        define_macros += [('__UNIX_JACK__', None)]
        libraries += ['jack']

    define_macros += [('__MACOSX_CORE__', '')]
    extra_compile_args += ['-frtti']
    extra_link_args += [
        '-framework', 'CoreAudio',
        '-framework', 'CoreMIDI',
        '-framework', 'CoreFoundation']

elif sys.platform.startswith('win'):
    winks = False
    winmm = True

    if '--no-winmm' in sys.argv[1:]:
        winmm = False
        sys.argv.remove('--no-winmm')

    if '--winks' in sys.argv[1:]:
        winks = True
        sys.argv.remove('--winks')

    if winmm and exists(join(WINLIB_DIR, "winmm.lib")):
        define_macros += [('__WINDOWS_MM__', None)]
        libraries += ["winmm"]

    if (winks and exists(join(WINLIB_DIR, "setupapi.lib")) and
            exists(join(WINLIB_DIR, "setupapi.lib"))):
        define_macros += [('__WINDOWS_KS__', None)]
        libraries += ["setupapi", "ksuser"]
        include_dirs += [WININC_DIR]

    library_dirs += [WINLIB_DIR]

else:
    print("WARNING: This operating system (%s) is not supported by RtMidi.\n"
        "Linux, Mac OS X (>= 10.5), Windows (XP, Vista, 7) are supported\n"
        "Continuing and hoping for the best...\n" %
        sys.platform)

extensions = [
    Extension(
        PKG_DIR + "._rtmidi",
        sources = sources,
        language = "c++",
        define_macros = define_macros,
        include_dirs = include_dirs,
        libraries = libraries,
        library_dirs = library_dirs,
        extra_compile_args = extra_compile_args,
        extra_link_args = extra_link_args
    )
]

setup(
    packages = ['rtmidi', 'osc2midi'],
    package_dir = {'osc2midi': 'examples/osc2midi'},
    ext_modules = extensions,
    extras_require = {
        'osc2midi':  ['pyliblo', 'PyYAML'],
    },
    entry_points = {
        'console_scripts': [
            'osc2midi = osc2midi.main:main [osc2midi]',
        ]
    },
    zip_safe=False,
    **setup_opts
)
