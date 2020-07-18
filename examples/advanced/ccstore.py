#!/usr/bin/env python
"""Record last seen value of specific Control Change events.

The main loop prints out last seen value of specific Control Change events
every second. The control change events are received by a MIDI input
callback, which gets called on every MIDI event received and runs
independently from the main loop.

"""

import time

from rtmidi.midiutil import open_midiinput
from rtmidi.midiconstants import (
    CONTROL_CHANGE,
    MODULATION,
    CHANNEL_VOLUME,
    EXPRESSION_CONTROLLER,
)


CONTROLLERS = (MODULATION, CHANNEL_VOLUME, EXPRESSION_CONTROLLER)


class MidiInHandler:
    def __init__(self, channel=1, controllers=None):
        self.ch = channel
        self.ccs = controllers or ()
        self._cur_value = {}

    def __call__(self, event, *args):
        event, delta = event
        status = event[0] & 0xF0
        ch = event[0] & 0xF

        if status == CONTROL_CHANGE and ch == self.ch - 1 and event[1] in self.ccs:
            self._cur_value[event[1]] = event[2]

    def get(self, cc, default=None):
        return self._cur_value.get(cc, default)


def main(args):
    midiin, _ = open_midiinput(args[0] if args else None)

    # record Modulation, Volume and Expression CC events
    handler = MidiInHandler(channel=1, controllers=CONTROLLERS)
    midiin.set_callback(handler)

    try:
        with midiin:
            while True:
                for cc in CONTROLLERS:
                    print("CC #%i: %s" % (cc, handler.get(cc)))

                print("--- ")
                time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        del midiin


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
