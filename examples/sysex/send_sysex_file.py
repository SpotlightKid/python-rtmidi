#!/usr/bin/env python

import argparse
import sys
import time

from rtmidi.midiutil import open_midioutput


def main(args=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--port", help="MIDI output port")
    ap.add_argument("-l", "--length", type=int,
                    help="Maximum SysEx message length in bytes per file.")
    ap.add_argument("sysex-file", nargs="+", help="SysEx input file(s)")
    args = ap.parse_args()

    midiout, name = open_midioutput(args.port)
    print("Opened port '%s'." % name)

    for filename in getattr(args, "sysex-file"):
        with open(filename, 'rb') as syx:
            data = bytearray(syx.read())
            assert data[0] == 0xF0 and data[-1] == 0xF7

            if args.length:
                data = bytearray(data[:args.length])

            data[-1] = 0xF7
            print("Sending %d bytes from '%s'..." % (len(data), filename))
            midiout.send_message(data)

    time.sleep(0.5)
    midiout.close_port()
    del midiout


if __name__ == "__main__":
    sys.exit(main() or 0)
