#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# sendsysex.py
#
"""Send all system exclusive files given on the command line or found in the 
current directory to the chosen MIDI ouput after confirmation.

"""

import argparse
import os
import sys
import time

from os.path import basename

import rtmidi


def info(msg, *args):
    sys.stderr.write(msg.format(*args) + '\n')

def main(args=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(dest='sysexfiles', nargs="*", metavar="SYSEX",
        help='MIDI system exclusive file(s) to send')
    parser.add_argument('-l',  '--list-ports', action="store_true",
        help='list available MIDI output ports')
    parser.add_argument('-p',  '--port', dest='port', default=0, type=int,
        help='MIDI output port number (default: 0)')
    parser.add_argument('-d',  '--delay', default="50", metavar="MS", type=int,
        help='delay between sending each Sysex message in milliseconds '
        '(default: 50)')
    parser.add_argument('-y',  '--no-prompt', dest='prompt', 
        action="store_false", help='do not ask for confirmation before sending')
    parser.add_argument('-v',  '--verbose', action="store_true",
        help='verbose output')

    args = parser.parse_args()

    try:
        midiout = rtmidi.MidiOut()

        ports = midiout.get_ports()

        if ports:
            if args.list_ports:
                for i, port in enumerate(ports):
                    info("{}: {}", i, port)
                
                return 0

            if args.port < len(ports):
                midiout.open_port(args.port)
                port_name = ports[args.port]
            else:
                info("MIDI port number out of range.")
                info("Use '-l' to list MIDI ports.")
                return 2
        else:
            info("No MIDI output ports found.")
            return 1

        if not args.sysexfiles:
            args.sysexfiles = sorted([fn for fn in os.listdir(os.curdir)
                                      if fn.lower().endswith('.syx')])

        
        if not args.sysexfiles:
            info("No sysex (.syx) files found in current directory.")

        for fn in args.sysexfiles:
            syx = open(fn, 'rb').read()

            if syx.startswith('\xF0'):
                try:
                    if args.prompt:
                        yn = raw_input(
                            "Send '{}' to {} (y/N)? ".format(basename(fn), port_name))
                except (EOFError, KeyboardInterrupt):
                    print()
                    break

                if not args.prompt or yn.lower() in ('y', 'yes'):
                    sox = 0
                    i = 0
                    while sox >= 0:
                        sox = syx.find('\xF0', sox)
                        
                        if sox >= 0:
                            eox = syx.find('\xF7', sox)

                            if eox >= 0:
                                msg = [ord(c) for c in syx[sox:eox+1]]
                                if args.verbose:
                                    info("Sending '{}' message #{:03}...",
                                        basename(fn), i)
                                midiout.send_message(msg)
                                i += 1
                                time.sleep(0.001 * args.delay)
                            else:
                                break

                            sox = eox + 1
            elif args.verbose:
                info("File '{}' not recognized as sysex message.", basename(fn))

    finally:
        midiout.close_port()
        del midiout

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)
