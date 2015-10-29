#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# sequencer.py
#
"""Example of using a thread to send out queued-up, timed MIDI messages."""

import logging
import threading
import time

from heapq import heappush, heappop

try:
    from Queue import Empty as QueueEmpty, Queue
except ImportError:
    from queue import Empty as QueueEmpty, Queue

try:
    range = xrange
except NameError:
    pass


log = logging.getLogger(__name__)


class MidiEvent(object):
    __slots__ = ('ticks', 'message')

    def __init__(self, ticks, message):
        self.ticks = ticks
        self.message = message

    def __repr__(self):
        return "@ %05i %r" % (self.ticks, self.message)

    def __eq__(self, other):
        return (self.ticks == other.ticks and
                self.message == other.message)

    def __lt__(self, other):
        return self.ticks < other.ticks

    def __le__(self, other):
        return self.ticks <= other.ticks

    def __gt__(self, other):
        return self.ticks > other.ticks

    def __ge__(self, other):
        return self.ticks >= other.ticks


class SequencerThread(threading.Thread):
    def __init__(self, midiout, queue=None, bpm=120.0, ppqn=480):
        super(SequencerThread, self).__init__()
        self.midiout = midiout

        # inter-thread communication
        self.queue = queue
        if queue is None:
            self.queue = Queue()
            log.debug("Created queue for MIDI output.")

        self._stopped = threading.Event()
        self._finished = threading.Event()

        # Set to current tiemm when seqquence is started
        self._start_time = None
        # Counts elapsed ticks when sequence is running
        self._tickcnt = None

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
        log.debug("Changed BPM => %s, tick interval %.2f ms.",
                  self._bpm, self._tick * 1000)

        if self._start_time:
            self._start_time = time.time() - self._tickcnt * self._tick

    def stop(self, timeout=5):
        """Set thread stop event, causing it to exit its mainloop."""
        self._stopped.set()
        log.debug("SequencerThread stop event set.")

        if self.is_alive():
            self._finished.wait(timeout)

        # flush event queue, otherwise joining the thread/process may deadlock
        # (see http://docs.python.org/library/multiprocessing.html#programming-guidelines)
        try:
            while True:
                self.queue.get(True, 1)
        except QueueEmpty:
            pass

        self.join()

    def add(self, event, ticks=None, delta=0):
        """Enqueue event for sending to MIDI output."""

        if ticks is None:
            ticks = self._tickcnt or 0

        if not isinstance(event, MidiEvent):
            event = MidiEvent(ticks, event)

        if not event.ticks:
            event.ticks = ticks

        event.ticks += delta
        self.queue.put_nowait(event)

    def get_event(self):
        """Poll the input queue for events without blocking."""
        try:
            return self.queue.get_nowait()
        except QueueEmpty:
            return None

    def run(self):
        """Start the thread's main loop.

        The thread will watch for events on the input queue and either send
        them immediately to the MIDI output or queue them for later output, if
        their timestamp has not been reached yet.

        """
        # busy loop to wait for time when next batch of events needs to
        # be written to output
        pending = []
        jitter = []
        self._tickcnt = 0
        self._start_time = time.time()

        try:
            while not self._stopped.is_set():
                q_event = self.get_event()
                current_time = time.time()
                deadline = current_time + self._tick / 2
                due = []

                # Pop events of the pending queue if the are due for this tick
                while True:
                    if pending:
                        evtdue = (self._start_time +
                                  pending[0].ticks * self._tick)

                    if not pending or evtdue > deadline:
                        break

                    evt = heappop(pending)
                    heappush(due, evt)
                    log.debug("Queued pending event for output: %r", evt)
                    jitter.append(abs(current_time - evtdue))

                if q_event:
                    log.debug("Got event from input queue: %r", q_event)
                    # Check whether event should be sent out immediately
                    # or needs to be scheduled

                    eventdue = self._start_time + q_event.ticks * self._tick

                    if eventdue <= deadline:
                        heappush(due, q_event)
                        log.debug("Queued event for output.")
                        jitter.append(abs(current_time - eventdue))
                    else:
                        heappush(pending, q_event)
                        log.debug("Scheduled event.")

                # If this batch contains any due events,
                # send them to the MIDI output.
                if due:
                    for i in range(len(due)):
                        message = heappop(due).message
                        log.debug("Midi Out: %r", message)
                        self.midiout.send_message(message)

                # calculate jitter
                if len(jitter) >= 100:
                    log.debug("Jitter (over 100 events): %0.3f (max: %0.3f,"
                        " min: %0.3f)", sum(jitter) / len(jitter),
                        max(jitter), min(jitter))
                    jitter = []

                # loop speed adjustment
                elapsed = time.time() - current_time

                if elapsed < self._tick:
                    time.sleep(self._tick - elapsed)

                self._tickcnt += 1
        except KeyboardInterrupt:
            log.debug("KeyboardInterrupt / INT signal received.")

        log.debug("Midi output mainloop exited.")
        self._finished.set()


def _test():
    import sys

    from rtmidi.midiconstants import NOTE_ON, NOTE_OFF
    from rtmidi.midiutil import open_midiport

    logging.basicConfig(level=logging.DEBUG)

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

    def add_quarter(ticks, note, vel=100):
        seq.add((NOTE_ON, note, vel), ticks)
        seq.add((NOTE_OFF, note, 0), ticks=ticks + seq.ppqn)

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


if __name__ == '__main__':
    _test()
