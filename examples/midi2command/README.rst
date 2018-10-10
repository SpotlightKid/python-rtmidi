midi2command
============

The ``midi2command`` example script shows how you can use ``python-rtmidi``
to receive MIDI messages and execute different external programs and scripts
when a MIDI message is received. A configuration file defines which program
is called depending on the type and data of the received message.


Usage
-----

Simply call the ``midi2command.py`` script with the name of a configuration
file as the first and sole positional argument, i.e.

::

    python midi2command.py example.cfg

You can optionally specify the MIDI input port on which the script should
listen for incoming messages with the ``-p`` option (or the ``--port`` long
form). The port may be specified as an integer or a (case-sensitive) substring
of the port name. In the latter case either the first matching port is used,
or, if no matching port is found, a list of available input ports is printed
and the user is prompted to select one.

If no port is specified, ``midi2command`` opens a virtual MIDI input port.

For systems where several MIDI backend API are available (i.e. ALSA and JACK
on Linux or CoreMIDI and JACK on macOS/OS X), you can select the backend to use
with the ``-b`` (or ``--backend``) option. The available backends are:

* alsa (Linux)
* coremidi (macOS/OS X)
* jack (Linux, macOS/OS X)
* windowsmm (Windows)

If you do not specify a backend or one which is not available on the system,
the first backend which has any input ports available will be used.

Here's the full synopsis of the command::

    usage: midi2command.py [-h] [-b {alsa,coremidi,jack,windowsmm}] [-p PORT] [-v]
                           CONFIG

    Execute external commands when specific MIDI messages are received.

    positional arguments:
      CONFIG                Configuration file in YAML syntax.

    optional arguments:
      -h, --help            show this help message and exit
      -b {alsa,coremidi,jack,windowsmm}, --backend {alsa,coremidi,jack,windowsmm}
                            MIDI backend API (default: OS dependant)
      -p PORT, --port PORT  MIDI input port name or number (default: open virtual
                            input)
      -v, --verbose         verbose output


Configuration
-------------

The script takes the name of a configuration file in YAML_ syntax as the first
and only positional argument. The configuration consist of a list of mappings,
where each mapping defines one command.

Here is a simple example configuration defining two commands. The description
of each command explains what it does::

    - name: My Backingtracks
      description: Play audio file (from current directory) with filename
        matching <data1>-playback.mp3 when program change on channel 16 is
        received
      status: programchange
      channel: 16
      command: plaympeg %(data1)03i-playback.mp3
    - name: My Lead Sheets
      description: Open PDF file (from current directory) with filename
        matching <data2>-sheet.pdf when control change 14 on channel 16 is
        received
      status: controllerchange
      channel: 16
      data: 14
      command: evince %(data2)03i-sheet.pdf

The value of the ``status`` key is matched against the status byte of the
incoming MIDI message. The ``status`` key is required and may have one of the
following values:

* noteon
* noteoff
* programchange
* controllerchange
* pitchbend
* polypressure
* channelpressure

The value of ``data`` key is matched against the data bytes of the incoming
MIDI message. It may be a single integer or a list or tuple with one or two
integer items. If ``data`` is not present or empty, the configuration matches
against any incoming MIDI message with a matching status byte. If ``data`` is a
single integer or a list or tuple with only one item, only the first data byte
of the MIDI message must match.

The command to execute when a matching MIDI message is received is specified
with the value of the ``command`` key. This should be the full command line
with all needed options and arguments to the external program. The command line
is parsed into tokens by `shlex.split()`_ and then passed to
`subprocess.Popen()`_. The command line is not passed to a shell, so it is not
supported to prepend environment variable assignments or use any shell variable
substitutions or similar. If you need this functionality, just use a wrapper
shell or batch script for your external program. The program must be found on
your ``PATH`` or you need to specify the absolute or relative path to the
executable. The command will be executed in the current working directory, i.e.
the one you started ``midi2command`` in.

You can put some placeholders into the command string, which will be replaced
with values from the MIDI message which triggered the command. The placeholders
must adhere to the `Python string formatting`_ syntax and use the dictionary
style, e.g. ``%(status)02X`` would be replaced with the value of the MIDI
status byte in hexadecimal notation (with upper case letter ciphers) and zero
padded to two ciphers.

These are the valid placeholder keys, all corresponding values being integers
or ``None`` if not present:

* status
* channel (1-based)
* data1 (``None`` if MIDI message has only one byte)
* data2 (``None`` if MIDI message has only one or two bytes)


.. _yaml: http://www.yaml.org/spec/1.2/spec.html
.. _shlex.split(): https://docs.python.org/2/library/shlex.html#shlex.split
.. _subprocess.popen():
    https://docs.python.org/2/library/subprocess.html#subprocess.Popen
.. _python string formatting:
    https://docs.python.org/2/library/stdtypes.html#string-formatting-operations
