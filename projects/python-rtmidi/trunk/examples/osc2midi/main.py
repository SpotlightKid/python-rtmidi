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


# These patterns will work with the TouchOSC Midi16 control layout
patterns = (
    # general
    (r'/(?P<page>\w+)$', '', 'page_change'),

    # page 1
    (r'/1/fader1$', 'f', 'sendcc', dict(cc=MODULATION_WHEEL, channel=1)),
    (r'/1/fader2$', 'f', 'sendcc', dict(cc=DATA_ENTRY, channel=1)),
    (r'/1/fader3$', 'f', 'sendcc', dict(cc=13, channel=1)),
    (r'/1/fader4$', 'f', 'sendcc', dict(cc=CHANNEL_VOLUME, channel=1)),

    (r'/1/toggle1$', 'f', 'sendcc', dict(cc=SUSTAIN_ONOFF, channel=1)),
    (r'/1/toggle2$', 'f', 'sendcc', dict(cc=PORTAMENTO_ONOFF, channel=1)),
    (r'/1/toggle3$', 'f', 'sendcc', dict(cc=LEGATO_ONOFF, channel=1)),

    (r'/1/push(?P<i:note>\d+)$', 'f', 'noteonoff', dict(transpose=60, channel=1)),

    (r'/1/xy$', 'ff', 'sendtwocc',
        dict(cc1=EXPRESSION_CONTROLLER, cc2=PAN, channel=1)),

    # page 2, map control number to MIDI channel
    (r'/2/fader(?P<i:channel>\d+)$', 'f', 'sendcc', dict(cc=CHANNEL_VOLUME)),
    (r'/2/toggle(?P<i:channel>\d+)$', 'f', 'sendcc', dict(cc=SUSTAIN_ONOFF)),

    # page 3, the same, differnt controllers
    (r'/3/fader(?P<i:channel>\d+)$', 'f', 'sendcc', dict(cc=PAN)),
    (r'/3/toggle(?P<i:channel>\d+)$', 'f', 'sendcc', dict(cc=29)),

    ## catch-all pattern that maps page number to MIDI channel
    ## and control number to MIDI controller number, e.g.
    ##
    ##    /1/push64 1.0 --> MIDI CC #64, channel 1, value 127
    ##
    #(r'/(?P<i:channel>\d+)/(fader|push|rotary|toggle)(?P<i:cc>\d+)$', 'f',
    #    'sendcc'),

    #(r'/(?P<i:page>\d+)/multitoggle(?P<i:cc>\d+)/(?P<i:col>\d+)/(?P<i:row>\d+)$',
    #    'f', 'sendcc'),
    #(r'/(?P<i:page>\d+)/xy(?P<i:cc>\d+)$', 'ff', 'sendtwocc')
)


class OSC2MIDIHandler(object):
    def __init__(self, midiout):
        self.midiout = midiout
        self._note_state = [{}] * 16
        self._program = [0] * 16
        #self._velocity = {}

    def sendcc(self, value, cc=0, channel=1, **kwargs):
        self.midiout.send(
            MidiEvent.fromdata(CONTROLLER_CHANGE,
                channel=(channel-1) & 0x7f,
                data=[cc & 0x7f, int(127 * value) & 0x7f]))

    def sendtwocc(self, val1, val2, cc1=0, cc2=32, channel=1, **kwargs):
        self.midiout.send(
            MidiEvent.fromdata(CONTROLLER_CHANGE,
                channel=(channel-1) & 0x7f,
                data=[cc1 & 0x7f, int(127 * val1) & 0x7f]))
        self.midiout.send(
            MidiEvent.fromdata(CONTROLLER_CHANGE,
                channel=(channel-1) & 0x7f,
                data=[cc2 & 0x7f, int(127 * val2) & 0x7f]))

    def page_change(self, page=None):
        log.info("Page %s selected.", page)

    def noteonoff(self, val, note=60, channel=1, velocity=None,
            transpose=0,**kwargs):
        note += transpose

        if val:
            velocity = velocity or 100
            self.midiout.send(
                MidiEvent.fromdata(NOTE_ON,
                    channel=(channel-1) & 0x7f,
                    data=[note & 0x7f, velocity & 0x7f]))
            self._note_state[channel][note] = velocity
        else:
            if velocity is None:
                try:
                    velocity = self._note_state[channel][note]
                    if velocity is None:
                        raise ValueError
                except KeyError, ValueError:
                    velocity = 0

            self.midiout.send(
                MidiEvent.fromdata(NOTE_OFF,
                    channel=(channel-1) & 0x7f,
                    data=[note & 0x7f, velocity & 0x7f]))
            self._note_state[channel][note] = None

    """
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
            if msgtype == 'on':
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
    """


class OSC2MIDIServer(liblo.ServerThread):
    def __init__(self, midiout, port=5555):
        super(OSC2MIDIServer, self).__init__(port)
        log.info("Listening on URL: " + self.get_url())
        osc2midi = OSC2MIDIHandler(midiout)
        dispatcher = OSCDispatcher(patterns, search_ns=osc2midi, cache_size=512)
        log.info("Registering OSC method handler.")
        self.add_method(None, None, dispatcher.dispatch)


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

    server = OSC2MIDIServer(midiout, args.oscport)

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
