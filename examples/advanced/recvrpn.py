#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# recrpn.py
#
"""Receive and decode RPN messages.

RPN (registered parameter number) messages are just regular Control Change
messages with a special semantic. To change an RPN value, the sender first
sends the parameter number with CC #100 (LSB) and #101 (MSB) and then the
parameter value with CC #38 (LSB) and #6 (MSB). Both the parameter number and
value are 14-bit values (MSB * 128 + LSB).

See also: http://www.somascape.org/midi/tech/spec.html#rpns

"""

import time
from collections import defaultdict

from rtmidi.midiconstants import (CONTROL_CHANGE, DATA_DECREMENT,
                                  DATA_ENTRY_LSB, DATA_ENTRY_MSB,
                                  DATA_INCREMENT, RPN_LSB, RPN_MSB)
from rtmidi.midiutil import open_midiinput


class RPNDecoder:
    def __init__(self, channel=1):
        self.channel = (channel - 1) & 0xF
        self.rpn = 0
        self.values = defaultdict(int)
        self.last_changed = None

    def __call__(self, event, data=None):
        msg, deltatime = event

        # event type = upper four bits of first byte
        if msg[0] == (CONTROL_CHANGE | self.channel):
            cc, value = msg[1], msg[2]

            if cc == RPN_LSB:
                self.rpn = (self.rpn >> 7) * 128 + value
            elif cc == RPN_MSB:
                self.rpn = value * 128 + (self.rpn & 0x7F)
            elif cc == DATA_INCREMENT:
                self.set_rpn(self.rpn, min(2 ** 14, self.values[self.rpn] + 1))
            elif cc == DATA_DECREMENT:
                self.set_rpn(self.rpn, max(0, self.values[self.rpn] - 1))
            elif cc == DATA_ENTRY_LSB:
                self.set_rpn(self.rpn,
                             (self.values[self.rpn] >> 7) * 128 + value)
            elif cc == DATA_ENTRY_MSB:
                self.set_rpn(self.rpn,
                             value * 128 + (self.values[self.rpn] & 0x7F))

    def set_rpn(self, rpn, value):
        self.values[rpn] = value
        self.last_changed = rpn


def main(args=None):
    decoder = RPNDecoder()
    m_in, port_name = open_midiinput(args[0] if args else None)
    m_in.set_callback(decoder)

    try:
        while True:
            rpn = decoder.last_changed

            if rpn:
                print("RPN %i: %i" % (rpn, decoder.values[rpn]))
                decoder.last_changed = None

            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        m_in.close_port()
        del m_in


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv[1:]) or 0)
