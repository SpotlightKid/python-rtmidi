# -*- coding: utf-8 -*-
#
# util.py
#
"""Collection of utility functions for handling MIDI I/O and ports.

Currently only contains one public function, ``open_midiport``.

"""

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
    """Prompt on the console whether a virtual MIDI port should be opened."""

    return raw_input("Do you want to create a virtual MIDI %s port? (y/N) "
        % type_).strip().lower() in ['y', 'yes']


def open_midiport(port=None, type_="input", api=rtmidi.API_UNSPECIFIED,
        use_virtual=False, interactive=True, client_name=None,
        port_name=None):
    """Open MIDI port for input or output and return MidiIn/MidiOut instance.

    Arguments:

    ``port``
        A MIDI port number or (substring of) a port name or ``None``.

        Available ports are enumerated starting from zero separately for input
        and output ports. If only a substring of a port name is given, the
        first matching port is used.

    ``type_``
        Must be ``"input"`` or ``"output"``. Determines whether a ``MidiIn``
        or ``MidiOut`` instance will be created and returned.

    ``api``
        Select the low-level MIDI API to use. Defaults to ``API_UNSPECIFIED``,
        i.e. the first compiled-in API, which has any input resp. output ports
        available, will be used.

    ``use_virtual``
        If ``port is ``None``, should a virtual MIDI port be opened? Defaults
        to ``False``.

    ``interactive``
        If port is ``None`` or no MIDI port matching the port number or name is
        available, should the user be prompted on the console whether to open
        a virtual MIDI port (if ``use_virtual`` is ``True``) and/or with a list
        of available MIDI ports and the option to choose one? Defaults to
        `` True``.

    ``client_name``
        The name of the MIDI client passed when instantiating a `MidiIn`` or
        ``MidiOut`` object.

        See the documentation of the constructor for these classes for the
        default values and caveats and OS-dependant ideosyncracies regarding
        the name.

    ``port_name``
        The name of the MIDI port passed to the ``open_port`` or
        ``open_virtual_port`` method of the new ``MidiIn`` or ``MidiOut``
        instance.

        See the documentation of the ``open_port`` resp. ``open_virtual_port``
        methods for the default values and caveats when wanting to change the
        port name afterwards.

    Returns:

    A two-element tuple of a new ``MidiIn`` or ``MidiOut`` instance and the
    name of the MIDI port which was opened.

    Exceptions:

    ``KeyboardInterrupt, EOFError``
        Raised when the user presses Control-C or Control-D during a console
        prompt.

    ``IOError``
        Raised when no MIDI input or output ports (depending on what was
        requested) are available.

    ``ValueError``
        Raised when an invalid port number or name is passed and
        ``interactive`` is ``False``.

    """
    midiclass_ = rtmidi.MidiIn if type_ == "input" else rtmidi.MidiOut
    log.debug("Creating %s object.", midiclass_.__name__)
    midiobj = midiclass_(api, name=client_name)
    type_ = "input" if isinstance(midiobj, rtmidi.MidiIn) else "output"

    ports = midiobj.get_ports()

    if port is None:
        try:
            if (midiobj.get_current_api() != rtmidi.API_WINDOWS_MM and
                    (use_virtual or
                    (interactive and _prompt_for_virtual(type_)))):
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

    if port is not None and (port >= 0 and port < len(ports)):
        if not port_name:
            port_name = ports[port]

        log.info("Opening MIDI %s port #%i (%s)." % (type_, port, port_name))
        midiobj.open_port(port, port_name)
        return midiobj, port_name
    else:
        raise ValueError("Invalid port.")
