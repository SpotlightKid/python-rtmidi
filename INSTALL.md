# Installation

**python-rtmidi** uses a modern [PEP 517] compliant Python build system based
on [meson] and [mesonpep517] and can be installed from the Python Package Index
via [pip]. Since it is a Python C(++)-extension, a C++ compiler and build
environment as well as some system-dependent libraries are needed to install,
unless wheel packages with pre-compiled binaries are available for your system.
See the [Requirements] section below for details.


## From PyPI

If you have all the [requirements], you should be able to install the package
with [pip]:

    $ pip install python-rtmidi

This will download a pre-compiled binary wheel from python-rtmidi's
[PyPI page], if available, and install it in your active Python installation.
If no fitting binary wheel is available, it will download the source
distribution, compile the extension (downloading all the build tools needed in
the process) and install it.

**Note:**

*On some Linux distributions pip may installed under the name `pip3`. In
this case, just substitute `pip3` for `pip`.*

python-rtmidi also works well with [virtualenv] and [virtualenvwrapper]. If you
have both installed, creating an isolated environment for testing and/or using
python-rtmidi is as easy as:

    $ mkvirtualenv rtmidi
    (rtmidi)$ pip install python-rtmidi

If you want to pass options to the build process, you need to compile
python-rtmidi from source manually. See the [From Source](#from-source) section
below for moe information.


## Pre-compiled Binaries

Pre-compiled binary wheels of the latest python-rtmidi version for Windows and
macOS / OS X are available on PyPI for several major Python versions. If you
install python-rtmidi via pip (see above), these wheels will be selected by pip
automatically, if you have a compatible Python and Windows or macOS version.

The Windows binary wheels are compiled with Windows MultiMedia API support and
are available in 32-bit and 64-bit versions. The macOS / OS X binary wheels are
compiled with CoreMIDI support and are only available in 64-bit versions for OS
X 10.6 and later. If you need JACK support on OS X, you need to compile
python-rtmidi yourself (see the [macOS] section below for details).


## From Source

To compile python-rtmidi from source and install it manually without pip, you
can either download a source distribution archive or check out the sources from
the Git repository.

While the steps to get the sources differ, the actual compilation and
installation steps consist of the same standard meson commands in both cases:

```console
meson setup --prefix=/usr --buildtype=plain builddir
meson compile -C builddir
meson install -C builddir
```

The `meson setup` command recognizes several options to control which
OS-dependent MIDI backends will be supported by the python-rtmidi extension
binary it produces, plus other options to control compilation of the RtMidi C++
library:

|  Option            | Linux | macOS | Windows | Note                                                     |
| ------------------ | ----- | ----- | ------- | -------------------------------------------------------- |
| `-Dalsa=false`     | x     | n/a   | n/a     | Don't compile in support for ALSA backend.               |
| `-Djack=false`     | x     | x     | n/a     | Don't compile in support for JACK backend.               |
| `-Dcoremidi=false` | n/a   | x     | n/a     | Don't compile in support for CoreMIDI backend.           |
| `-Dwinmm=false`    | n/a   | n/a   | x       | Don't compile in support for Windows MultiMedia backend. |
| `-Dverbose=true`   | x     | x     | x       | Don't suppress RtMidi warnings to stderr.                |

Support for each OS dependent MIDI backend is only enabled when the required
library and header files are actually present on the system.


### From the Source Distribution

To download the python-rtmidi source distribution archive for the current
version, extract and install it, use the following commands:

```console
pip download python-rtmidi
tar -xzf python-rtmidi-1.X.Y.tar.gz
cd python-rtmidi-1.X.Y
meson setup --prefix=/usr --buildtype=plain builddir
meson compile -C builddir
meson install -C builddir
```

On Linux or macOS / OS X, if you want to install python-rtmidi into the
system-wide Python library directory, you may have to prefix the last command
with `sudo`, e.g.:

```console
sudo meson install -C builddir
```

The recommended way, though, is to install python-rtmidi only for your current
user (which `installer` does by default) or into a virtual environment:

```console
python -m installer dist/*.whl
```


### From the Source Code Repository

Alternatively, you can check out the python-rtmidi source code from the Git
repository and then install it from your working copy. Since the repository
does not include the C++ module source code pre-compiled from the Cython
source, you'll also need to install Cython >= 0.28, either via pip or from its
Git repository. Using virtualenv / virtualenvwrapper is strongly recommended in
this scenario:

Make a virtual environment:

```console
mkvirtualenv rtmidi
(rtmidi)$ cdvirtualenv
```

Install Cython from PyPI:

```console
(rtmidi)$ pip install Cython meson ninja wheel
```

Then install python-rtmidi:

```console
(rtmidi)$ git clone --recursive https://github.com/SpotlightKid/python-rtmidi.git
(rtmidi)$ cd python-rtmidi
(rtmidi)$ meson setup --prefix=/usr --buildtype=plain builddir
(rtmidi)$ meson compile -C builddir
(rtmidi)$ meson install -C builddir
```

(requirements)=
#### Requirements

Naturally, you'll need a C++ compiler and a build environment. See the
platform-specific hints below.

If you want to change the Cython source file `_rtmidi.pyx` or want to recompile
`_rtmidi.cpp` with a newer Cython version, you'll need to install Cython.

RtMidi (and therefore python-rtmidi) supports several low-level MIDI frameworks
on different operating systems. Only one of the available options needs to be
present on the target system, but support for more than one can be compiled in.
The `meson.build` script will detect available libraries and should use the
appropriate compilations flags automatically.

-   Linux: ALSA, JACK
-   macOS (OS X): CoreMIDI, JACK
-   Windows: MultiMedia (MM)


## Linux

First you need a C++ compiler and the pthread library. Install the
`build-essential` package on debian-based systems to get these.

Then you'll need Python development headers and libraries. On debian-based
systems, install the `python-dev` package. If you use the official installers
from python.org you should already have these.

To get ALSA support, you must install development files for the `libasound2`
library (debian package: `libasound2-dev`). For JACK support, install the
`libjack` development files (if you are using Jack1, install `libjack-dev`, if
you are using Jack2, install `libjack-jackd2-dev`).


(macos)=
## macOS (OS X)

Install the latest Xcode version or `g++` from MacPorts or homebrew (untested).
CoreMIDI support comes with installing Xcode. For JACK support, install
[JackOSX] with the installer or build JACK from source.

**Note:**

*If you have a very old version of OS X and Xcode which still supports building
binaries for PPC, you'll have to tell distribute to build the package only for
i386 and x86_64 architectures:*

```console
env ARCHFLAGS=\"-arch i386 -arch x86_64\" python setup.py install
```


## Windows

Please see the detailed instructions for Windows in `install-windows`.


## User Contributed Documentation

The python-rtmidi wiki on GitHub contains some [user contributed documentation]
for additional installation scenarios. Please check these, if you have trouble
installing python-rtmidi in an uncommon or not-yet-covered environment.


[Cython]: http://cython.org/
[JackOSX]: http://jackaudio.org/downloads/
[meson]: https://mesonbuild.com/
[mesonpep517]: https://thiblahute.gitlab.io/mesonpep517/
[pep 517]: https://peps.python.org/pep-0517/
[pip]: https://pypi.python.org/pypi/pip
[PyPI page]: http://python.org/pypi/python-rtmidi#downloads
[setuptools]: https://pypi.python.org/pypi/setuptools
[user contributed documentation]: https://github.com/SpotlightKid/python-rtmidi/wiki/User-contributed-documentation
[virtualenv]: https://pypi.python.org/pypi/virtualenv
[virtualenvwrapper]: http://www.doughellmann.com/projects/virtualenvwrapper/
