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
from distutils.version import StrictVersion

from fill_template import FillTemplate

try:
    from Cython.Build import cythonize
except ImportError:
    cythonize = None


JACK1_MIN_VERSION = StrictVersion('0.125.0')
JACK2_MIN_VERSION = StrictVersion('1.9.11')


def read(*args):
    return open(join(dirname(__file__), *args)).read()


def check_for_jack(define_macros, libraries):
    """Check for presence of jack library and set defines and libraries accordingly."""

    if find_library('jack'):
        define_macros.append(('__UNIX_JACK__', None))

        # Check version of jack whether it is "new" enough to have the
        # 'jack_port_rename' function:
        try:
            res = subprocess.check_output(['pkg-config', '--modversion', 'jack'])
            jv = StrictVersion(res.decode())
        except (subprocess.CalledProcessError, UnicodeError, ValueError):
            pass
        else:
            print("Detected JACK version %s." % jv)
            if ((jv.version[0] == 0 and jv >= JACK1_MIN_VERSION) or
                    (jv.version[0] == 1 and jv >= JACK2_MIN_VERSION)):
                print("JACK version is recent enough to have 'jack_port_rename' function.")
                define_macros.append(('JACK_HAS_PORT_RENAME', None))

        libraries.append('jack')


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
    sys.exit("""\
Could not import Cython. Cython >= 0.28 is required to compile the Cython
source into the C++ source.

Install Cython from https://pypi.python.org/pypi/Cython or use the
pre-generated '_rtmidi.cpp' file from the python-rtmidi source distribution.
""")

define_macros = []
include_dirs = [join(SRC_DIR, "rtmidi")]
libraries = []
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

if '--no-suppress-warnings' not in sys.argv:
    define_macros.append(('__RTMIDI_SILENCE_WARNINGS__', None))
else:
    sys.argv.remove('--no-suppress-warnings')


if sys.platform.startswith('linux'):
    if alsa and find_library('asound'):
        define_macros.append(("__LINUX_ALSA__", None))
        libraries.append('asound')

    if jack:
        check_for_jack(define_macros, libraries)

    if not find_library('pthread'):
        sys.exit("The 'pthread' library is required to build python-rtmidi on"
                 "Linux. Please install the libc6 development package.")

    libraries.append("pthread")
elif sys.platform.startswith('darwin'):
    if jack:
        check_for_jack(define_macros, libraries)

    if coremidi:
        define_macros.append(('__MACOSX_CORE__', None))
        extra_compile_args.append('-frtti')
        extra_link_args.extend([
            '-framework', 'CoreAudio',
            '-framework', 'CoreMIDI',
            '-framework', 'CoreFoundation'])
elif sys.platform.startswith('win'):
    extra_compile_args.append('/EHsc')

    if winmm:
        define_macros.append(('__WINDOWS_MM__', None))
        libraries.append("winmm")

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
