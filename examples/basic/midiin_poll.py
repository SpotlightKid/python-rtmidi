#!/usr/bin/env python
#
# test_midiin_poll.py
#
"""Shows how to receive MIDI input by polling an input port."""

import logging
import sys
import time

from rtmidi.midiutil import open_midiport

log = logging.getLogger('test_midiin_poll')

logging.basicConfig(level=logging.DEBUG)

port = sys.argv[1] if len(sys.argv) > 1 else None
try:
    midiin, port_name = open_midiport(port)
except (EOFError, KeyboardInterrupt):
    sys.exit()

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
