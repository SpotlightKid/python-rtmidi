#!/usr/bin/env python
#
# midiout.py
#
"""Show how to open an output port and send MIDI events."""

from __future__ import print_function

import logging
import sys
import time

from rtmidi.midiutil import open_midioutput
from rtmidi.midiconstants import NOTE_OFF, NOTE_ON


log = logging.getLogger('midiout')
logging.basicConfig(level=logging.DEBUG)

# Prompts user for MIDI input port, unless a valid port number or name
# is given as the first argument on the command line.
# API backend defaults to ALSA on Linux.
port = sys.argv[1] if len(sys.argv) > 1 else None

try:
    midiout, port_name = open_midioutput(port)
except (EOFError, KeyboardInterrupt):
    sys.exit()

note_on = [NOTE_ON, 60, 112]  # channel 1, middle C, velocity 112
note_off = [NOTE_OFF, 60, 0]

with midiout:
    print("Sending NoteOn event.")
    midiout.send_message(note_on)
    time.sleep(1)
    print("Sending NoteOff event.")
    midiout.send_message(note_off)
    time.sleep(0.1)

del midiout
print("Exit.")
