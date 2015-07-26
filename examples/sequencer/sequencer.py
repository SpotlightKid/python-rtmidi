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
    def __init__(self, timestamp, message):
        self.timestamp = timestamp
        self.message = message
    def __repr__(self):
        return "%r @ %.2f" % (self.message, self.timestamp)

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
        self.resolution = 60. / value / self.ppqn

    def stop(self):
        """Set thread stop event, causing it to exit its mainloop."""
        self._stopped.set()
        log.debug("SequencerThread stop event set.")

        if self.is_alive():
            self._finished.wait()

        self.join()

    def add(self, event, timestamp=None, delta=0):
        """Enqueue event for sending to MIDI output."""

        if timestamp is None:
            timestamp = time.time()

        if not isinstance(event, MidiEvent):
            event = MidiEvent(timestamp, event)

        if not event.timestamp:
            event.timestamp = timestamp

        event.timestamp += delta
        self.queue.put_nowait(event)

    def get_event(self):
        """Poll the input queue for events without blocking."""
        try:
            return self.queue.get_nowait()
        except QueueEmpty:
            return None

    def run(self):
        """Start the thread's main loop.

        The thread will watch for events on the input queue and either output
        them immediately to the MIDI output or queue them for later output, if
        their timestamp has not been reached yet.

        """
        # busy loop to wait for time when next batch of events needs to
        # be written to output
        pending = []
        jitter = []

        try:
            while not self._stopped.is_set():
                queue_event = self.get_event()
                current_time = time.time()
                due = []

                # go through the batch of events for this tick and handle them
                # according to type
                while True:
                    if not pending or pending[0].timestamp > current_time:
                        break

                    ev = heappop(pending)
                    heappush(due, ev)
                    log.debug("Queued pending event for output: %r", ev)
                    jitter.append(current_time - ev.timestamp)

                if queue_event:
                    log.debug("Got event from input queue: %r", queue_event)
                    # Check whether event should be sent out immediately
                    # or needs to be scheduled
                    if queue_event.timestamp <= current_time:
                        heappush(due, queue_event)
                        log.debug("Queued event for output.")
                        jitter.append(current_time - queue_event.timestamp)
                    else:
                        heappush(pending, queue_event)
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

                if elapsed < self.resolution:
                    time.sleep(self.resolution - elapsed)
        except KeyboardInterrupt:
            log.debug("KeyboardInterrupt / INT signal received.")

        log.debug("Midi output mainloop exited.")
        self._finished.set()


def _test():
    from rtmidi.midiconstants import NOTE_ON, NOTE_OFF
    from rtmidi.midiutil import open_midiport

    logging.basicConfig(level=logging.DEBUG)
    midiout, port = open_midiport(None, "output",
                                  client_name="RtMidi Sequencer")
    seq = SequencerThread(midiout)
    seq.start()

    seq.add((NOTE_ON, 60, 100))
    seq.add((NOTE_OFF, 60, 0), delta=2)

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        seq.stop()
        midiout.close_port()


if __name__ == '__main__':
    _test()
