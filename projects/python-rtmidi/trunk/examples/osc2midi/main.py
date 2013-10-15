#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# osc2midi/main.py
#
"""Simple uni-directional OSC to MIDI gateway."""

__program__ = 'oscmidi.py'
__version__ = '1.2 ($Rev$)'
__author__  = 'Christopher Arndt'
__date__    = '$Date$'

import argparse
import logging
import re
import sys
import time

import rtmidi
import liblo
import yaml

# package-specific modules
from rtmidi import midiconstants
from rtmidi.midiconstants import *
from rtmidi.midiutil import open_midiport

from .midiio import MidiOutputProc, MidiOutputThread
from .midievents import *
from .oscdispatcher import OSCDispatcher

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


class OSC2MIDIHandler(object):
    def __init__(self, midiout):
        self.midiout = midiout
        self._note_state = [{} for i in range(16)]
        self._controllers = [{} for i in range(16)]
        self._program = [0] * 16
        self._bank = [0] * 16
        self._base_channel = 0

    def sendcc(self, value, cc=0, channel=None, invert=False, **kwargs):
        value = int(127 * value) & 0x7f

        if channel is None:
            channel = self._base_channel
        else:
            channel = (channel-1) & 0xf

        if invert:
            value = 127 - value

        self._controllers[channel][cc] = value

        self.midiout.send(
            MidiEvent.fromdata(CONTROLLER_CHANGE,
                channel=channel, data=[cc & 0x7f, value]))

    def sendtwocc(self, val1, val2, cc1=0, cc2=32, channel=None, invert=False,
            **kwargs):
        val1 = int(127 * val1) & 0x7f
        val2 = int(127 * val2) & 0x7f

        if channel is None:
            channel = self._base_channel
        else:
            channel = (channel-1) & 0xf

        if invert:
            val1 = 127 - val1
            val2 = 127 - val2

        self._controllers[channel][cc1] = val1
        self._controllers[channel][cc2] = val2

        self.midiout.send(
            MidiEvent.fromdata(CONTROLLER_CHANGE,
                channel=channel, data=[cc1 & 0x7f, val1]))
        self.midiout.send(
            MidiEvent.fromdata(CONTROLLER_CHANGE,
                channel=channel, data=[cc2 & 0x7f, val2]))

    def page_change(self, page=None):
        log.info("Page %s selected.", page)

    def noteonoff(self, val, note=60, channel=None, velocity=None,
            transpose=0,**kwargs):
        note += transpose

        if channel is None:
            channel = self._base_channel
        else:
            channel = (channel-1) & 0xf

        if val:
            velocity = velocity or 100
            self.midiout.send(
                MidiEvent.fromdata(NOTE_ON,
                    channel=channel,
                    data=[note & 0x7f, velocity & 0x7f]))
            self._note_state[channel][note] = velocity
        else:
            if velocity is None:
                try:
                    velocity = self._note_state[channel][note]
                    if velocity is None:
                        raise ValueError
                except (KeyError, ValueError):
                    velocity = 0

            self.midiout.send(
                MidiEvent.fromdata(NOTE_OFF,
                    channel=channel, data=[note & 0x7f, velocity & 0x7f]))
            self._note_state[channel][note] = None

    def solo_channel(self, value, channel=None, invert=False, **kwargs):
        value = int(127 * value) & 0x7f

        if channel is None:
            channel = self._base_channel
        else:
            channel = (channel-1) & 0xf

        if invert:
            value = 127 - value

        for ch in range(16):
            if ch == channel:
                continue

            val = (0 if value >= 64
                else self._controllers[ch].get(CHANNEL_VOLUME, 127))

            self.midiout.send(
                MidiEvent.fromdata(CONTROLLER_CHANGE,
                    channel=ch, data=[CHANNEL_VOLUME, val]))

    def sendpc(self, value, program=0, bank=None, bank_msb=None,
            bank_lsb=None, channel=None, **kwargs):
        if not value:
            return

        if channel is None:
            channel = self._base_channel
        else:
            channel = (channel-1) & 0xf

        if bank is not None:
            bank_msb = (int(bank) >> 7) & 0x7f
            bank_lsb = int(bank) & 0x7f
        
        if bank_msb is not None:
            self.midiout.send(
                MidiEvent.fromdata(CONTROLLER_CHANGE,
                    channel=channel, data=[BANK_SELECT, bank_msb]))

        if bank_lsb is not None:
            self.midiout.send(
                MidiEvent.fromdata(CONTROLLER_CHANGE,
                    channel=channel, data=[BANK_SELECT_LSB, bank_msb]))

        if (bank_msb, bank_lsb) != (None, None):
            self._bank[channel] = (bank_lsb or 0) * 128 + (bank_msb or 0)
        
        self._program[channel] = program
        self.midiout.send(
            MidiEvent.fromdata(PROGRAM_CHANGE,
                channel=channel, data=[program]))

    def sendpcrel(self, value, channel=None, **kwargs):
        if channel is None:
            channel = self._base_channel
        else:
            channel = (channel-1) & 0xf
        
        if value > 0.5:
            self._program[channel] = min(127, self._program[channel] + 1)
        else:
            self._program[channel] = max(0, self._program[channel] - 1)

        self.midiout.send(
            MidiEvent.fromdata(PROGRAM_CHANGE,
                channel=channel, data=[self._program[channel]]))

    def sendpb(self, value, channel=None, **kwargs):
        if channel is None:
            channel = self._base_channel
        else:
            channel = (channel-1) & 0xf

        pb = int(2**14 * value)
        self.midiout.send(
            MidiEvent.fromdata(PITCH_BEND,
                channel=channel,
                data=[pb & 0x7f, (pb >> 7) & 0x7f]))

    def sendmp(self, value, channel=None, **kwargs):
        value = int(127 * value) & 0x7f

        if channel is None:
            channel = self._base_channel
        else:
            channel = (channel-1) & 0xf

        self.midiout.send(
            MidiEvent.fromdata(CHANNEL_PRESSURE,
                channel=channel, data=[value]))

    def sendpp(self, value, note=0, channel=None, transpose=0, **kwargs):
        value = int(127 * value) & 0x7f

        if channel is None:
            channel = self._base_channel
        else:
            channel = (channel-1) & 0xf

        self.midiout.send(
            MidiEvent.fromdata(POLYPHONIC_PRESSURE,
                channel=channel, data=[(note + transpose) & 0x7f, value]))


class OSC2MIDIServer(liblo.ServerThread):
    def __init__(self, midiout, dispatcher, port=5555):
        super(OSC2MIDIServer, self).__init__(port)
        log.info("Listening on URL: " + self.get_url())
        log.info("Registering OSC method handler.")
        self.add_method(None, None, dispatcher.dispatch)

def _resolve_constants(params):
    for name, value in params.items():
        if isinstance(value, str) and re.match('[A-Z][_A-Z0-9]*$', value):
            params[name] = getattr(midiconstants, value, value)
    return params

def load_patch(filename):
    with open(filename) as patch:
        data = yaml.load(patch)

    patterns = []
    for pattern in data:
        try:
            if isinstance(pattern, dict) and 'params' in pattern:
                pattern['params'] = _resolve_constants(pattern['params'])
            elif len(pattern) == 4:
                pattern[3] = _resolve_constants(pattern[3])
        except TypeError:
            raise IOError("Invalid pattern. %r" % pattern)

        patterns.append(pattern)

    return patterns

def main(args=None):
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument('-p', '--port', dest="midiport",
        help="MIDI output port (default: ask to open virtual MIDI port).")
    argparser.add_argument('-P', '--oscport', default=5555, type=int,
        help="Port the OSC server listens on (default: %(default)s).")
    argparser.add_argument('-v', '--verbose', action="store_true",
        help="Print debugging info to standard output.")
    argparser.add_argument('patch',
        help="YAML file with OSC address mappings.")
    argparser.add_argument('--version', action='version', version=__version__)

    args = argparser.parse_args(args if args is not None else sys.argv)

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    if sys.platform == 'darwin':
        midiout = MidiOutputThread(name=__program__, port=args.midiport)
    else:
        midiout = MidiOutputProc(name=__program__, port=args.midiport)

    osc2midi = OSC2MIDIHandler(midiout)

    try:
        patterns = load_patch(args.patch)
    except (IOError, OSError) as exc:
        log.error("Could not load patch: %s", exc)
        return 1

    dispatcher = OSCDispatcher(patterns, search_ns=osc2midi, cache_size=512)
    server = OSC2MIDIServer(midiout, dispatcher, args.oscport)

    print("Entering main loop. Press Control-C to exit.")
    try:
        midiout.start()
        server.start()

        while True:
            time.sleep(1)
    except (EOFError, IOError, KeyboardInterrupt):
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
