#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# wavetablemodstep.py
#
"""Play a note and step through MIDI Control Change #1 (modulation) values.

Optionally allows to send a Control Change #70 first, to set the wavetable
of the current sound on a Waldorf Microwave II/XT(k) synthesizer.

I use this with a Microwave sound program where the CC #1 is mapped to
wavetable position of oscillator 1. This script then allows me to listen to
all the waves in a selected wavetable in succession.

"""

import time
import rtmidi

from rtmidi.midiconstants import *

CC_SET_WAVETABLE = 70


class Midi(object):
    """Encapsulate MIDI output."""

    def __init__(self, port):
        self.midi = rtmidi.MidiOut()
        self.midi.open_port(port)

    def play_stepping(self, note, dur=0.2, step=1, vel=64, rvel=None, ch=0):
        """Play given note and step through cc #1 values over time."""
        # note on
        self.midi.send_message([NOTE_ON | (ch & 0xF), note & 0x7F, vel & 0x7F])

        # step through modulation controller values
        for i in range(0, 128, step):
            self.midi.send_message([CONTROLLER_CHANGE | (ch & 0xF),
                MODULATION_WHEEL, i])
            time.sleep(dur)

        # note off
        self.midi.send_message([NOTE_OFF | (ch & 0xF), note & 0x7F,
            (rvel if rvel is not None else vel) & 0x7F])

    def reset_controllers(self, ch=0):
        """Reset controllers on given channel."""
        self.midi.send_message([CONTROLLER_CHANGE | (ch & 0xF),
            RESET_ALL_CONTROLLERS, 0])

    def set_wavetable(self, wt, ch=0):
        """Set wavetable for current sound to given number."""
        self.midi.send_message([CONTROLLER_CHANGE | (ch & 0xF),
            CC_SET_WAVETABLE, wt & 0x7F])

    def close(self):
        """Close MIDI outpurt."""
        self.midi.close_port()
        del self.midi


if __name__ == '__main__':
    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument('-c', '--channel', type=int, default=1,
        help="MIDI channel (1-based, default: %(default)s)")
    argparser.add_argument('-p', '--port', type=int, default=0,
        help="MIDI output port (default: %(default)s)")
    argparser.add_argument('-l', '--length', type=float, default=0.3,
        help="Length (in sec.) of each wave (default: %(default)s)")
    argparser.add_argument('-n', '--note', type=int, default=60,
        help="MIDI note number to play (default: %(default)s)")
    argparser.add_argument('-w', '--wavetable', type=int,
        help="Send CC #70 to set wavetable number (1-based, default: none)")

    args = argparser.parse_args()

    m = Midi(args.port)

    if args.wavetable:
        m.set_wavetable(args.wavetable-1, ch=args.channel-1)
        time.sleep(0.1)

    try:
        m.reset_controllers(ch=args.channel-1)
        m.play_stepping(args.note, dur=args.length, step=2, ch=args.channel-1)
    finally:
        m.reset_controllers(ch=args.channel-1)
        m.close()
