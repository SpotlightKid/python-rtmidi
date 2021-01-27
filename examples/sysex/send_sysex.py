#!/usr/bin/env python

import argparse
import sys
import time

from rtmidi.midiutil import open_midioutput


def main(args=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--port", help="MIDI output port")
    ap.add_argument("sysex-byte", nargs="+",
                    help="SysEx bytes as hexadecimal")
    args = ap.parse_args()

    midiout, name = open_midioutput(args.port)
    print("Opened port '%s'." % name)

    data = bytearray.fromhex("".join(getattr(args, "sysex-byte")))
    assert data[0] == 0xF0 and data[-1] == 0xF7
    print("Sending %d bytes" % len(data))
    midiout.send_message(data)

    time.sleep(0.5)
    midiout.close_port()
    del midiout


if __name__ == "__main__":
    sys.exit(main() or 0)
