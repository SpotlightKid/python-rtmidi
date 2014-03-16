#!/usr/bin/env python
#
# midi2command.py
#
"""Execute external commands when specific MIDI messages are received.

Example configuration (in YAML syntax)::

    - name: My Backingtracks
      description: Play audio file with filename matching <data1>-playback.wav
        when program change on channel 16 is received
      status: programchange
      channel: 16
      command: aplay %(data1)03i-playback.wav
    - name: My Lead Sheets
      description: Open PDF with filename matching <data2>-sheet.pdf
        when control change 14 on channel 16 is received
      status: controllerchange
      channel: 16
      data: 14 g
      command: evince %(data2)03i-sheet.pdf

"""

import argparse
import logging
import shlex
import subprocess
import sys
import time

from os.path import exists

import yaml

import rtmidi
from rtmidi.midiutil import open_midiport
from rtmidi.midiconstants import *


log = logging.getLogger('midi2command')
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
    def __init__(self, name='', description='', status=0xB0, channel=None,
            data=None, command=None):
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
        log.debug("[%s] @%0.6f %r", self.port, self._wallclock, event)

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

        # Look for matching command definitions
        # XXX: use memoize cache here
        if status in self.commands:
            for cmd in self.commands[status]:
                if channel is not None and cmd.channel != channel:
                    continue

                found = False
                if num_bytes == 1 or cmd.data is None:
                    found = True
                elif isinstance(cmd.data, int) and cmd.data == data1:
                    found = True
                elif (isinstance(cmd.data, (list, tuple)) and
                        cmd.data[0] == data1 and cmd.data[1] == data2):
                    found = True

                if found:
                    cmdline = cmd.command % dict(
                        channel=channel,
                        data1=data1,
                        data2=data2,
                        status=status)
                    self.do_command(cmdline)
            else:
                return

    def do_command(self, cmdline):
        log.info("Calling external command: %s", cmdline)
        try:
            args = shlex.split(cmdline)
            subprocess.Popen(args)
        except:
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
                    except:
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
    parser.add_argument('-p',  '--port', dest='port',
        help='MIDI input port name or number (default: open virtual input)')
    parser.add_argument('-v',  '--verbose', action="store_true",
        help='verbose output')
    parser.add_argument(dest='config', metavar="CONFIG",
        help='Configuration file in YAML syntax.')

    args = parser.parse_args(args if args is not None else sys.argv[1:])

    logging.basicConfig(format="%(name)s: %(levelname)s - %(message)s",
        level=logging.DEBUG if args.verbose else logging.WARNING)

    try:
        midiin, port_name = open_midiport(args.port, use_virtual=True)
    except (EOFError, KeyboardInterrupt):
        sys.exit()

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
    sys.exit(main(sys.argv[1:]) or 0)
