#!/usr/bin/env python
#
# test_midiin_callback.py
#
"""Shows how to receive MIDI input by setting a callback function."""

import sys
import time

import rtmidi

try:
    raw_input
except NameError:
    # Python 3
    raw_input = input

class MidiInputHandler(object):
    def __init__(self, port):
        self.port = port
        self._wallclock = time.time()

    def __call__(self, event, data=None):
        message, deltatime = event
        self._wallclock += deltatime
        print("[%s] @%0.6f %r" % (self.port, self._wallclock, message))

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

print("Attaching MIDI input callback handler.")
midiin.set_callback(MidiInputHandler(port_name))

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
