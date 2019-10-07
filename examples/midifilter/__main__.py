#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# midifilter/__main__.py
#
"""Simple MIDI filter / processor."""

from __future__ import absolute_import

import argparse
import logging
import sys
import threading
import time

try:
    import Queue as queue
except ImportError:  # Python 3
    import queue

from rtmidi.midiutil import open_midiport

from .filters import MapControllerValue, MonoPressureToCC, Transpose


log = logging.getLogger("midifilter")


class MidiDispatcher(threading.Thread):
    def __init__(self, midiin, midiout, *filters):
        super(MidiDispatcher, self).__init__()
        self.midiin = midiin
        self.midiout = midiout
        self.filters = filters
        self._wallclock = time.time()
        self.queue = queue.Queue()

    def __call__(self, event, data=None):
        message, deltatime = event
        self._wallclock += deltatime
        log.debug("IN: @%0.6f %r", self._wallclock, message)
        self.queue.put((message, self._wallclock))

    def run(self):
        log.debug("Attaching MIDI input callback handler.")
        self.midiin.set_callback(self)

        while True:
            event = self.queue.get()

            if event is None:
                break

            events = [event]

            for filter_ in self.filters:
                events = list(filter_.process(events))

            for event in events:
                log.debug("Out: @%0.6f %r", event[1], event[0])
                self.midiout.send_message(event[0])

    def stop(self):
        self.queue.put(None)


def main(args=None):
    parser = argparse.ArgumentParser(prog='midifilter', description=__doc__)
    padd = parser.add_argument
    padd('-m', '--mpresstocc', action="store_true",
         help='Map mono pressure (channel aftertouch) to CC')
    padd('-r', '--mapccrange', action="store_true",
         help='Map controller value range to min/max value range')
    padd('-t', '--transpose', action="store_true",
         help='Transpose note on/off event note values')
    padd('-i', '--inport',
         help='MIDI input port number (default: ask)')
    padd('-o', '--outport',
         help='MIDI output port number (default: ask)')
    padd('-v', '--verbose', action="store_true",
         help='verbose output')
    padd('filterargs', nargs="*", type=int,
         help='MIDI filter argument(s)')

    args = parser.parse_args(args)

    logging.basicConfig(format="%(name)s: %(levelname)s - %(message)s",
                        level=logging.DEBUG if args.verbose else logging.INFO)

    try:
        midiin, inport_name = open_midiport(args.inport, "input")
        midiout, outport_name = open_midiport(args.outport, "output")
    except IOError as exc:
        print(exc)
        return 1
    except (EOFError, KeyboardInterrupt):
        return 0

    filters = []
    #filters = [CCToBankChange(cc=99, channel=15, msb=0, lsb=1, program=99)]

    if args.transpose:
        filters.append(Transpose(transpose=args.filterargs[0]))
    if args.mpresstocc:
        filters.append(MonoPressureToCC(cc=args.filterargs[0]))
    if args.mapccrange:
        filters.append(MapControllerValue(*args.filterargs))

    dispatcher = MidiDispatcher(midiin, midiout, *filters)

    print("Entering main loop. Press Control-C to exit.")
    try:
        dispatcher.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        dispatcher.stop()
        dispatcher.join()
        print('')
    finally:
        print("Exit.")

        midiin.close_port()
        midiout.close_port()

        del midiin
        del midiout

    return 0


if __name__ == '__main__':
    sys.exit(main() or 0)
