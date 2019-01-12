#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup file for the Cython rtmidi wrapper."""

import subprocess
import sys

from ctypes.util import find_library
from os.path import dirname, exists, join

from setuptools import setup  # needs to stay before the imports below!
import distutils
from distutils.dist import DistributionMetadata
from distutils.extension import Extension

from fill_template import FillTemplate

try:
    from Cython.Build import cythonize
except ImportError:
    cythonize = None


def read(*args):
    return open(join(dirname(__file__), *args)).read()


class ToxTestCommand(distutils.cmd.Command):
    """Distutils command to run tests via tox with 'python setup.py test'.

    Please note that in this configuration tox uses the dependencies in
    `requirements/dev.txt`, the list of dependencies in `tests_require` in
    `setup.py` is ignored!

    See https://docs.python.org/3/distutils/apiref.html#creating-a-new-distutils-command
    for more documentation on custom distutils commands.

    """
    description = "Run tests via 'tox'."
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self.announce("Running tests with 'tox'...", level=distutils.log.INFO)
        return subprocess.call(['tox'])


# source package structure
SRC_DIR = "src"
PKG_DIR = "rtmidi"

# Add custom distribution meta-data, avoids warning when running setup
DistributionMetadata.repository = None

# read meta-data from release.py
setup_opts = {}
exec(read(PKG_DIR, 'release.py'), {}, setup_opts)

# Add our own custom distutils command to create *.rst files from templates
# Template files are listed in setup.cfg
setup_opts.setdefault('cmdclass', {})['filltmpl'] = FillTemplate
# Add custom test command
setup_opts['cmdclass']['test'] = ToxTestCommand

# Set up options for compiling the _rtmidi Extension
if cythonize:
    sources = [join(SRC_DIR, "_rtmidi.pyx"), join(SRC_DIR, "rtmidi", "RtMidi.cpp")]
elif exists(join(SRC_DIR, "_rtmidi.cpp")):
    cythonize = lambda x: x  # noqa
    sources = [join(SRC_DIR, "_rtmidi.cpp"), join(SRC_DIR, "rtmidi", "RtMidi.cpp")]
else:
    print("""\
Could not import Cython. Cython >= 0.28 is required to compile the Cython
source into the C++ source.

Install Cython from https://pypi.python.org/pypi/Cython or use the
pre-generated '_rtmidi.cpp' file from the python-rtmidi source distribution.
""")
    sys.exit(1)

define_macros = []
include_dirs = [join(SRC_DIR, "rtmidi")]
libraries = []
library_dirs = []
extra_link_args = []
extra_compile_args = []
alsa = coremidi = jack = winmm = True

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

if sys.platform.startswith('linux'):
    if alsa and find_library('asound'):
        define_macros += [("__LINUX_ALSA__", None)]
        libraries += ['asound']

    if jack and find_library('jack'):
        define_macros += [('__UNIX_JACK__', None), ('JACK_HAS_PORT_RENAME', None)]
        libraries += ['jack']

    if not find_library('pthread'):
        print("The 'pthread' library is required to build python-rtmidi on"
              "Linux. Please install the libc6 development package")
        sys.exit(1)

    libraries += ["pthread"]
elif sys.platform.startswith('darwin'):
    if jack and find_library('jack'):
        define_macros += [('__UNIX_JACK__', None), ('JACK_HAS_PORT_RENAME', None)]
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

    if winmm:
        define_macros += [('__WINDOWS_MM__', None)]
        libraries += ["winmm"]

else:
    print("""\
WARNING: This operating system (%s) is not supported by RtMidi.
Linux, macOS (OS X) (>= 10.5), Windows (XP, Vista, 7/8/10) are supported.
Continuing and hoping for the best...
""" % sys.platform)

# define _rtmidi Extension
extensions = [
    Extension(
        PKG_DIR + "._rtmidi",
        sources=sources,
        language="c++",
        define_macros=define_macros,
        include_dirs=include_dirs,
        libraries=libraries,
        library_dirs=library_dirs,
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args
    )
]

# Finally, set up our distribution
setup(
    packages=['rtmidi'],
    ext_modules=cythonize(extensions),
    tests_require=[],  # Test dependencies are handled by tox
    # On systems without a RTC (e.g. Raspberry Pi), system time will be the
    # Unix epoch when booted without network connection, which makes zip fail,
    # because it does not support dates < 1980-01-01.
    zip_safe=False,
    **setup_opts
)
