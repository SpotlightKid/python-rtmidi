#!/usr/bin/env python
#
# probe_ports.py
#
"""Shows how to probe for available MIDI input and output ports."""

from rtmidi import (API_LINUX_ALSA, API_MACOSX_CORE, API_RTMIDI_DUMMY,
                    API_UNIX_JACK, API_WINDOWS_MM, MidiIn, MidiOut,
                    get_compiled_api)

try:
    input = raw_input
except NameError:
    # Python 3
    StandardError = Exception

apis = {
    API_MACOSX_CORE: "macOS (OS X) CoreMIDI",
    API_LINUX_ALSA: "Linux ALSA",
    API_UNIX_JACK: "Jack Client",
    API_WINDOWS_MM: "Windows MultiMedia",
    API_RTMIDI_DUMMY: "RtMidi Dummy"
}

available_apis = get_compiled_api()

for api, api_name in sorted(apis.items()):
    if api in available_apis:
        try:
            reply = input("Probe ports using the %s API? (Y/n) " % api_name)
            if reply.strip().lower() not in ['', 'y', 'yes']:
                continue
        except (KeyboardInterrupt, EOFError):
            print('')
            break

        for name, class_ in (("input", MidiIn), ("output", MidiOut)):
            try:
                midi = class_(api)
                ports = midi.get_ports()
            except StandardError as exc:
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
