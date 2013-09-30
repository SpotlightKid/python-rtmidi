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

def _prompt_for_virtual(type_):
    return raw_input("Do you want to create a virtual MIDI %s port? (y/N) "
        % type_).strip().lower() in ['y', 'yes']

def open_midiport(port=None, type_="input", use_virtual=False):
    log.debug("Creating MidiIn object.")
    midiobj = rtmidi.MidiIn() if type_ == "input" else rtmidi.MidiOut()
    type_ = "input" if isinstance(midiobj, rtmidi.MidiIn) else "ouput"

    ports = midiobj.get_ports(encoding='latin1'
        if sys.platform.startswith('win') else 'utf-8')

    if port is None:
        try:
            if use_virtual or _prompt_for_virtual(type_):
                port_name = "Virtual MIDI Input"
                log.info("Opening virtual MIDI %s port.", type_)
                midiobj.open_virtual_port()
                return midiobj, port_name
        except (KeyboardInterrupt, EOFError):
            del midiobj
            print('')
            sys.exit()

    if len(ports) == 0:
        del midiobj
        raise IOError("No MIDI %s ports found." % type_)

    while port is None or (port < 0 or port >= len(ports)):
        print("Available MIDI %s ports:\n" % type_)

        for portno, name in enumerate(ports):
            print("[%i] %s" % (portno, name))

        print('')

        try:
            r = raw_input("Select MIDI %s port (Control-C to exit): "
                % type_)
            port = int(r)
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
