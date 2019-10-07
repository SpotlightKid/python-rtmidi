#!/usr/bin/env python
#
# contextmanager.py
#
"""Shows how to use a MidiOut instance as a context manager."""

import time
import rtmidi

from rtmidi.midiconstants import NOTE_OFF, NOTE_ON

NOTE = 60  # middle C

midiout = rtmidi.MidiOut()

with (midiout.open_port(0) if midiout.get_ports() else
        midiout.open_virtual_port("My virtual output")):
    note_on = [NOTE_ON, NOTE, 112]
    note_off = [NOTE_OFF, NOTE, 0]
    midiout.send_message(note_on)
    time.sleep(0.5)
    midiout.send_message(note_off)
    time.sleep(0.1)

del midiout
