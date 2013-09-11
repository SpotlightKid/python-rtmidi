#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# osc2midi.py
#
"""Simple uni-directional OSC to MIDI gateway."""

__program__ = b'oscmidi.py'
__version__ = '1.1'
__author__  = 'Christopher Arndt'
__date__    = '$Date:$'
__usage__   = "%(prog)s [-d DEVICE] [-p PORT]"

import logging
import argparse
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
    def __init__(self, name=None, port=None):
        super(MidiOutputProc, self).__init__()
        self.clientname = name or self.__class__.__name__
        self.port = port
        self._queue = Queue()
        self._finished = Event()

    def run(self):
        log.debug("Creating MidiOut instance.")
        self._midi = rtmidi.MidiOut(name=self.clientname)

        if self.port is None:
            log.info("Opening virtual MIDI output port.", )
            self._midi.open_virtual_port(b"osc2midi MIDI out")
        else:
            if isinstance(self.port, int):
                name = self._midi.get_port_name(self.port)
                self.port = (self.port, name)
            log.info("Opening MIDI output port #%i (%s).", *self.port)
            self._midi.open_port(self.port[0], b"osc2midi MIDI out")

        break_ = False

        while not break_:
            # nested while so we don't need a try/except
            # within the inner while-loop to ignore interrupts
            try:
                while not break_:
                    event = self._queue.get()
                    log.debug("Read event from queue: %r", event)

                    if event is None:
                        log.debug("Received stop event. "
                            "Exit MidiOutputProc loop.")
                        break_ = True

                    if event:
                        self._midi.send_message(event)
            except KeyboardInterrupt:
                pass

        self._midi.close_port()
        self._finished.set()

    def stop(self, timeout=5):
        if not self._finished.is_set():
            self.send(None)
            log.debug("MidiOutputProc stop event sent.")
            # not sure, whether those two method calls are needed,
            # but they shouldn't hurt
            self._queue.close()
            self._queue.join_thread()

        if self.is_alive():
            log.debug("Waiting for MidiOutputProc to terminate.")
            self._finished.wait(timeout)

        self.join()

    def send(self, event, timeout=0):
        if not self._finished.is_set():
            self._queue.put(event, timeout)


class OSC2MIDI(liblo.ServerThread):
    def __init__(self, midiout, port=5555):
        super(OSC2MIDI, self).__init__(port)
        log.info("Listening on URL: " + self.get_url())
        self.midiout = midiout
        self._note_state = {}
        self._program = 0
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
            self._note_state[note] = 0
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
            self._program = args[0] & 0x7f
            self.midiout.send([0xc0 | channel, args[0] & 0x7f])
        elif msgtype == 'pcrel':
            channel = int(channel) & 0xf
            if int(args[0]) > 0:
                self._program = min(127, self._program + 1)
            else:
                self._program = max(0, self._program - 1)
            self.midiout.send([0xc0 | channel, self._program])
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
