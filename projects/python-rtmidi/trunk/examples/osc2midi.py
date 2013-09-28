#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# osc2midi.py
#
"""Simple uni-directional OSC to MIDI gateway."""

__program__ = 'oscmidi.py'
__version__ = '1.1'
__author__  = 'Christopher Arndt'
__date__    = '$Date:$'
__usage__   = "%(prog)s [-d DEVICE] [-p PORT]"

import logging
import argparse
import sys
import time
import multiprocessing
import threading

try:
    import Queue as queue
except ImportError:
    # Python 3
    import queue

import rtmidi
import liblo

# package-specific modules
from midiconstants import *


try:
    raw_input
except NameError:
    #Python 3
    raw_input = input


log = logging.getLogger("osc2midi")



class MidiEvent(object):
    """Generic MIDI event base class.

    This also serves as a factory for more specific event (sub-)classes.

    Event classes can be registered with this class by calling the 'register'
    class method, passing the class to register. The class must have a 'type'
    attribute, which corresponds to a MIDI status byte. Event objects are
    instantiated by calling the 'fromdata' factory class method, passing the
    MIDI status byte (with the channel bits stripped off), the event data bytes
    and, optionally, the channel number. The factory method then returns an
    event instance selected based on the registered classes and the status byte.

    """
    _event_register = {}

    type = 0xFE

    def __init__(self, type=None, **kwargs):
        if type is not None:
            self.type = type
        self.__dict__.update(kwargs)

    @classmethod
    def register(cls, eventclass):
        cls._event_register[eventclass.type] = eventclass

    @classmethod
    def fromdata(cls, status, data, channel=None, timestamp=None):
        status = status & 0xF0
        eventclass = cls._event_register.get(status, cls)
        return eventclass(type=status, data=data, channel=channel,
                          timestamp=timestamp)

    def __str__(self):
        s = "Status: %02X " % self.type
        if self.channel is not None:
            s += "CH: %02i " % self.channel
        s += "Data: " + " ".join(["%-3i (%02X)" % (i, i) for i in self.data])
        return s


class RtMidiDevice(object):
    """Provides a common API for different MIDI driver implementations."""

    def __init__(self, name="RtMidiDevice", port=None, portname=None):
        self.name = name
        self.port = port
        self.portname = portname
        self._output = None

    def __str__(self):
        return self.name

    def open_output(self):
        self._output = rtmidi.MidiOut(name=self.name)
        if self.port is None:
            if self.portname is None:
                self.portname = "RtMidi Virtual Output"
            log.info("Opening virtual MIDI output port.")
            self._output.open_virtual_port(self.portname)
        else:
            if self.portname is None:
                self.portname = self._output.get_port_name(self.port)
            log.info("Opening MIDI output port #%i (%s).",
                self.port, self.portname)
            self._output.open_port(self.port, self.portname)

    def close_output(self):
        if self._output is not None:
            self._output.close_port()

    def send(self, events):
        if self._output:
            for ev in events:
                self._output.send_message(ev)

    def send_sysex(self, msg):
        if self._output:
            self._output.send_message([ord(c) for c in msg])

    @classmethod
    def time(cls):
        return time.time() / 1000.


class MidiOutputBase(object):
    def __init__(self, queue=None, bpm=120.0, ppqn=480,
            get_event=None, driver_class=RtMidiDevice, **driver_args):
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
        log.debug("Creating MidiOut instance.")
        driver = self.driver = self._driver_class(**self._driver_args)
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
                        except StandardError as exc:
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
        """Close MIDI output device."""
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


class OSC2MIDI(liblo.ServerThread):
    def __init__(self, midiout, port=5555):
        super(OSC2MIDI, self).__init__(port)
        log.info("Listening on URL: " + self.get_url())
        self.midiout = midiout
        self._note_state = [{}] * 16
        self._program = [0] * 16
        #self._velocity = {}

    @liblo.make_method(None, None)
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
            if msgtype == 'cc':
                self.midiout.send(
                    MidiEvent.fromdata(CONTROL_CHANGE,
                        channel=int(data1) & 0x7f,
                        data=[int(data1) & 0x7f, args[0] & 0x7f]))

            elif msgtype == 'on':
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

def select_midiport(midi, default=0):
    type_ = "input" if isinstance(midi, rtmidi.MidiIn) else "output"

    try:
        r = raw_input("Do you want to create a virtual MIDI %s port? (y/N) "
            % type_)
        if r.strip().lower() == 'y':
            return None
    except (KeyboardInterrupt, EOFError):
        pass

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
            except (KeyboardInterrupt, EOFError):
                return None
            except (ValueError, TypeError):
                port = default

            if port < 0 or port >= len(ports):
                print("Invalid port number: %i" % port)
                port = None
            else:
                return port, ports[port]


def main(args=None):
    argparser = argparse.ArgumentParser(usage=__usage__, description=__doc__)
    argparser.add_argument('-d', '--device', dest="device", type=int,
        help="MIDI output device (default: ask to open virtual MIDI port).")
    argparser.add_argument('-p', '--oscport',
        default=5555, type=int, dest="oscport",
        help="Port the OSC server listens on (default: %(default)s).")
    argparser.add_argument('-v', '--verbose',
        action="store_true", dest="verbose",
        help="Print debugging info to standard output.")
    argparser.add_argument('--version', action='version', version=__version__)

    args = argparser.parse_args(args if args is not None else sys.argv)

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    if args.device is None:
        midiout = rtmidi.MidiOut(name=__program__)
        args.device = select_midiport(midiout)
        del midiout

    midiout = MidiOutputProc(name=__program__, port=args.device)
    server = OSC2MIDI(midiout, args.oscport)

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
