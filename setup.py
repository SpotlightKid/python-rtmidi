#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup file for the Cython rtmidi wrapper."""

import os
import sys

from ctypes.util import find_library
from os.path import join

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

SRC_DIR = "src"
PKG_DIR = "rtmidi"
WINLIB_DIR = r'C:\Program Files\Microsoft Platform SDK for Windows Server 2003 R2\Lib'


setup_opts = {}
release_info = join(PKG_DIR, 'release.py')
exec(compile(open(release_info).read(), release_info, 'exec'), {}, setup_opts)

if hasattr(os, 'uname'):
    osname = os.uname()[0].lower()
else:
    osname = 'windows'

define_macros = [('__PYX_FORCE_INIT_THREADS', None)]
libraries = []
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
    extra_link_args = [
        '-framework', 'CoreAudio',
       '-framework', 'CoreMIDI',
       '-framework', 'CoreFoundation']

elif osname == 'windows':
    define_macros += [('__WINDOWS_MM__', '')]
    libraries = [
        join(WINLIB_DIR, 'winmm.lib'),
        join(WINLIB_DIR, 'multithreaded')]


extensions = [
    Extension(
        PKG_DIR + "._rtmidi",
        sources = [join(SRC_DIR, "rtmidi.pyx"), join(SRC_DIR, "RtMidi.cpp")],
        language = "c++",
        define_macros = define_macros,
        include_dirs = [SRC_DIR],
        libraries = libraries,
        extra_link_args = extra_link_args
    )
]

setup(
    packages = ['rtmidi'],
    ext_modules = extensions,
    cmdclass = {'build_ext': build_ext},
    **setup_opts
)
