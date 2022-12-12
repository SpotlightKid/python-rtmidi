#!/usr/bin/env python3
"""Send all notes and CCs with all possible values an all 16 channels."""

import argparse
import logging
import sys
import time

from rtmidi.midiutil import open_midioutput
from rtmidi.midiconstants import *


log = logging.getLogger("midi-send-all")

argp = argparse.ArgumentParser()
argp.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="Verbose output"
)
argp.add_argument(
    "-c",
    "--channels",
    help="Channel or list of channels (comma-separated) to send on (default: 1..16)",
)
argp.add_argument(
    "-d",
    "--delay",
    type=float,
    default=0.01,
    help="Delay between messages (default: %(default).2f s)",
)
argp.add_argument(
    "-o",
    "--off-velocity",
    type=int,
    default=64,
    help="Note off velocity (default: %(default)i)"
)
argp.add_argument(
    "-V",
    "--velocity",
    type=int,
    default=127,
    help="Note on velocity (default: %(default)i)"
)
argp.add_argument(
    "port",
    nargs="?",
    help="MIDI output port (default: ask)"
)

args = argp.parse_args()

logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

if args.channels:
    channels = []
    for ch in args.channels.split(","):
        try:
            ch = int(ch.strip()) - 1
            if 0 > ch > 16:
                raise ValueError
        except:
            argp.print_help()
            sys.exit(1)

        channels.append(ch)
else:
    channels = range(16)

try:
    midiout, name = open_midioutput()

    with midiout:
        for chan in channels:
            for note in range(128):
                log.debug(f"Sending NOTE ON:  ch={chan+1:02}, note={note:03}, vel={args.velocity:03}")
                midiout.send_message([NOTE_ON | chan, note, args.velocity])
                time.sleep(args.delay)
                log.debug(f"Sending NOTE OFF: ch={chan+1:02}, note={note:03}, vel={args.off_velocity:03}")
                midiout.send_message([NOTE_OFF | chan, note, args.off_velocity])
                time.sleep(args.delay)

        for chan in channels:
            for cc in range(128):
                for val in range(128):
                    log.debug(f"Sending CONTROL_CHANGE: ch={chan+1:02}, cc={cc:03}, val={val:03}")
                    midiout.send_message([CONTROL_CHANGE | chan, cc, val])
                    time.sleep(args.delay)
except (EOFError, KeyboardInterrupt):
    log.warning("Interrupted.")

log.debug("Done.")
