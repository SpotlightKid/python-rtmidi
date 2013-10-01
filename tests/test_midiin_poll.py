#!/usr/bin/env python
#
# test_midiin_poll.py
#
"""Shows how to receive MIDI input by polling an input port."""

import sys
import time

import rtmidi
from rtmidi.midiutil import open_midiport


port = int(sys.argv[1]) if len(sys.argv) > 1 else None
midiin, port_name = open_midiport(port)

print("Entering main loop. Press Control-C to exit.")
try:
    timer = time.time()
    while True:
        msg = midiin.get_message()

        if msg:
            message, deltatime = msg
            timer += deltatime
            print("[%s] @%0.6f %r" % (port_name, timer, message))

        time.sleep(0.01)
except KeyboardInterrupt:
    print('')
finally:
    print("Exit.")
    midiin.close_port()
    del midiin
