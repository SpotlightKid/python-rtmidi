#!/usr/bin/env python
#
# noteon2osc.py
#
"""Send an OSC message when a MIDI Note On message is received."""

import sys
import time

import liblo

from rtmidi.midiconstants import NOTE_ON
from rtmidi.midiutil import open_midiinput


def midiin_callback(event, data=None):
    message, deltatime = event

    if message[0] & 0xF0 == NOTE_ON:
        status, note, velocity = message
        channel = (status & 0xF) + 1
        liblo.send(
            ('localhost', 9001),
            '/midi/%i/noteon' % channel,
            note,
            velocity)


# Prompts user for MIDI input port, defaulting to ALSA on Linux
try:
    port = sys.argv[1] if len(sys.argv) > 1 else None

    with open_midiinput(port, client_name='noteon2osc')[0] as midiin:
        midiin.set_callback(midiin_callback)

        while True:
            time.sleep(1)
except (EOFError, KeyboardInterrupt):
    print("Bye.")
