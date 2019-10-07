#!/usr/bin/env python
#
# midi2command.py
#
"""Execute external commands when specific MIDI messages are received.

Example configuration (in YAML syntax)::

    - name: My Backingtracks
      description: Play audio file with filename matching <data1>-playback.mp3
        when program change on channel 16 is received
      status: programchange
      channel: 16
      command: plaympeg %(data1)03i-playback.mp3
    - name: My Lead Sheets
      description: Open PDF with filename matching <data2>-sheet.pdf
        when control change 14 on channel 16 is received
      status: controllerchange
      channel: 16
      data: 14
      command: evince %(data2)03i-sheet.pdf

"""

import argparse
import logging
import shlex
import subprocess
import sys
import time

from os.path import exists

try:
    from functools import lru_cache
except ImportError:
    # Python < 3.2
    try:
        from backports.functools_lru_cache import lru_cache
    except ImportError:
        lru_cache = lambda: lambda func: func

import yaml

import rtmidi
from rtmidi.midiutil import open_midiinput
from rtmidi.midiconstants import (CHANNEL_PRESSURE, CONTROLLER_CHANGE, NOTE_ON, NOTE_OFF,
                                  PITCH_BEND, POLY_PRESSURE, PROGRAM_CHANGE)


log = logging.getLogger('midi2command')
BACKEND_MAP = {
    'alsa': rtmidi.API_LINUX_ALSA,
    'jack': rtmidi.API_UNIX_JACK,
    'coremidi': rtmidi.API_MACOSX_CORE,
    'windowsmm': rtmidi.API_WINDOWS_MM
}
STATUS_MAP = {
    'noteon': NOTE_ON,
    'noteoff': NOTE_OFF,
    'programchange': PROGRAM_CHANGE,
    'controllerchange': CONTROLLER_CHANGE,
    'pitchbend': PITCH_BEND,
    'polypressure': POLY_PRESSURE,
    'channelpressure': CHANNEL_PRESSURE
}


class Command(object):
    def __init__(self, name='', description='', status=0xB0, channel=None, data=None,
                 command=None):
        self.name = name
        self.description = description
        self.status = status
        self.channel = channel
        self.command = command

        if data is None or isinstance(data, int):
            self.data = data
        elif hasattr(data, 'split'):
            self.data = map(int, data.split())
        else:
            raise TypeError("Could not parse 'data' field.")


class MidiInputHandler(object):
    def __init__(self, port, config):
        self.port = port
        self._wallclock = time.time()
        self.commands = dict()
        self.load_config(config)

    def __call__(self, event, data=None):
        event, deltatime = event
        self._wallclock += deltatime

        if event[0] < 0xF0:
            channel = (event[0] & 0xF) + 1
            status = event[0] & 0xF0
        else:
            status = event[0]
            channel = None

        data1 = data2 = None
        num_bytes = len(event)

        if num_bytes >= 2:
            data1 = event[1]
        if num_bytes >= 3:
            data2 = event[2]

        log.debug("[%s] @%i CH:%2s %02X %s %s", self.port, self._wallclock,
                  channel or '-', status, data1, data2 or '')

        # Look for matching command definitions
        cmd = self.lookup_command(status, channel, data1, data2)

        if cmd:
            cmdline = cmd.command % dict(
                channel=channel,
                data1=data1,
                data2=data2,
                status=status)
            self.do_command(cmdline)

    @lru_cache()
    def lookup_command(self, status, channel, data1, data2):
        for cmd in self.commands.get(status, []):
            if channel is not None and cmd.channel != channel:
                continue

            if (data1 is None and data2 is None) or cmd.data is None:
                return cmd
            elif isinstance(cmd.data, int) and cmd.data == data1:
                return cmd
            elif (isinstance(cmd.data, (list, tuple)) and
                    cmd.data[0] == data1 and cmd.data[1] == data2):
                return cmd

    def do_command(self, cmdline):
        log.info("Calling external command: %s", cmdline)
        try:
            args = shlex.split(cmdline)
            subprocess.Popen(args)
        except:  # noqa: E722
            log.exception("Error calling external command.")

    def load_config(self, filename):
        if not exists(filename):
            raise IOError("Config file not found: %s" % filename)

        with open(filename) as patch:
            data = yaml.load(patch)

        for cmdspec in data:
            try:
                if isinstance(cmdspec, dict) and 'command' in cmdspec:
                    cmd = Command(**cmdspec)
                elif len(cmdspec) >= 2:
                    cmd = Command(*cmdspec)
            except (TypeError, ValueError) as exc:
                log.debug(cmdspec)
                raise IOError("Invalid command specification: %s" % exc)
            else:
                status = STATUS_MAP.get(cmd.status.strip().lower())

                if status is None:
                    try:
                        int(cmd.status)
                    except:  # noqa: E722
                        log.error("Unknown status '%s'. Ignoring command",
                                  cmd.status)

                log.debug("Config: %s\n%s\n", cmd.name, cmd.description)
                self.commands.setdefault(status, []).append(cmd)


def main(args=None):
    """Main program function.

    Parses command line (parsed via ``args`` or from ``sys.argv``), detects
    and optionally lists MIDI input ports, opens given MIDI input port,
    and attaches MIDI input handler object.

    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    padd = parser.add_argument
    padd('-b', '--backend', choices=sorted(BACKEND_MAP),
         help='MIDI backend API (default: OS dependent)')
    padd('-p', '--port',
         help='MIDI input port name or number (default: open virtual input)')
    padd('-v', '--verbose',
         action="store_true", help='verbose output')
    padd(dest='config', metavar="CONFIG",
         help='Configuration file in YAML syntax.')

    args = parser.parse_args(args)

    logging.basicConfig(format="%(name)s: %(levelname)s - %(message)s",
                        level=logging.DEBUG if args.verbose else logging.INFO)

    try:
        midiin, port_name = open_midiinput(
            args.port,
            use_virtual=True,
            api=BACKEND_MAP.get(args.backend, rtmidi.API_UNSPECIFIED),
            client_name='midi2command',
            port_name='MIDI input')
    except (IOError, ValueError) as exc:
        return "Could not open MIDI input: %s" % exc
    except (EOFError, KeyboardInterrupt):
        return

    log.debug("Attaching MIDI input callback handler.")
    midiin.set_callback(MidiInputHandler(port_name, args.config))

    log.info("Entering main loop. Press Control-C to exit.")
    try:
        # just wait for keyboard interrupt in main thread
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('')
    finally:
        midiin.close_port()
        del midiin


if __name__ == '__main__':
    sys.exit(main() or 0)
