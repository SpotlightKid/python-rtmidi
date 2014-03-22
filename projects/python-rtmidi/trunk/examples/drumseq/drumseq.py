#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# drumseq.py
#
# MIDI Drum sequencer prototype, by Michiel Overtoom, motoom@xs4all.nl
#
"""Play drum pattern from file to MIDI out."""

from __future__ import print_function

import threading
from time import sleep, time as timenow

import rtmidi
from rtmidi.midiutil import open_midiport
from rtmidi.midiconstants import *

FUNKYDRUMMER = """
    #  ,...,...,...,...
    42 xxxxx-x-xxxxx-xx Closed Hi-hat
    46 -----x-x-----x-- Open Hi-hat
    38 ----x--m-m-mx--m Snare
    36 x-x-------x--x-- Bassdrum
"""


class Sequencer(threading.Thread):
    """MIDI output and scheduling thread."""

    def __init__(self, midiout, bpm, pattern, channel=9):
        super(Sequencer, self).__init__()
        self.midiout = midiout
        self.bpm = max(20, min(bpm, 400))
        self.interval = 15. / self.bpm
        self.pattern = pattern
        self.channel = channel
        self.start()

    def run(self):
        self.done = False
        self.callcount = 0
        self.pattern.activate_drumkit(channel=self.channel)
        # give MIDI instrument some time to activate drumkit
        sleep(0.3)
        self.started = timenow()

        while not self.done:
            self.worker()
            self.callcount += 1
            # Compensate for drift:
            # calculate the time when the worker should be called again.
            nexttime = self.started + self.callcount * self.interval
            timetowait = nexttime - timenow()
            sleep(timetowait)

        midiout.send_message([CONTROL_CHANGE | self.channel, ALL_SOUND_OFF, 0])

    def worker(self):
        """Variable time worker function.

        i.e., output notes, emtpy queues, etc.

        """
        self.pattern.playstep(self.midiout, self.channel)


class Drumpattern(object):
    """Container and iterator for a multi-track step sequence."""

    velocities = {
        "-": 0,   # off
        ".": 32,  # low
        "s": 60,  # soft
        "m": 100, # medium
        "x": 120, # hard
        }

    def __init__(self, pattern, kit=0):
        self.instruments = []
        self.kit = kit

        pattern = (line.strip() for line in pattern.splitlines())
        pattern = (line for line in pattern if line and line[0] != '#')

        for line in pattern:
            parts = line.split(" ", 2)

            if len(parts) == 3:
                patch, strokes, description = parts
                patch = int(patch)
                self.instruments.append((patch, strokes))
                self.steps = len(strokes)

        self.step = 0

    def reset(self):
        self.step = 0

    def playstep(self, midiout, channel=9):
        for ins in self.instruments:
            patch, strokes = ins
            char = strokes[self.step]
            velocity = Drumpattern.velocities.get(char, 64)

            if velocity:
                note_on = [NOTE_ON | channel, patch, velocity]
                midiout.send_message(note_on)

        self.step += 1

        if self.step >= self.steps:
            self.step = 0

    def activate_drumkit(self, kit=None, volume=127, channel=9):
        if kit is not None:
            self.kit = kit

        if isinstance(self.kit, (list, tuple)):
            msb, lsb, pc = self.kit
        elif self.kit is not None:
            msb = lsb = None
            pc = self.kit

        cc = CONTROL_CHANGE | channel
        if msb is not None:
            midiout.send_message([cc, BANK_SELECT_MSB, msb & 0x7F])

        if lsb is not None:
            midiout.send_message([cc, BANK_SELECT_LSB, lsb & 0x7F])

        if pc is not None:
            midiout.send_message([PROGRAM_CHANGE | channel, pc & 0x7F])

        midiout.send_message([cc, CHANNEL_VOLUME, volume & 0x7F])


if __name__ == "__main__":
    import sys
    import argparse

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('-b', '--bpm', type=int, default=100,
        help="Beats per minute (BPM) (default: %(default)s)")
    ap.add_argument('-c', '--channel', type=int, default=10, metavar='CH',
        help="MIDI channel (default: %(default)s)")
    ap.add_argument('-p', '--port',
        help="MIDI output port number (default: ask)")
    ap.add_argument('-k', '--kit', type=int, default=0, metavar='KIT',
        help="Drum kit MIDI program number (default: %(default)s)")
    ap.add_argument('--bank-msb', type=int, metavar='MSB',
        help="MIDI bank select MSB (CC#00) number (default: none)")
    ap.add_argument('--bank-lsb', type=int, metavar='MSB',
        help="MIDI bank select LSB (CC#32) number (default: none)")
    ap.add_argument('pattern', nargs='?', type=open,
        help="Drum pattern file (default: use built-in pattern)")

    args = ap.parse_args(sys.argv[1:])

    if args.pattern:
        pattern = args.pattern.read()
    else:
        pattern = FUNKYDRUMMER

    pattern = Drumpattern(pattern, kit=(args.bank_msb, args.bank_lsb, args.kit))

    try:
        midiout, port_name = open_midiport(args.port, "output",
            client_name="drumseq", port_name="MIDI Out")
    except (EOFError, KeyboardInterrupt):
        sys.exit()

    seq = Sequencer(midiout, args.bpm, pattern, args.channel-1)

    print("Playing drum loop at %i BPM, press Control-C to quit." % seq.bpm)

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print('')
    finally:
        seq.done = True # And kill it.
        seq.join()
        del midiout
        print("Done")
