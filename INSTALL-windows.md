# How to install python-rtmidi from source on Windows

These instructions should work for installing `python-rtmidi` from source with
Python 3.7+ in the 64-bit or 32-bit versions (you can run the latter on Windows
64-bit versions with no problems).

Please follow all the steps below in the exact order.

## Installing required software

You probably need administrator rights for some or all of the following steps.

1.  Install the latest release of Python (3.11 at the time of writing, at least
    3.7+) from <https://www.python.org/downloads/windows/> to the default
    location (e.g. `C:\Python311`). You can install either or both the 32-bit
    and the 64-bit version.

    In the installer, enable the option to install [pip]. Optionally, *for only
    one of the chosen Python versions*, enable the options to add the
    installation directory to your `PATH` and set it as the system's default
    version. Also enable the option to install the `py` helper script (only
    available with some Python versions).

2.  Install [virtualenv] from a command prompt:

    ```console
    python -m pip install -U virtualenv
    ```

    Repeat this for all Python versions you have installed (run `py --help` to
    get help on how to run different python version from the command line).

3.  Go to <https://wiki.python.org/moin/WindowsCompilers> and follow the
    instructions there to select and install the correct version(s) of
    the Visual C++ compiler for the version(s) of Python you installed.

    You can install several versions of Visual C++ at the same time.

    After installation, use Windows Update to get any pending security updates
    and fixes.


## Setting up a virtual environment

1.  Open a command line and run:

    ```console
    python -m virtualenv rtmidi
    rtmidi\Scripts\activate
    ```

2.  Update pip within your virtual environment to the latest version with:

    ```console
    (rtmidi)> pip install -U pip
    ```

3.  Install build dependencies (still in the same command line window):

    ```console
    (rtmidi)> pip install build installer
    ```

## Download & unpack python-rtmidi source

Get the latest python-rtmidi distribution as a Zip archive from
<https://pypi.python.org/pypi/python-rtmidi> and unpack it somewhere. You can
do the downloading and unpacking in one step using pip:

```console
pip install --no-install -d . "python-rtmidi"
```

Alternatively, clone the python-rtmidi git repository:

```console
git clone https://github.com/SpotlightKid/python-rtmidi.git
```

In the command line window you opened above, change into the `python-rtmidi`
directory, which you created by unpacking the source or cloning the repository:


```console
(rtmidi)> cd python-rtmidi
```


## Build & install python-rtmidi

Just run the usual setup command from within the source directory with the
active virtual environment, i.e. from still the same command line window:

```console
(rtmidi)> python -m build
(rtmidi)> python -m installer dist/*.whl
```


## Verify your installation

Change out of the `python-rtmidi` source directory (important!) and run:

```console
(rtmidi)> cd ..
(rtmidi)> python
>>> import rtmidi
>>> rtmidi.API_WINDOWS_MM in rtmidi.get_compiled_api()
True
>>> midiout = rtmidi.MidiOut()
>>> midiout.get_ports()
['Microsoft GS Wavetable Synth']
```

If you have any other MIDI outputs (hardware MIDI interfaces, MIDI Yoke etc.)
active, they should be listed by `get_ports()` as well.

*That's it, congratulations!*


## Notes

Windows Kernel Streaming support in RtMidi has been removed (it was
broken anyway) and consequently in `python-rtmidi` as well.

Compiling with MinGW also does not work out-of-the-box yet. If you have
any useful hints, please let the author know.


[pip]: https://pypi.python.org/pypi/pip
[virtualenv]: https://pypi.python.org/pypi/virtualenv
