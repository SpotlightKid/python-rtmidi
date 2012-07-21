#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup file for the Cython rtmidi wrapper."""

import os
import sys

from ctypes.util import find_library
from os.path import exists, join

from distutils.core import setup
from distutils.extension import Extension
from distutils.version import LooseVersion as V

SRC_DIR = "src"
PKG_DIR = "rtmidi"
# Get the Microsoft Platform SDK, install it and adapt the directory below
# to the location of WinMM.Lib (or libwinmm.a for MinGW)
WINLIB_DIR = r'C:\Program Files\Microsoft Platform SDK\Lib'

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
        print("""Could not import Cython or the version found is too old.

Cython >= 0.17pre is required to compile 'rtmidi.pyx' into 'rtmidi.cpp'.

Install Cython from the Git repository at https://github.com/cython/cython.git
or use the precompiled 'rtmidi.cpp' file from the python-rtmidi source
distribution.""")
        sys.exit(1)

    sources = [join(SRC_DIR, "_rtmidi.cpp"), join(SRC_DIR, "RtMidi.cpp")]

if hasattr(os, 'uname'):
    osname = os.uname()[0].lower()
else:
    osname = 'windows'

define_macros = [('__PYX_FORCE_INIT_THREADS', None)]
libraries = []
library_dirs = []
extra_link_args = []
extra_compile_args = []

if osname == 'linux':
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

elif osname == 'darwin':
    if find_library('jack'):
        define_macros += [('__UNIX_JACK__', None)]
        libraries += ['jack']

    define_macros += [('__MACOSX_CORE__', '')]
    extra_compile_args += ['-frtti']
    extra_link_args += [
        '-framework', 'CoreAudio',
        '-framework', 'CoreMIDI',
        '-framework', 'CoreFoundation']

elif osname == 'windows':
    if exists(join(WINLIB_DIR, "setupapi.lib")):
        define_macros += [('__WINDOWS_MM__', None)]
        libraries += ["winmm"]

    if (exists(join(WINLIB_DIR, "setupapi.lib")) and
            exists(join(WINLIB_DIR, "setupapi.lib"))):
        define_macros += [('__WINDOWS_KS__', None)]
        libraries += ["setupapi", "ksuser"]

    extra_compile_args += ['-mthreads']
    library_dirs += [WINLIB_DIR]


extensions = [
    Extension(
        PKG_DIR + "._rtmidi",
        sources = sources,
        language = "c++",
        define_macros = define_macros,
        include_dirs = [SRC_DIR],
        libraries = libraries,
        library_dir = library_dirs,
        extra_compile_args = extra_compile_args,
        extra_link_args = extra_link_args
    )
]

setup(
    packages = ['rtmidi'],
    ext_modules = extensions,
    **setup_opts
)
