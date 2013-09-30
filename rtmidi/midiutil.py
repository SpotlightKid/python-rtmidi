# -*- coding: utf-8 -*-
#
# util.py
#

__all__ = [
    'open_midiport'
]

import logging
import sys

try:
    raw_input
except NameError:
    # Python 3
    raw_input = input


import rtmidi

log = logging.getLogger(__name__)


def open_midiport(port, type_="input"):
    log.debug("Creating MidiIn object.")
    midiobj = rtmidi.MidiIn() if type_ == "input" else rtmidi.MidiOut()
    type_ = "input" if isinstance(midiobj, rtmidi.MidiIn) else "ouput"

    ports = midiobj.get_ports(encoding='latin1'
        if sys.platform.startswith('win') else 'utf-8')
    use_virtual = False

    if port is None:
        try:
            r = raw_input(
                "Do you want to create a virtual MIDI %s port? (y/N) " % type_)

            if r.strip().lower() in ['y', 'yes']:
                use_virtual = True
                port_name = "Virtual MIDI Input"
                log.info("Opening virtual MIDI %s port.", type_)
                midiobj.open_virtual_port()
        except (KeyboardInterrupt, EOFError):
            del midiobj
            print('')
            sys.exit()

    if not use_virtual:
        if not ports:
            del midiobj
            raise IOError("No MIDI %s ports found." % type_)
        elif port is None or (port < 0 or port >= len(ports)):
            print("Available MIDI %s ports:\n" % type_)

            for portno, name in enumerate(ports):
                print("[%i] %s" % (portno, name))

            print('')

            while port is None:
                try:
                    r = raw_input("Select MIDI %s port (Control-C to exit): "
                        % type_)
                    port = int(r)

                    if port < 0 or port >= len(ports):
                        print("Invalid port number: %i" % port)
                        port = None
                except (KeyboardInterrupt, EOFError):
                    del midiobj
                    print('')
                    sys.exit()
                except (ValueError, TypeError):
                    port = None

        port_name = ports[port]

        log.info("Opening MIDI %s port #%i (%s)." % (type_, port, port_name))
        midiobj.open_port(port)

    return midiobj, port_name
