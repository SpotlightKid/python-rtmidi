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
    basestring = str

import rtmidi

log = logging.getLogger(__name__)

def _prompt_for_virtual(type_):
    return raw_input("Do you want to create a virtual MIDI %s port? (y/N) "
        % type_).strip().lower() in ['y', 'yes']

def open_midiport(port=None, type_="input", use_virtual=False,
        interactive=True, client_name=None, port_name=None):
    log.debug("Creating MidiIn object.")
    midiobj = (rtmidi.MidiIn(name=client_name)
        if type_ == "input" else rtmidi.MidiOut(name=client_name))
    type_ = "input" if isinstance(midiobj, rtmidi.MidiIn) else "ouput"

    ports = midiobj.get_ports(encoding='latin1'
        if sys.platform.startswith('win') else 'utf-8')

    if port is None:
        try:
            if use_virtual or (interactive and _prompt_for_virtual(type_)):
                if not port_name:
                    port_name = "Virtual MIDI Input"
                log.info("Opening virtual MIDI %s port.", type_)
                midiobj.open_virtual_port(port_name)
                return midiobj, port_name
        except (KeyboardInterrupt, EOFError):
            del midiobj
            print('')
            raise

    if len(ports) == 0:
        del midiobj
        raise IOError("No MIDI %s ports found." % type_)

    try:
        port = int(port)
    except (TypeError, ValueError):
        if isinstance(port, basestring):
            portspec = port
            for portno, name in enumerate(ports):
                if portspec in name:
                    port = portno
                    break
            else:
                log.warning("No port matching '%s' found.", portspec)
                port = None

    while interactive and (port is None or (port < 0 or port >= len(ports))):
        print("Available MIDI %s ports:\n" % type_)

        for portno, name in enumerate(ports):
            print("[%i] %s" % (portno, name))

        print('')

        try:
            r = raw_input("Select MIDI %s port (Control-C to exit): " % type_)
            port = int(r)
        except (KeyboardInterrupt, EOFError):
            del midiobj
            print('')
            raise
        except (ValueError, TypeError):
            port = None

    if port is not None and (port > 0 and port <= len(ports)):
        if not port_name:
            port_name = ports[port]

        log.info("Opening MIDI %s port #%i (%s)." % (type_, port, port_name))
        midiobj.open_port(port, port_name)
        return midiobj, port_name
    else:
        raise ValueError("Invalid port.")
