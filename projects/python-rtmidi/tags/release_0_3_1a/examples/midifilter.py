#!/usr/bin/env python
#
# midifilter.py
#
"""Simple MIDI filter/ processor."""

import logging
import Queue
import sys
import threading
import time

import rtmidi

try:
    raw_input
except NameError:
    # Python 3
    raw_input = input

log = logging.getLogger("midifilter")


class MidiFilter(object):
    """ABC for midi filters."""
    def __init__(self, *args, **kwargs):
        self.args = args
        self.__dict__.update(kwargs)

    def process(self, event):
        """Process one event.

        Receives a list of MIDI event tuples (message, timestamp).

        Must return an iterable of event tuples.

        """
        raise NotImplementedError("Abstract method 'process()'.")


class Transpose(MidiFilter):
    event_types = (0x90, 0x80)

    def process(self, events):
        for event, timestamp in events:
            if event[0] & 0xF0 in self.event_types:
                # transpose note value (data byte 1)
                event[1] = max(0, min(127, event[1] + self.transpose)) & 0x7F
            yield event, timestamp


class MapControllerValue(MidiFilter):
    event_types = (0xB0,)

    def __init__(self, min_, max_, *args, **kwargs):
        super(MapControllerValue, self).__init__(*args, **kwargs)
        self.min = min_
        self.max = max_

    def process(self, events):
        for event, timestamp in events:
            # check controller number
            if event[0] & 0xF0 in self.event_types and event[1] == self.cc:
                # map controller value
                event[2] = int(self._map(event[2]))
            yield event, timestamp

    def _map(self, value):
        return value * (self.max - self.min) / 127. + self.min


class MonoPressureToCC(MidiFilter):
    event_types = (0xD0,)

    def process(self, events):
        for event, timestamp in events:
            if event[0] & 0xF0 in self.event_types:
                channel = event[0] & 0xF
                event = [0xB0 | channel, self.cc, event[1]]
            yield event, timestamp


class MidiDispatcher(threading.Thread):
    def __init__(self, midiin, midiout, *filters):
        super(MidiDispatcher, self).__init__()
        self.midiin = midiin
        self.midiout = midiout
        self.filters = filters
        self._wallclock = time.time()
        self.queue = Queue.Queue()

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


def select_midiport(midi, default=0):
    type_ = "input" if isinstance(midi, rtmidi.MidiIn) else "output"
    try:
        r = raw_input("Do you want to create a virtual MIDI %s port? (y/N) " % type_)
        if r.strip().lower() == 'y':
            return None, "midifilter MIDI %s" % type_
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
    if '-v' in args:
        args.remove('-v')
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    try:
        value = int(args.pop(0))
    except (IndexError, TypeError):
        value = 12

    logging.basicConfig(level=loglevel)

    log.debug("Creating MidiIn object.")
    midiin = rtmidi.MidiIn()
    midiinport = select_midiport(midiin)

    if midiinport is None:
        return 0
    else:
        midiinport, midiinportname = midiinport

    if midiinport is not None:
        log.info("Opening MIDI input port #%i (%s).", midiinport, midiinportname)
        midiin.open_port(midiinport, midiinportname)
    else:
        log.info("Opening virtual MIDI input port (%s).", midiinportname)
        midiin.open_virtual_port(midiinportname)

    log.debug("Creating MidiOut object.")
    midiout = rtmidi.MidiOut()
    midioutport = select_midiport(midiout)

    if midioutport is None:
        return 0
    else:
        midioutport, midioutportname = midioutport

    if midioutport is not None:
        log.info("Opening MIDI output port #%i (%s).", midioutport, midioutportname)
        midiout.open_port(midioutport, midioutportname)
    else:
        log.info("Opening virtual MIDI input port (%s).", midioutportname)
        midiout.open_virtual_port(midioutportname)

    filters = [
        #Transpose(transpose=value),
        MonoPressureToCC(cc=value),
        MapControllerValue(64, 84, cc=value)
    ]
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

        if midiinport is not None:
            midiin.close_port()

        if midioutport is not None:
            midiout.close_port()

        del midiin
        del midiout

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)
