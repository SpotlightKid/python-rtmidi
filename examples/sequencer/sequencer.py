#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# sequencer.py
#
"""Example of using a thread to send out queued-up, timed MIDI messages."""

import logging
import threading
import time

from collections import deque
from heapq import heappush, heappop

try:
    range = xrange  # noqa
except NameError:
    pass


log = logging.getLogger(__name__)


class MidiEvent(object):
    """Container for a MIDI message and a timing tick.

    Bascially like a two-item named tuple, but we overwrite the comparison
    operators, so that they (except when testing for equality) use only the
    timing ticks.

    """

    __slots__ = ('tick', 'message')

    def __init__(self, tick, message):
        self.tick = tick
        self.message = message

    def __repr__(self):
        return "@ %05i %r" % (self.tick, self.message)

    def __eq__(self, other):
        return (self.tick == other.tick and
                self.message == other.message)

    def __lt__(self, other):
        return self.tick < other.tick

    def __le__(self, other):
        return self.tick <= other.tick

    def __gt__(self, other):
        return self.tick > other.tick

    def __ge__(self, other):
        return self.tick >= other.tick


class SequencerThread(threading.Thread):
    def __init__(self, midiout, queue=None, bpm=120.0, ppqn=480):
        super(SequencerThread, self).__init__()
        # log.debug("Created sequencer thread.")
        self.midiout = midiout

        # inter-thread communication
        self.queue = queue
        if queue is None:
            self.queue = deque()
            # log.debug("Created queue for MIDI output.")

        self._stopped = threading.Event()
        self._finished = threading.Event()

        # Counts elapsed ticks when sequence is running
        self._tickcnt = None
        # Max number of input queue events to get in one loop
        self._batchsize = 100

        # run-time options
        self.ppqn = ppqn
        self.bpm = bpm

    @property
    def bpm(self):
        """Return current beats-per-minute value."""
        return self._bpm

    @bpm.setter
    def bpm(self, value):
        self._bpm = value
        self._tick = 60. / value / self.ppqn
        # log.debug("Changed BPM => %s, tick interval %.2f ms.",
        #           self._bpm, self._tick * 1000)

    def stop(self, timeout=5):
        """Set thread stop event, causing it to exit its mainloop."""
        self._stopped.set()
        # log.debug("SequencerThread stop event set.")

        if self.is_alive():
            self._finished.wait(timeout)

        self.join()

    def add(self, event, tick=None, delta=0):
        """Enqueue event for sending to MIDI output."""
        if tick is None:
            tick = self._tickcnt or 0

        if not isinstance(event, MidiEvent):
            event = MidiEvent(tick, event)

        if not event.tick:
            event.tick = tick

        event.tick += delta
        self.queue.append(event)

    def get_event(self):
        """Poll the input queue for events without blocking.

        Could be overwritten, e.g. if you passed in your own queue instance
        with a different API.

        """
        try:
            return self.queue.popleft()
        except IndexError:
            return None

    def handle_event(self, event):
        """Handle the event by sending it to MIDI out.

        Could be overwritten, e.g. to handle meta events, like time signature
        and tick division changes.

        """
        # log.debug("Midi Out: %r", event.message)
        self.midiout.send_message(event.message)

    def run(self):
        """Start the thread's main loop.

        The thread will watch for events on the input queue and either send
        them immediately to the MIDI output or queue them for later output, if
        their timestamp has not been reached yet.

        """
        # busy loop to wait for time when next batch of events needs to
        # be written to output
        pending = []
        self._tickcnt = 0

        try:
            while not self._stopped.is_set():
                due = []
                curtime = time.time()

                # Pop events off the pending queue
                # if they are due for this tick
                while True:
                    if not pending or pending[0].tick > self._tickcnt:
                        break

                    evt = heappop(pending)
                    heappush(due, evt)
                    # log.debug("Queued pending event for output: %r", evt)

                # Pop up to self._batchsize events off the input queue
                for i in range(self._batchsize):
                    evt = self.get_event()

                    if not evt:
                        break

                    # log.debug("Got event from input queue: %r", evt)
                    # Check whether event should be sent out immediately
                    # or needs to be scheduled

                    if evt.tick <= self._tickcnt:
                        heappush(due, evt)
                        # log.debug("Queued event for output.")
                    else:
                        heappush(pending, evt)
                        # log.debug("Scheduled event in pending queue.")

                # If this batch contains any due events,
                # send them to the MIDI output.
                if due:
                    for i in range(len(due)):
                        self.handle_event(heappop(due))

                # loop speed adjustment
                elapsed = time.time() - curtime

                if elapsed < self._tick:
                    time.sleep(self._tick - elapsed)

                self._tickcnt += 1
        except KeyboardInterrupt:
            # log.debug("KeyboardInterrupt / INT signal received.")
            pass

        # log.debug("Midi output mainloop exited.")
        self._finished.set()


def _test():
    import sys

    from rtmidi.midiconstants import NOTE_ON, NOTE_OFF
    from rtmidi.midiutil import open_midiport

    logging.basicConfig(level=logging.DEBUG, format="%(message)s")

    try:
        midiout, port = open_midiport(
            sys.argv[1] if len(sys.argv) > 1 else None,
            "output",
            client_name="RtMidi Sequencer")
    except (IOError, ValueError) as exc:
        return "Could not open MIDI input: %s" % exc
    except (EOFError, KeyboardInterrupt):
        return

    seq = SequencerThread(midiout, bpm=100, ppqn=240)

    def add_quarter(tick, note, vel=100):
        seq.add((NOTE_ON, note, vel), tick)
        seq.add((NOTE_OFF, note, 0), tick=tick + seq.ppqn)

    t = 0
    p = seq.ppqn
    add_quarter(t, 60)
    add_quarter(t + p, 64)
    add_quarter(t + p * 2, 67)
    add_quarter(t + p * 3, 72)

    t = p * 5
    add_quarter(t, 60)
    add_quarter(t + p, 64)
    add_quarter(t + p * 2, 67)
    add_quarter(t + p * 3, 72)

    try:
        seq.start()
        time.sleep(60. / seq.bpm * 4)
        seq.bpm = 150
        time.sleep(60. / seq.bpm * 6)
    finally:
        seq.stop()
        midiout.close_port()
        del midiout


if __name__ == '__main__':
    _test()
