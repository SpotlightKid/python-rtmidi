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
from rtmidi.midiconstants import (CONTROL_CHANGE, MODULATION_WHEEL,
                                  NOTE_OFF, NOTE_ON, RESET_ALL_CONTROLLERS)


CC_SET_WAVETABLE = 70


class Midi(object):
    """Encapsulate MIDI output."""

    def __init__(self, port):
        self.midi = rtmidi.MidiOut()
        self.midi.open_port(port)

    def play_stepping(self, note, cc, dur=0.2, step=1, vel=64, rvel=None, ch=0):
        """Play given note and step through ctrl values over time."""
        # note on
        note &= 0x7F
        ch &= 0x0F
        self.midi.send_message([CONTROL_CHANGE | ch, cc, 0])
        time.sleep(0.1)
        self.midi.send_message([NOTE_ON | ch, note, vel & 0x7F])

        # step through modulation controller values
        for i in range(0, 128, step):
            self.midi.send_message([CONTROL_CHANGE | ch, cc, i])
            time.sleep(dur)

        # note off
        self.midi.send_message(
            [NOTE_OFF | ch, note, (vel if rvel is None else rvel) & 0x7F])

    def reset_controllers(self, ch=0):
        """Reset controllers on given channel."""
        self.midi.send_message(
            [CONTROL_CHANGE | (ch & 0xF), RESET_ALL_CONTROLLERS, 0])

    def set_wavetable(self, wt, ch=0):
        """Set wavetable for current sound to given number."""
        self.midi.send_message(
            [CONTROL_CHANGE | (ch & 0xF), CC_SET_WAVETABLE, wt & 0x7F])

    def close(self):
        """Close MIDI outpurt."""
        self.midi.close_port()
        del self.midi


if __name__ == '__main__':
    import argparse

    argparser = argparse.ArgumentParser()
    aadd = argparser.add_argument
    aadd('-c', '--channel', type=int, default=1,
         help="MIDI channel (1-based, default: %(default)s)")
    aadd('-C', '--controller', type=int, default=MODULATION_WHEEL,
         help="MIDI controller number (default: %(default)s)")
    aadd('-p', '--port', type=int, default=0,
         help="MIDI output port (default: %(default)s)")
    aadd('-l', '--length', type=float, default=0.3,
         help="Length (in sec.) of each wave (default: %(default)s)")
    aadd('-n', '--note', type=int, default=60,
         help="MIDI note number to play (default: %(default)s)")
    aadd('-w', '--wavetable', type=int,
         help="Send CC #70 to set wavetable number (1-based, default: none)")

    args = argparser.parse_args()

    m = Midi(args.port)
    ch = max(0, args.channel - 1)

    if args.wavetable:
        m.set_wavetable(args.wavetable - 1, ch=args.channel - 1)
        time.sleep(0.1)

    try:
        m.reset_controllers(ch)
        m.play_stepping(args.note, args.controller, dur=args.length, step=2, ch=ch)
    finally:
        m.reset_controllers(ch)
        m.close()
