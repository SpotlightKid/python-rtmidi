#!/usr/bin/env python
#
# test_midiout.py
#
"""Shows how to open an output port and send MIDI events."""

import sys
import time

import rtmidi

print("Creating MidiOut object.")
midiout = rtmidi.MidiOut()
available_ports = midiout.get_ports(encoding='latin1'
    if sys.platform.startswith('win') else 'utf-8')

if available_ports:
    try:
        # Use port number given on command line, if valid
        port = int(sys.argv[1])
        if port < 0 or port >= len(available_ports):
            raise ValueError
    except Exception as exc:
        print("No or invalid port number specified, using port #0.")
        port = 0

    print("Opening output port #%i (%s)." % (port, available_ports[port]))
    midiout.open_port(port)
else:
    port_name = "My virtual output"
    print("Opening virtual output port (%s)." % port_name)
    # port name is optional, defaults to "RtMidi Output"
    midiout.open_virtual_port(port_name)

note_on = [0x99, 60, 112] # channel 10, middle C, velocity 112
note_off = [0x89, 60, 0]

print("Sending NoteOn event.")
midiout.send_message(note_on)
time.sleep(1)
print("Sending NoteOff event.")
midiout.send_message(note_off)

del midiout
print("Exit.")
