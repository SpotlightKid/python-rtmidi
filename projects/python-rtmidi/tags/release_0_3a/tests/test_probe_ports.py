#!/usr/bin/env python
#
# test_probe_ports.py
#
"""Shows how to probe for available MIDI input and output ports."""

import sys

from rtmidi import *

try:
    raw_input
except NameError:
    # Python 3
    raw_input = input

apis = {
  API_MACOSX_CORE:  "OS X CoreMIDI",
  API_LINUX_ALSA:   "Linux ALSA",
  API_UNIX_JACK:    "Jack Client",
  API_WINDOWS_MM:   "Windows MultiMedia",
  API_WINDOWS_KS:   "Windows Kernel Streaming",
  API_RTMIDI_DUMMY: "RtMidi Dummy"
}

available_apis = get_compiled_api()

for api, desc in sorted(apis.items()):
    if api in available_apis:
        try:
            r = raw_input("Probe ports using the %s API? (Y/n) " % desc).strip()
            if r and r.lower() != "y":
                continue
        except (KeyboardInterrupt, EOFError):
            print('')
            break

        for name, class_ in (("input", MidiIn), ("output", MidiOut)):
            try:
                midi = class_(api)
                ports = midi.get_ports(encoding='latin1'
                    if sys.platform.startswith('win') else 'utf-8')
            except RuntimeError as exc:
                print("Could not probe MIDI %s ports: %s" % (name, exc))
                continue

            if not ports:
                print("No MIDI %s ports found." % name)
            else:
                print("Available MIDI %s ports:\n" % name)

                for port, name in enumerate(ports):
                    print("[%i] %s" % (port, name))

            print('')
            del midi
