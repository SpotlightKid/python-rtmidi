#/usr/bin/env python
# -*- coding: utf-8 -*-
#
# sysexsaver.py
#
"""Save revceived sysex message to directory given on command line."""

import os
import sys
import time

from datetime import datetime
from os.path import exists, isdir, join

try:
    raw_input
except NameError:
    # Python 3
    raw_input = input

import rtmidi
from manufacturers import manufacturers

SOX = 0xF0
EOX = 0xF7

class SysexMessage(object):
    @classmethod
    def fromdata(cls, data):
        self = cls()
        if data[0] != SOX:
            raise ValuError("Message does not start with 0xF0")
        if data[-1] != EOX:
            raise ValuError("Message does not end with 0xF7")
        if len(data) < 5:
            raise ValuError("Message too short")
        if data[1] == 0:
            self._manufacturer = (data[1], data[2], data[3])
            self._device = data[5]
        else:
            self._manufacturer = data[1]
            self._device = data[2]

        self._data = data
        return self

    @property
    def manufacturer(self):
        m = manufacturers.get(self._manufacturer)
        if m:
            return m[1] or m[0]

    @property
    def device(self):
        return "0x%02X" % self._device

    def __str__(self):
        return "".join([chr(b) for b in self._data])

class SysexSaver(object):
    def __init__(self, port, directory):
        self.port = port
        self.directory = directory

    def __call__(self, event, data=None):
        message, deltatime = event
        if message[:1] == [SOX]:
            dt = datetime.now()
            print("[%i: %s] Received sysex msg of %i bytes." % (
                self.port, dt.strftime('%x %X'), len(message)))
            sysex = SysexMessage.fromdata(message)

            data = dict(timestamp=dt.strftime('%Y%m%dT%H%M%S'))
            data['manufacturer'] = (sysex.manufacturer or 'unknown').lower().replace(' ', '_')
            data['device'] = sysex.device

            outfn = join(self.directory,
                "%(manufacturer)s-%(device)s-%(timestamp)s.syx" % data)

            if exists(outfn):
                print("Output file already exists, will not overwrite.")
            else:
                outfile = open(outfn, 'wb')
                outfile.write(str(sysex))
                outfile.close()


def open_midiport():
    print("Creating MidiIn object.")
    midiin = rtmidi.MidiIn()

    try:
        use_virtual = False
        r = raw_input("Do you want to create a virtual MIDI input port? (y/N) ")

        if r.strip().lower() == 'y':
            midiin.open_virtual_port()
            use_virtual = True
            port_name = "Virtual MIDI Input"
    except (KeyboardInterrupt, EOFError):
        pass

    if not use_virtual:
        ports = midiin.get_ports(encoding='latin1'
            if sys.platform.startswith('win') else 'utf-8')

        if not ports:
            print("No MIDI input ports found.")
            del midiin
            sys.exit(1)
        else:
            print("Available MIDI input ports:\n")
            for port, name in enumerate(ports):
                print("[%i] %s" % (port, name))
            print('')

        try:
            port = int(sys.argv[1])
        except:
            try:
                r = raw_input("Select MIDI input port (Control-C to exit) [0]: ")
                port = int(r)
            except (KeyboardInterrupt, EOFError):
                print('')
                del midiin
                sys.exit()
            except (ValueError, TypeError):
                port = 0

        if port < 0 or port >= len(ports):
            print("Invalid port number: %i" % port)
            del midiin
            sys.exit(1)
        else:
            port_name = ports[port]

        print("Opening MIDI input port #%i (%s)." % (port, port_name))
        midiin.open_port(port)

    return midiin, port

def main(args=None):
    """Save revceived sysex message to directory given on command line."""

    midiin, port = open_midiport()

    if len(sys.argv) > 1 and isdir(sys.argv[1]):
        ss = SysexSaver(port, sys.argv[1])
    else:
        ss = SysexSaver(port, os.getcwd())

    print("Attaching MIDI input callback handler.")
    midiin.set_callback(ss)
    print("Enabling reception of sysex messages.")
    midiin.ignore_types(sysex=False)

    print("Entering main loop. Press Control-C to exit.")
    try:
        # just wait for keyboard interrupt in main thread
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('')
    finally:
        print("Exit.")
        midiin.close_port()
        del midiin

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)
