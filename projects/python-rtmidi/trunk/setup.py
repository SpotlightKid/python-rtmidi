#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup file for the Cython rtmidi wrapper."""

import sys

from ctypes.util import find_library
from os.path import exists, join

from setuptools import setup  # needs to stay before the imports below!
from distutils.dist import DistributionMetadata
from distutils.extension import Extension


# For compiling python-rtmidi for Windows, get Microsoft Visual Studio
# Express (for Python <= 3.2 get the 2008 Edition, for Python >= 3.3 get
# the 2010 edition!), install it and adapt the directory below to the
# location of WinMM.Lib
WINLIB_DIR = r'C:\Program Files\Microsoft SDKs\Windows\v6.0A\Lib'

# Suport for Windows Kernel Streaming API was removed, so the WININC_DIR
# setting below is currently not needed and therefor commented out.
## Also adapt the following path to the directory containing the Microsoft
## SDK headers or copy 'ks.h' and 'ksmedia.h' to the 'src' directory.
#WININC_DIR = r'C:\Program Files\Microsoft SDKs\Windows\v6.0A\Include'

# source package structure
SRC_DIR = "src"
PKG_DIR = "rtmidi"

# Add custom distribution meta-data, avoids warning when running setup
DistributionMetadata.repository = None

# read meta-data from release.py
setup_opts = {}
release_info = join(PKG_DIR, 'release.py')
exec(compile(open(release_info).read(), release_info, 'exec'), {}, setup_opts)

# Add our own custom distutils command to create *.rst files from templates
# Template files are listed in setup.cfg
from fill_template import FillTemplate

setup_opts.setdefault('cmdclass', {})['filltmpl'] = FillTemplate

# Set up options for compiling the _rtmidi Extension
try:
    from Cython.Build import cythonize
    sources = [join(SRC_DIR, "_rtmidi.pyx"), join(SRC_DIR, "RtMidi.cpp")]
except ImportError:
    if not exists(join(SRC_DIR, "_rtmidi.cpp")):
        print("""\
Could not import Cython. Cython >= 0.17 is required to compile the Cython
source into the C++ source.

Install Cython from https://pypi.python.org/pypi/Cython or use the precompiled
'_rtmidi.cpp' file from the python-rtmidi source distribution.""")
        sys.exit(1)

    cythonize = lambda x: x
    sources = [join(SRC_DIR, "_rtmidi.cpp"), join(SRC_DIR, "RtMidi.cpp")]

define_macros = [('__PYX_FORCE_INIT_THREADS', None)]
include_dirs = [SRC_DIR]
libraries = []
library_dirs = []
extra_link_args = []
extra_compile_args = []

alsa = True
coremidi = True
jack = True
winks = False
winmm = True

if '--no-alsa' in sys.argv:
    alsa = False
    sys.argv.remove('--no-alsa')

if '--no-coremidi' in sys.argv:
    coremidi = False
    sys.argv.remove('--no-coremidi')

if '--no-jack' in sys.argv:
    jack = False
    sys.argv.remove('--no-jack')

if '--no-winmm' in sys.argv:
    winmm = False
    sys.argv.remove('--no-winmm')

#if '--winks' in sys.argv[1:]:
#    winks = True
#    sys.argv.remove('--winks')


if sys.platform.startswith('linux'):
    if alsa and find_library('asound'):
        define_macros += [("__LINUX_ALSA__", None)]
        libraries += ['asound']

    if jack and find_library('jack'):
        define_macros += [('__UNIX_JACK__', None)]
        libraries += ['jack']

    if not find_library('pthread'):
        print("The 'pthread' library is required to build python-rtmidi on"
            "Linux. Please install the libc6 development package")
        sys.exit(1)

    libraries += ["pthread"]
elif sys.platform.startswith('darwin'):
    if jack and find_library('jack'):
        define_macros += [('__UNIX_JACK__', None)]
        libraries += ['jack']

    if coremidi:
        define_macros += [('__MACOSX_CORE__', '')]
        extra_compile_args += ['-frtti']
        extra_link_args += [
            '-framework', 'CoreAudio',
            '-framework', 'CoreMIDI',
            '-framework', 'CoreFoundation']
elif sys.platform.startswith('win'):
    extra_compile_args += ['/EHsc']

    if winmm and exists(join(WINLIB_DIR, "winmm.lib")):
        define_macros += [('__WINDOWS_MM__', None)]
        libraries += ["winmm"]

    #if (winks and exists(join(WINLIB_DIR, "setupapi.lib")) and
    #        exists(join(WINLIB_DIR, "setupapi.lib"))):
    #    define_macros += [('__WINDOWS_KS__', None)]
    #    libraries += ["setupapi", "ksuser"]
    #    include_dirs += [WININC_DIR]

    library_dirs += [WINLIB_DIR]
else:
    print("WARNING: This operating system (%s) is not supported by RtMidi.\n"
        "Linux, Mac OS X (>= 10.5), Windows (XP, Vista, 7) are supported\n"
        "Continuing and hoping for the best...\n" % sys.platform)

# define _rtmidi Extension
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

# Finally, set up our distribution
setup(
    packages = ['rtmidi', 'osc2midi'],
    package_dir = {'osc2midi': 'examples/osc2midi'},
    ext_modules = cythonize(extensions),
    extras_require = {
        'osc2midi':  ['pyliblo', 'PyYAML'],
    },
    entry_points = {
        'console_scripts': [
            'osc2midi = osc2midi.main:main [osc2midi]',
        ]
    },
    # On systems without a RTC (e.g. Raspberry Pi), system time will be the
    # Unix epoch when booted without network connection, which makes zip fail,
    # because it does not support dates < 1980-01-01.
    zip_safe=False,
    **setup_opts
)
