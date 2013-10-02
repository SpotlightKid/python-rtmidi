# -*- coding: utf-8 -*-
#
# osc2midi/midiio.py
#
"""Asynchroneous MIDI input / output framework."""

__all__ = [
    "MidiOutputBase",
    "MidiOutputProc",
    "MidiOutputThread",
]

import logging
import multiprocessing
import threading
import time

try:
    import Queue as queue
except ImportError:
    # Python 3
    import queue

try:
    StandardError
except NameError:
    StandardError = Exception

import rtmidi
from rtmidi.midiconstants import *

from . import device

log = logging.getLogger(__name__)


class MidiOutputBase(object):
    def __init__(self, queue=None, bpm=120.0, ppqn=480,
            get_event=None, driver_class="RtMidiDevice", **driver_args):
        super(MidiOutputBase, self).__init__()
        driver_args.setdefault('name', self.__class__.__name__)
        self._driver_args = driver_args
        self._driver_class = driver_class

        # inter-thread communication
        if queue is None:
            self._queue = self.queue_class()
            log.debug("Created queue for MIDI output: %r", self._queue)
        else:
            self._queue = queue

        self._stopped = self.event_class()
        self._stopped.set()

        # run-time options
        self.queue_timeout = 1
        self.all_notes_off_on_stop = True
        self.ppqn = ppqn
        self.bpm = bpm

        # If no function to poll/get events is provided, we use our own default
        # implementation, which fetches events from the queue.
        if get_event is None:
            get_event = self._get_event
        self.get_event = get_event

    def run(self):
        """Start the MIDI output thread's/process' main loop.

        It will watch for events on the input queue and either output them
        immediately to the driver or queue them for later output, if their
        timestamp has not been reached yet.

        """
        # Instantiate the driver.
        # We do this ourselves instead of passing in a driver instance
        # so that the I/O class can run in a different thread or process.
        log.debug("Creating %s instance with args: %r.",
            self._driver_class, self._driver_args)
        driver = self.driver = getattr(device, self._driver_class)(**self._driver_args)
        driver.open_output()

        # busy loop to wait for time when next batch of events needs to
        # be written to output
        self.pending = []
        jitter = []
        loops = 0
        break_ = False
        self._stopped.clear()

        while not break_:
            # nested while so we don't need a try/except
            # within the inner while-loop to ignore interrupts
            try:
                while not break_:
                    queue_event = self.get_event()

                    if queue_event == "STOP":
                        log.debug("Received stop event. "
                            "Exit MidiOutputProc loop.")
                        break_ = True
                        break

                    current_time = driver.time()

                    event_list = []

                    # go through the pending events for this tick and handle
                    # queue them for output
                    while self.pending and self.pending[0].timestamp > current_time:
                        ev = self.pending.pop(0)
                        log.debug("%s: picked up event from schedule queue: %s",
                            driver, ev)
                        self._output_event(ev, event_list)
                        log.debug("%s: queued event for output.", driver)
                        jitter.append(current_time - ev.timestamp)
                        loops += 1

                    # Check whether an event received through the queue should
                    # be sent out immediately or needs to be scheduled
                    if queue_event:
                        log.debug("%s: received event from IPC queue: %s",
                            driver, queue_event)
                        if queue_event.timestamp <= current_time:
                            self._output_event(queue_event, event_list)
                            log.debug("%s: queued event for output.", driver)
                            jitter.append(current_time - queue_event.timestamp)
                            loops += 1
                        else:
                            self._schedule_event(queue_event)
                            log.debug("%s: scheduled event.", driver)

                    # If this batch contains any pending channel/system message
                    # events, send them all to the MIDI driver at once.
                    if event_list:
                        log.debug("Midi Out(%s): %r", driver.port, event_list)
                        try:
                            driver.send(event_list)
                        except StandardError:
                            log.exception("%s: error writing MIDI events: %r",
                                driver, event_list)

                    # calculate jitter
                    if loops >= 100:
                        log.debug("%s: Jitter (over 100 events): %0.3f (max: %0.3f,"
                            " min: %0.3f)", driver, sum(jitter) / loops,
                            max(jitter), min(jitter))
                        jitter = []
                        loops = 0

                    # no MIDI data available at the moment
                    else:
                        elapsed = driver.time() - current_time

                        if elapsed < self.resolution:
                            time.sleep(self.resolution - elapsed)

            except KeyboardInterrupt:
                log.debug("KeyboardInterrupt / INT signal received in output "
                    "thread. Ignoring it.")

        log.debug("Midi output mainloop exited.")
        # cleanup
        if self.all_notes_off_on_stop:
            self._all_notes_off()

        log.info("Closing driver output port...")
        self.driver.close_output()
        self._stopped.set()

    # public API

    # inherited from Thread/Process
    # def start(self)

    def stop(self, timeout=5):
        if not self._stopped.is_set():
            self._queue.put_nowait("STOP")
            log.debug("MidiOutputProc stop event sent.")

        if self.is_alive():
            log.debug("Waiting for MidiOutputProc to terminate.")
            self._stopped.wait(timeout)

        # flush event queue, otherwise joining the thread/process may deadlock
        # (see http://docs.python.org/library/multiprocessing.html#programming-guidelines)
        try:
            while True:
                self._queue.get(True, self.queue_timeout)
        except queue.Empty:
            pass

        # not sure, whether those two method calls are needed,
        # but they shouldn't hurt (only available for multiprocessing.Queue)
        try:
            self._queue.close()
            self._queue.join_thread()
        except AttributeError:
            pass

        self.join()

    def send(self, event, time=None, delta=0, timeout=None):
        """Enqueue event for sending to MIDI output."""
        if not self._stopped.is_set():
            if event.timestamp is None:
                if time is None:
                    time = self.time()
                event.timestamp = time

            if timeout is None:
                timeout = self.queue_timeout

            event.timestamp += delta
            self._queue.put(event, timeout)
        else:
            raise RuntimeError("Output queue is not running.")


    def time(self):
        """Return driver's notion of the current time.

        The unit should by convention be milliseconds.

        """
        driver = getattr(self, 'driver', None)

        if driver:
            return driver.time()

        return self._driver_class.time()

    def _get_bpm(self):
        """Return current beats-per-minute value."""
        return self._bpm
    def _set_bpm(self, bpm):
        self._bpm = bpm
        self.resolution = 60. / self.bpm / self.ppqn
    bpm = property(_get_bpm, _set_bpm)

    # Internal methods -
    # These should only be called by instance methods of this class
    # ( or superclasses)

    def __del__(self):
        self._close()

    def _close(self):
        """Close MIDI output port."""
        # If start() was never called, we might be called by __del__ and
        # self.driver is not yet defined
        if getattr(self, 'driver', None):
            self.driver.close_port()
            self.driver = None

    def _get_event(self):
        """Poll the input queue for events without blocking.

        You can supply your own polling function to the constructor. It must
        return a list of MidiEvents or None and should not block.

        """
        try:
            return self._queue.get_nowait()
        except queue.Empty:
            return None

    def _schedule_event(self, event):
        """Queue event until its timestamp is reached."""
        self.pending.append(event)
        if len(self.pending) > 1:
            self.pending.sort(key=attrgetter('timestamp'))

    def _output_event(self, ev, event_list):
        """Queue event for immediate output to the driver."""
        if ev.type == SYSTEM_EXCLUSIVE:
            # write sysex message to MIDI output driver immediately
            self.driver.send_sysex('\xF0' + ev.data)
            log.debug("Midi Out(%s): System Exclusive %i bytes",
                self.driver.port, len(ev.data))
        else:
            # write channel and system events to MIDI output driver
            if ev.channel is not None:
                msg = [ev.type | ev.channel] + list(ev.data)
            else:
                msg = [ev.type] + list(ev.data)
            event_list.append(msg)

    def _all_notes_off(self, channels=range(16)):
        """Send All Notes Off message(s) directly on all given channels.

        If no channel or list of channel numbers is given, use all 16 channels.

        Will be called when thread mainloop exits if the instance attribute
        'all_notes_off_on_stop' evaluates to True.

        """
        if isinstance(channels, int):
            channels = [channels]

        messages = []
        for channel in channels:
            log.debug("%s: Sending ALL NOTES OFF on channel %02i",
                self.driver, channel + 1)
            messages.append([CONTROLLER_CHANGE | channel, ALL_NOTES_OFF, 0])

        self.driver.send(messages)


class MidiOutputThread(MidiOutputBase, threading.Thread):
    """Handles writing MIDI events to the driver in the background.

    Uses a thread for concurrent processing.

    """
    event_class = staticmethod(threading.Event)
    queue_class = staticmethod(queue.Queue)


class MidiOutputProc(MidiOutputBase, multiprocessing.Process):
    """Handles writing MIDI events to the driver in the background.

    Uses a child process for concurrent processing.

    """
    event_class = staticmethod(multiprocessing.Event)
    queue_class = staticmethod(multiprocessing.Queue)
