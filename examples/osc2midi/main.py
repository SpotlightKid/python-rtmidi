#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# osc2midi/main.py
#
"""Simple uni-directional OSC to MIDI gateway."""

__program__ = 'oscmidi.py'
__version__ = '1.1 ($Rev$)'
__author__  = 'Christopher Arndt'
__date__    = '$Date$'
__usage__   = "%(prog)s [-d DEVICE] [-p PORT]"

import logging
import argparse
import sys
import time

import rtmidi
import liblo

# package-specific modules
from rtmidi.midiconstants import *

from .midiio import MidiOutputProc, MidiOutputThread
from .midievents import *

try:
    raw_input
except NameError:
    #Python 3
    raw_input = input

try:
    StandardError
except NameError:
    StandardError = Exception

log = logging.getLogger("osc2midi")



class OSC2MIDI(liblo.ServerThread):
    def __init__(self, midiout, port=5555):
        super(OSC2MIDI, self).__init__(port)
        log.info("Listening on URL: " + self.get_url())
        self.midiout = midiout
        self._note_state = [{}] * 16
        self._program = [0] * 16
        #self._velocity = {}

    @liblo.make_method(None, None)
    def _osc_callback(self, path, args, types, source, data=None):
        log.debug("OSC recv: @%0.6f %s,%s %r", time.time(), path, types, args)
        try:
            parts = path.strip('/').split('/')
            if len(parts) == 3:
                prefix, channel, msgtype = parts
            else:
                prefix, channel, msgtype, data1 = parts
        except (IndexError, ValueError):
            log.debug("Ignoring unrecognized OSC pattern '%s'.", path)
            return 1

        if prefix != 'midi':
            return 1

        try:
            if msgtype == 'cc':
                self.midiout.send(
                    MidiEvent.fromdata(CONTROLLER_CHANGE,
                        channel=int(channel) & 0x7f,
                        data=[int(data1) & 0x7f, args[0] & 0x7f]))

            elif msgtype == 'on':
                channel = int(channel) & 0xf
                note = int(data1) & 0x7f

                if args[0] == 0 and self._note_state[channel].get(note, 0) == 2:
                    self.midiout.send(
                        MidiEvent.fromdata(NOTE_OFF, channel=channel, data=[note, 0]))

                self._note_state[channel][note] = args[0]

            elif msgtype == 'off':
                self.midiout.send(
                    MidiEvent.fromdata(NOTE_OFF,
                        channel=int(channel) & 0xf,
                        data=[int(data1) & 0x7f, args[0] & 0x7f]))
                self._note_state[channel][note] = 0

            elif msgtype == 'pb':
                self.midiout.send(
                    MidiEvent.fromdata(PITCH_BEND,
                        channel=int(channel) & 0xf,
                        data=[args[0] & 0x7f, (args[0] >> 7) & 0x7f]))

            elif msgtype == 'mp':
                self.midiout.send(
                    MidiEvent.fromdata(CHANNEL_PRESSURE,
                        channel=int(channel) & 0xf,
                        data=[args[0] & 0x7f]))

            elif msgtype == 'pc':
                channel = int(channel) & 0xf
                program = args[0] & 0x7f
                self.midiout.send(
                    MidiEvent.fromdata(PROGRAM_CHANGE,
                        channel=channel,
                        data=[program]))
                self._program[channel] = program

            elif msgtype == 'pcrel':
                channel = int(channel) & 0xf

                if int(args[0]) > 0:
                    self._program[channel] = min(127, self._program[channel] + 1)
                else:
                    self._program[channel] = max(0, self._program[channel] - 1)

                self.midiout.send(
                    MidiEvent.fromdata(PROGRAM_CHANGE,
                        channel=channel,
                        data=[self._program[channel]]))

            elif msgtype == 'pp':
                channel = int(channel) & 0xf
                note = int(data1) & 0x7f
                velocity = 127 - (args[0] & 0x7f)

                if self._note_state[channel].get(note, 0) == 1:
                    self.midiout.send(
                        MidiEvent.fromdata(NOTE_ON,
                            channel=channel,
                            data=[note, velocity]))
                    self._note_state[channel][note] = 2
            else:
                return 1
        except StandardError:
            import traceback
            traceback.print_exc()

def select_midiport(midi, default=0):
    type_ = "input" if isinstance(midi, rtmidi.MidiIn) else "output"

    r = raw_input("Do you want to create a virtual MIDI %s port? (y/N) "
        % type_)
    if r.strip().lower() == 'y':
        return None

    ports = midi.get_ports()

    if not ports:
        print("No MIDI %s ports found." % type_)
        return None
    else:
        port = None

        while port is None:
            print("Available MIDI %s ports:\n" % type_)

            for port, name in enumerate(ports):
                print("[%i] %s" % (port, name))
            print('')

            try:
                r = raw_input("Select MIDI %s port [%i]: " % (type_, default))
                port = int(r)
            except (ValueError, TypeError):
                port = default

            if port < 0 or port >= len(ports):
                print("Invalid port number: %i" % port)
                port = None
            else:
                return port


def main(args=None):
    argparser = argparse.ArgumentParser(usage=__usage__, description=__doc__)
    argparser.add_argument('-p', '--port', type=int, dest="midiport",
        help="MIDI output port (default: ask to open virtual MIDI port).")
    argparser.add_argument('-P', '--oscport',
        default=5555, type=int, dest="oscport",
        help="Port the OSC server listens on (default: %(default)s).")
    argparser.add_argument('-v', '--verbose',
        action="store_true", dest="verbose",
        help="Print debugging info to standard output.")
    argparser.add_argument('--version', action='version', version=__version__)

    args = argparser.parse_args(args if args is not None else sys.argv)

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    if args.midiport is None:
        try:
            midiout = rtmidi.MidiOut(name=__program__)
            args.midiport = select_midiport(midiout)
        except (KeyboardInterrupt, EOFError):
            print('')
            return 0
        finally:
            del midiout

    if sys.platform == 'darwin':
        midiout = MidiOutputThread(name=__program__, port=args.midiport)
    else:
        midiout = MidiOutputProc(name=__program__, port=args.midiport)

    server = OSC2MIDI(midiout, args.oscport)

    print("Entering main loop. Press Control-C to exit.")
    try:
        midiout.start()
        server.start()

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
        server.free()
        midiout.stop()
        print('')
    finally:
        print("Exit.")
        del midiout

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)
