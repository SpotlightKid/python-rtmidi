#!/usr/bin/env python
#
# test_midiout.py
#
"""Shows how to open an output port and send MIDI events."""

import sys
import time

import rtmidi
from rtmidi.midiutil import open_midiport
from rtmidi.midiconstants import *

port = int(sys.argv[1]) if len(sys.argv) > 1 else None
midiout, port_name = open_midiport(port, "output")

note_on = [NOTE_ON, 60, 112] # channel 1, middle C, velocity 112
note_off = [NOTE_OFF, 60, 0]

print("Sending NoteOn event.")
midiout.send_message(note_on)
time.sleep(1)
print("Sending NoteOff event.")
midiout.send_message(note_off)

del midiout
print("Exit.")