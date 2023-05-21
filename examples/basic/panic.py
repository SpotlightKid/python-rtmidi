#!/usr/bin/env python
#
# panic.py
#
"""Send AllSoundOff and ResetAllControllers on all JACK MIDI outputs and all channels."""

from __future__ import print_function

import time

import rtmidi
from rtmidi.midiconstants import (ALL_SOUND_OFF, CONTROL_CHANGE,
                                  RESET_ALL_CONTROLLERS)


midiout = rtmidi.MidiOut(rtapi=rtmidi.API_UNIX_JACK)
print(__doc__)

for portnum, portname in enumerate(midiout.get_ports()):
    print("Port:", portname)

    with midiout.open_port(portnum):
        for channel in range(16):
            midiout.send_message([CONTROL_CHANGE | channel, ALL_SOUND_OFF, 0])
            midiout.send_message([CONTROL_CHANGE | channel, RESET_ALL_CONTROLLERS, 0])
            time.sleep(0.05)

        time.sleep(0.1)
