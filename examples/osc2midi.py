#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# osc2midi.py
#
"""Simple uni-directional OSC to MIDI gateway."""

__program__ = 'oscmidi.py'
__version__ = '1.0'
__author__  = 'Christopher Arndt'
__date__    = '$Date:$'
__usage__   = "%prog [-d DEVICE] [-p PORT]"

import logging
import optparse
import sys
import time

from multiprocessing import Event, Process, Queue

import rtmidi
import liblo

try:
    raw_input
except NameError:
    raw_input = input # Python 3


log = logging.getLogger("osc2midi")


class MidiOutputProc(Process):
    def __init__(self, port=None):
        self._queue = Queue()
        self._finished = Event()
        log.debug("Creating MidiOut instance.")
        self._midi = rtmidi.MidiOut()

        if port is None:
            try:
                self.port = select_midiport(self._midi)[0]
            except:
                self.port = None
        else:
            self.port = port

        super(MidiOutputProc, self).__init__()

    def run(self):
        if self.port is None:
            log.info("Opening virtual MIDI output port.", )
            self._midi.open_virtual_port(b"osc2midi MIDI out")
        else:
            portname = self._midi.get_port_name(self.port)
            log.info("Opening MIDI output port #%i (%s).", self.port, portname)
            self._midi.open_port(self.port)

        try:
            while True:
                event = self._queue.get()

                if event is None:
                    log.debug("Received stop event. Exit MidiOutputProc loop.")
                    break

                log.debug("Read event from queue: %r", event)
                self._midi.send_message(event)
        except KeyboardInterrupt:
            pass

        self._midi.close_port()
        self._finished.set()

    def stop(self, timeout=5):
        log.debug("MidiOutputProc stop event send.")
        self._queue.put_nowait(None)

        if self.is_alive():
            self._finished.wait(timeout)

        self.join()

    def send(self, event, timeout=0):
        self._queue.put(event, timeout)


class OSC2MIDI(liblo.ServerThread):
    def __init__(self, midiout, port=5555):
        super(OSC2MIDI, self).__init__(port)
        log.info("Listening on URL: " + self.get_url())
        self.midiout = midiout
        self._note_state = {}
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

        if msgtype == 'cc':
            channel = int(channel) & 0xf
            cc = int(data1) & 0x7f
            self.midiout.send([0xb0 | channel, cc, args[0] & 0x7f])
        elif msgtype == 'on':
            channel = int(channel) & 0xf
            note = int(data1) & 0x7f

            if args[0] == 0 and self._note_state.get(note, 0) == 2:
                self.midiout.send([0x90 | channel, note, 0])

            self._note_state[note] = args[0]
        elif msgtype == 'off':
            channel = int(channel) & 0xf
            note = int(data1) & 0x7f
            self.midiout.send([0x80 | channel, note, args[0] & 0x7f])
        elif msgtype == 'pb':
            channel = int(channel) & 0xf
            data1 = args[0] & 0x7f
            data2 = (args[0] >> 7) & 0x7f
            self.midiout.send([0xe0 | channel, data1, data2])
        elif msgtype == 'mp':
            channel = int(channel) & 0xf
            self.midiout.send([0xd0 | channel, args[0] & 0x7f])
        elif msgtype == 'pc':
            channel = int(channel) & 0xf
            self.midiout.send([0xc0 | channel, args[0] & 0x7f])
        elif msgtype == 'pp':
            channel = int(channel) & 0xf
            note = int(data1) & 0x7f

            if self._note_state.get(note, 0) == 1:
                self.midiout.send([0x90 | channel, note, 127 - (args[0] & 0x7f)])
                #self.midiout.send([0xa0 | channel, note, args[0] & 0x7f])
                self._note_state[note] = 2
        else:
            return 1


def select_midiport(midi, default=0):
    type_ = "output" if isinstance(midi, rtmidi.MidiOut) else "input"
    try:
        r = raw_input("Do you want to create a virtual MIDI %s port? (y/N) " % type_)
        if r.strip().lower() == 'y':
            return None, "osc2midi MIDI %s" % type_
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
    optparser = optparse.OptionParser(usage=__usage__, description=__doc__,
        version=__version__)
    optparser.add_option('-d', '--device', dest="device",
        help="MIDI output device (default: open virtual MIDI port).")
    optparser.add_option('-p', '--oscport',
        default=5555, type="int", dest="oscport",
        help="Port the OSC server listens on (default: %default).")
    optparser.add_option('-v', '--verbose',
        action="store_true", dest="verbose",
        help="Print debugging info to standard output.")

    options, args = optparser.parse_args(
        args if args is not None else sys.argv)

    if options.verbose:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    logging.basicConfig(level=loglevel)
    midiout = MidiOutputProc(options.device)
    server = OSC2MIDI(midiout, options.oscport)

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
