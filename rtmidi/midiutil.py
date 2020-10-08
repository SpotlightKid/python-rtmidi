# -*- coding: utf-8 -*-
#
# midiutil.py
#
"""Collection of utility functions for handling MIDI I/O and ports.

Currently contains functions to list MIDI input/output ports, to get the RtMidi
API to use from the environment and to open MIDI ports.

"""

from __future__ import print_function, unicode_literals

import logging
import os

try:
    raw_input
except NameError:
    # Python 3
    raw_input = input
    basestring = str

import rtmidi


__all__ = (
    'get_api_from_environment',
    'list_available_ports',
    'list_input_ports',
    'list_output_ports',
    'open_midiinput',
    'open_midioutput',
    'open_midiport',
)

log = logging.getLogger(__name__)


def _prompt_for_virtual(type_):
    """Prompt on the console whether a virtual MIDI port should be opened."""
    return raw_input("Do you want to create a virtual MIDI %s port? (y/N) " %
                     type_).strip().lower() in ['y', 'yes']


def get_api_from_environment(api=rtmidi.API_UNSPECIFIED):
    """Return RtMidi API specified in the environment if any.

    If the optional api argument is ``rtmidi.API_UNSPECIFIED`` (the default),
    look in the environment variable ``RTMIDI_API`` for the name of the RtMidi
    API to use. Valid names are ``LINUX_ALSA``, ``UNIX_JACK``, ``MACOSX_CORE``,
    ``WINDOWS_MM`` and ``RTMIDI_DUMMY``. If no valid value is found,
    ``rtmidi.API_UNSPECIFIED`` will be used.

    Returns a ``rtmidi.API_*`` constant.

    """
    if api == rtmidi.API_UNSPECIFIED and 'RTMIDI_API' in os.environ:
        try:
            api_name = os.environ['RTMIDI_API'].upper()
            api = getattr(rtmidi, 'API_' + api_name)
        except AttributeError:
            log.warning("Ignoring unknown API '%s' in environment variable "
                        "RTMIDI_API." % api_name)

    return api


def list_available_ports(ports=None, midiio=None):
    """List MIDI ports given or available on given MIDI I/O instance."""
    if ports is None:
        ports = midiio.get_ports()
        type_ = " input" if isinstance(midiio, rtmidi.MidiIn) else " ouput"
    else:
        type_ = ''

    if ports:
        print("Available MIDI{} ports:\n".format(type_))

        for portno, name in enumerate(ports):
            print("[{}] {}".format(portno, name))
    else:
        print("No MIDI{} ports found.".format(type_))

    print()


def list_input_ports(api=rtmidi.API_UNSPECIFIED):
    """List available MIDI input ports.

    Optionally the RtMidi API can be passed with the ``api`` argument. If not
    it will be determined via the ``get_api_from_environment`` function.

    Exceptions:

    ``rtmidi.SystemError``
        Raised when RtMidi backend initialization fails.

    """
    midiin = rtmidi.MidiIn(get_api_from_environment(api))
    list_available_ports(midiio=midiin)


def list_output_ports(api=rtmidi.API_UNSPECIFIED):
    """List available MIDI output ports.

    Optionally the RtMidi API can be passed with the ``api`` argument. If not
    it will be determined via the ``get_api_from_environment`` function.

    Exceptions:

    ``rtmidi.SystemError``
        Raised when RtMidi backend initialization fails.

    """
    midiout = rtmidi.MidiOut(get_api_from_environment(api))
    list_available_ports(midiio=midiout)


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
        The specified api will be passed to the ``get_api_from_environment``
        function and its return value will be used. If it's ``API_UNSPECIFIED``
        the first compiled-in API, which has any input resp. output ports
        available, will be used.

    ``use_virtual``
        If ``port`` is ``None``, should a virtual MIDI port be opened? Defaults
        to ``False``.

    ``interactive``
        If ``port`` is ``None`` or no MIDI port matching the port number or
        name is available, should the user be prompted on the console whether
        to open a virtual MIDI port (if ``use_virtual`` is ``True``) and/or
        with a list of available MIDI ports and the option to choose one?
        Defaults to ``True``.

    ``client_name``
        The name of the MIDI client passed when instantiating a ``MidiIn`` or
        ``MidiOut`` object.

        See the documentation of the constructor for these classes for the
        default values and caveats and OS-dependent ideosyncracies regarding
        the client name.

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

    ``rtmidi.SystemError``
        Raised when RtMidi backend initialization fails.

    ``rtmidi.NoDevicesError``
        Raised when no MIDI input or output ports (depending on what was
        requested) are available.

    ``rtmidi.InvalidPortError``
        Raised when an invalid port number or name is passed and
        ``interactive`` is ``False``.

    """
    midiclass_ = rtmidi.MidiIn if type_ == "input" else rtmidi.MidiOut
    log.debug("Creating %s object.", midiclass_.__name__)

    api = get_api_from_environment(api)

    midiobj = midiclass_(api, name=client_name)
    type_ = "input" if isinstance(midiobj, rtmidi.MidiIn) else "output"

    ports = midiobj.get_ports()

    if port is None:
        try:
            if (midiobj.get_current_api() != rtmidi.API_WINDOWS_MM and
                    (use_virtual or (interactive and _prompt_for_virtual(type_)))):
                if not port_name:
                    port_name = "Virtual MIDI %s" % type_

                log.info("Opening virtual MIDI %s port.", type_)
                midiobj.open_virtual_port(port_name)
                return midiobj, port_name
        except (KeyboardInterrupt, EOFError):
            del midiobj
            print('')
            raise

    if len(ports) == 0:
        del midiobj
        raise rtmidi.NoDevicesError("No MIDI %s ports found." % type_)

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
        list_available_ports(ports)

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
        raise rtmidi.InvalidPortError("Invalid port.")


def open_midiinput(port=None, api=rtmidi.API_UNSPECIFIED, use_virtual=False,
                   interactive=True, client_name=None, port_name=None):
    """Open a MIDI port for input and return a MidiIn instance.

    See the ``open_midiport`` function for information on parameters and
    possible exceptions.

    """
    return open_midiport(port, "input", api, use_virtual, interactive,
                         client_name, port_name)


def open_midioutput(port=None, api=rtmidi.API_UNSPECIFIED, use_virtual=False,
                    interactive=True, client_name=None, port_name=None):
    """Open a MIDI port for output and return a MidiOut instance.

    See the ``open_midiport`` function for information on parameters and
    possible exceptions.

    """
    return open_midiport(port, "output", api, use_virtual, interactive,
                         client_name, port_name)
