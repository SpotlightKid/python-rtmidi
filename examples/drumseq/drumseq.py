#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# drumseq.py
#
# MIDI Drum sequencer prototype, by Michiel Overtoom, motoom@xs4all.nl
#
"""Play drum pattern from file to MIDI out."""

from __future__ import print_function

import argparse
import sys
import threading

from random import gauss
from time import sleep, time as timenow

import rtmidi
from rtmidi.midiutil import open_midioutput
from rtmidi.midiconstants import (ALL_SOUND_OFF, BANK_SELECT_LSB,
                                  BANK_SELECT_MSB, CHANNEL_VOLUME,
                                  CONTROL_CHANGE, NOTE_ON, PROGRAM_CHANGE)


FUNKYDRUMMER = """
    #  1...|...|...|...
    36 x.x.......x..x.. Bassdrum
    38 ....x..m.m.mx..m Snare
    42 xxxxx.x.xxxxx.xx Closed Hi-hat
    46 .....x.x.....x.. Open Hi-hat
"""


class Sequencer(threading.Thread):
    """MIDI output and scheduling thread."""

    def __init__(self, midiout, pattern, bpm, channel=9, volume=127):
        super(Sequencer, self).__init__()
        self.midiout = midiout
        self.bpm = max(20, min(bpm, 400))
        self.interval = 15. / self.bpm
        self.pattern = pattern
        self.channel = channel
        self.volume = volume
        self.start()

    def run(self):
        self.done = False
        self.callcount = 0
        self.activate_drumkit(self.pattern.kit)
        cc = CONTROL_CHANGE | self.channel
        self.midiout.send_message([cc, CHANNEL_VOLUME, self.volume & 0x7F])

        # give MIDI instrument some time to activate drumkit
        sleep(0.3)
        self.started = timenow()

        while not self.done:
            self.worker()
            self.callcount += 1
            # Compensate for drift:
            # calculate the time when the worker should be called again.
            nexttime = self.started + self.callcount * self.interval
            timetowait = max(0, nexttime - timenow())
            if timetowait:
                sleep(timetowait)
            else:
                print("Oops!")

        self.midiout.send_message([cc, ALL_SOUND_OFF, 0])

    def worker(self):
        """Variable time worker function.

        i.e., output notes, emtpy queues, etc.

        """
        self.pattern.playstep(self.midiout, self.channel)

    def activate_drumkit(self, kit):
        if isinstance(kit, (list, tuple)):
            msb, lsb, pc = kit
        elif kit is not None:
            msb = lsb = None
            pc = kit

        cc = CONTROL_CHANGE | self.channel
        if msb is not None:
            self.midiout.send_message([cc, BANK_SELECT_MSB, msb & 0x7F])

        if lsb is not None:
            self.midiout.send_message([cc, BANK_SELECT_LSB, lsb & 0x7F])

        if kit is not None and pc is not None:
            self.midiout.send_message([PROGRAM_CHANGE | self.channel, pc & 0x7F])


class Drumpattern(object):
    """Container and iterator for a multi-track step sequence."""

    velocities = {
        "-": None,  # continue note
        ".": 0,     # off
        "+": 10,    # ghost
        "s": 60,    # soft
        "m": 100,   # medium
        "x": 120,   # hard
    }

    def __init__(self, pattern, kit=0, humanize=0):
        self.instruments = []
        self.kit = kit
        self.humanize = humanize

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
        self._notes = {}

    def reset(self):
        self.step = 0

    def playstep(self, midiout, channel=9):
        for note, strokes in self.instruments:
            char = strokes[self.step]
            velocity = self.velocities.get(char)

            if velocity is not None:
                if self._notes.get(note):
                    midiout.send_message([NOTE_ON | channel, note, 0])
                    self._notes[note] = 0
                if velocity > 0:
                    if self.humanize:
                        velocity += int(round(gauss(0, velocity * self.humanize)))

                    midiout.send_message([NOTE_ON | channel, note, max(1, velocity)])
                    self._notes[note] = velocity

        self.step += 1

        if self.step >= self.steps:
            self.step = 0


def main(args=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    aadd = ap.add_argument
    aadd('-b', '--bpm', type=float, default=100,
         help="Beats per minute (BPM) (default: %(default)s)")
    aadd('-c', '--channel', type=int, default=10, metavar='CH',
         help="MIDI channel (default: %(default)s)")
    aadd('-p', '--port',
         help="MIDI output port number (default: ask)")
    aadd('-k', '--kit', type=int, metavar='KIT',
         help="Drum kit MIDI program number (default: none)")
    aadd('--bank-msb', type=int, metavar='MSB',
         help="MIDI bank select MSB (CC#00) number (default: none)")
    aadd('--bank-lsb', type=int, metavar='MSB',
         help="MIDI bank select LSB (CC#32) number (default: none)")
    aadd('-H', '--humanize', type=float, default=0.0, metavar='VAL',
         help="Random velocity variation (float, default: 0, try ~0.03)")
    aadd('pattern', nargs='?', type=argparse.FileType(),
         help="Drum pattern file (default: use built-in pattern)")

    args = ap.parse_args(args)

    if args.pattern:
        pattern = args.pattern.read()
    else:
        pattern = FUNKYDRUMMER

    kit = (args.bank_msb, args.bank_lsb, args.kit)
    pattern = Drumpattern(pattern, kit=kit, humanize=args.humanize)

    try:
        midiout, port_name = open_midioutput(
            args.port,
            api=rtmidi.API_UNIX_JACK,
            client_name="drumseq",
            port_name="MIDI Out")
    except (EOFError, KeyboardInterrupt):
        return

    seq = Sequencer(midiout, pattern, args.bpm, args.channel - 1)

    print("Playing drum loop at %.1f BPM, press Control-C to quit." % seq.bpm)

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print('')
    finally:
        seq.done = True  # And kill it.
        seq.join()
        midiout.close_port()
        del midiout
        print("Done")


if __name__ == "__main__":
    sys.exit(main() or 0)
