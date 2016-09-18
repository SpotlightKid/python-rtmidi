#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# sendsysex.py
#
"""Send all system exclusive files given on the command line.

The paths given on the command line can also contain directories and all files
with a *.syx extension in them will be sent (in alphabetical order).

All consecutive sysex messages in each file will be sent to the chosen MIDI
output, after confirmation (which can be turned off).

"""

import argparse
import logging
import os
import sys
import time

from os.path import basename, exists, isdir, join

import rtmidi

try:
    raw_input
except NameError:
    # Python 3
    raw_input = input


__program__ = 'sendsysex.py'
__version__ = '1.1'
__author__ = 'Christopher Arndt'
__date__ = '$Date$'

log = logging.getLogger("sendsysex")

SYSTEM_EXCLUSIVE = b'\xF0'
END_OF_EXCLUSIVE = b'\xF7'


def send_sysex_file(filename, midiout, portname, prompt=True, delay=50):
    """Send contents of sysex file to given MIDI output.

    Reads file given by filename and sends all consecutive sysex messages found
    in it to given midiout after prompt.

    """
    bn = basename(filename)

    with open(filename, 'rb') as sysex_file:
        data = sysex_file.read()

        if data.startswith(SYSTEM_EXCLUSIVE):
            try:
                if prompt:
                    yn = raw_input("Send '%s' to %s (y/N)? " % (bn, portname))
            except (EOFError, KeyboardInterrupt):
                print('')
                raise StopIteration

            if not prompt or yn.lower() in ('y', 'yes'):
                sox = 0
                i = 0

                while sox >= 0:
                    sox = data.find(SYSTEM_EXCLUSIVE, sox)

                    if sox >= 0:
                        eox = data.find(END_OF_EXCLUSIVE, sox)

                        if eox >= 0:
                            sysex_msg = data[sox:eox + 1]
                            # Python 2: convert data into list of integers
                            if isinstance(sysex_msg, str):
                                sysex_msg = [ord(c) for c in sysex_msg]

                            log.info("Sending '%s' message #%03i...", bn, i)
                            midiout.send_message(sysex_msg)
                            time.sleep(0.001 * delay)

                            i += 1
                        else:
                            break

                        sox = eox + 1
        else:
            log.warning("File '%s' does not start with a sysex message.", bn)


def main(args=None):
    """Main program function.

    Parses command line (parsed via ``args`` or from ``sys.argv``), detects
    and optionally lists MIDI output ports, opens given MIDI output port,
    assembles list of sysex files and calls ``send_sysex_file`` on each of
    them.

    """
    parser = argparse.ArgumentParser(description=__doc__)
    padd = parser.add_argument
    padd(dest='sysexfiles', nargs="*", metavar="SYSEX",
         help='MIDI system exclusive files or directories to send.')
    padd('-l', '--list-ports', action="store_true",
         help='list available MIDI output ports')
    padd('-p', '--port', dest='port', default=0, type=int,
         help='MIDI output port number (default: %(default)s)')
    padd('-d', '--delay', default="50", metavar="MS", type=int,
         help='delay between sending each Sysex message in milliseconds '
         '(default: %(default)s)')
    padd('-y', '--no-prompt', dest='prompt', action="store_false",
         help='do not ask for confirmation before sending')
    padd('-v', '--verbose', action="store_true", help='verbose output')

    args = parser.parse_args(args if args is not None else sys.argv[1:])

    logging.basicConfig(format="%(name)s: %(levelname)s - %(message)s",
                        level=logging.DEBUG if args.verbose else logging.INFO)

    try:
        midiout = rtmidi.MidiOut()

        ports = midiout.get_ports()

        if ports:
            if args.list_ports:
                for i, port in enumerate(ports):
                    print("%i: %s" % (i, port))

                return 0

            if args.port < len(ports):
                midiout.open_port(args.port)
                portname = midiout.get_port_name(args.port)
            else:
                log.error("MIDI port number out of range.")
                log.error("Use '-l' option to list MIDI ports.")
                return 2
        else:
            log.error("No MIDI output ports found.")
            return 1

        files = []
        for path in args.sysexfiles or [os.curdir]:
            if isdir(path):
                files.extend(sorted([join(path, fn) for fn in os.listdir(path)
                                     if fn.lower().endswith('.syx')]))
            elif exists(path):
                files.append(path)
            else:
                log.error("File '%s' not found.")

        if not files:
            log.warning("No sysex (.syx) files found in given directories or "
                        "working directory.")

        for filename in files:
            try:
                send_sysex_file(
                    filename, midiout, portname, args.prompt, args.delay)
            except StopIteration:
                break
            except Exception as exc:
                log.error("Error while sending file '%s': %s", (filename, exc))
    finally:
        midiout.close_port()
        del midiout

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)
