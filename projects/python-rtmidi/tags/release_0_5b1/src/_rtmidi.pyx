# -*- encoding: utf-8 -*-
#cython: embedsignature=True
#
# rtmidi.pyx
#
"""A Python wrapper for the RtMidi C++ library written with Cython.

Overview
========

**RtMidi** is a set of C++ classes which provides a concise and simple,
cross-platform API (Application Programming Interface) for realtime MIDI
input/output across Linux (ALSA & JACK), Macintosh OS X (CoreMIDI & JACK),
and Windows (Multimedia Library & Kernel Streaming) operating systems.

**python-rtmidi** is a Python binding for RtMidi implemented with Cython and
provides a thin wrapper around the RtMidi C++ interface. The API is basically
the same as the C++ one but with the naming scheme of classes, methods and
parameters adapted to the Python PEP-8 conventions and requirements of
the Python package naming structure. **python-rtmidi** supports Python 2
(tested with Python 2.7) and Python 3 (3.2, 3.3).


Public API
==========

See the docstrings of each function and class and their methods for more
information.

Functions
---------

``get_compiled_api``
    Return a list of low-level MIDI backend APIs this module supports.


Classes
-------

``MidiIn(rtapi=API_UNSPECIFIED, name="RtMidi Client", queue_size_limit=1024)``
    Midi input client interface.

``MidiOut(rtapi=API_UNSPECIFIED, name="RtMidi Client")``
    Midi output client interface.


Constants
---------

These constants are returned by the ``get_compiled_api`` function and the
``MidiIn.get_current_api`` resp. ``MidiOut.get_current_api`` methods and are
used to specify the low-level MIDI backend API to use when creating a
``MidiIn`` or `MidiOut`` instance.

``API_UNSPECIFIED``
    Use first compiled-in API, which has any input resp. output ports
``API_MACOSX_CORE``
    OS X CoreMIDI
``API_LINUX_ALSA``
    Linux ALSA
``API_UNIX_JACK``
    Jack Client
``API_WINDOWS_MM``
    Windows MultiMedia
``API_RTMIDI_DUMMY``
    RtMidi Dummy (used when no suitable API was found)


Usage example
=============

Here's a short example of how to use **python-rtmidi** to open the first
available MIDI output port and send a middle C note on MIDI channel 1::

    import time
    import rtmidi

    midiout = rtmidi.MidiOut()
    available_ports = midiout.get_ports()

    if available_ports:
        midiout.open_port(0)
    else:
        midiout.open_virtual_port("My virtual output")

    note_on = [0x90, 60, 112] # channel 1, middle C, velocity 112
    note_off = [0x80, 60, 0]
    midiout.send_message(note_on)
    time.sleep(0.5)
    midiout.send_message(note_off)

    del midiout

"""

__all__ = [
    'API_UNSPECIFIED', 'API_MACOSX_CORE', 'API_LINUX_ALSA', 'API_UNIX_JACK',
    'API_WINDOWS_MM', 'API_RTMIDI_DUMMY',
    'MidiIn', 'MidiOut', 'get_compiled_api'
]

import sys

from libcpp cimport bool
from libcpp.string cimport string
from libcpp.vector cimport vector


class RtMidiError(Exception):
    """Base general RtMidi error."""
    pass


cdef extern from "RtMidi.h":
    # Enums nested in classes are apparently not supported by Cython yet
    # therefore we need to use the following work-around.
    # https://groups.google.com/d/msg/cython-users/monwJxJCb-g/k_h1rcU-3TgJ
    cdef enum Api "RtMidi::Api":
        UNSPECIFIED  "RtMidi::UNSPECIFIED"
        MACOSX_CORE  "RtMidi::MACOSX_CORE"
        LINUX_ALSA   "RtMidi::LINUX_ALSA"
        UNIX_JACK    "RtMidi::UNIX_JACK"
        WINDOWS_MM   "RtMidi::WINDOWS_MM"
        RTMIDI_DUMMY "RtMidi::RTMIDI_DUMMY"

    # Another work-around for calling a C++ static method:
    cdef void RtMidi_getCompiledApi "RtMidi::getCompiledApi"(vector[Api] &apis)

    ctypedef void (*RtMidiCallback)(double timeStamp,
        vector[unsigned char] *message, void *userData)

    cdef cppclass RtMidiIn:
        Api RtMidiIn() except +
        Api RtMidiIn(Api rtapi, string clientName, unsigned int queueSizeLimit) except +
        void cancelCallback()
        void closePort()
        Api getCurrentApi()
        double getMessage(vector[unsigned char] *message)
        unsigned int getPortCount()
        string getPortName(unsigned int portNumber)
        void ignoreTypes(bool midiSysex, bool midiTime, bool midiSense)
        void openPort(unsigned int portNumber, string portName) except +
        void openVirtualPort(string portName) except +
        void setCallback(RtMidiCallback callback, void *data) except +

    cdef cppclass RtMidiOut:
        Api RtMidiOut() except +
        Api RtMidiOut(Api rtapi, string clientName) except +
        void closePort()
        Api getCurrentApi()
        unsigned int getPortCount()
        string getPortName(unsigned int portNumber)
        void openPort(unsigned int portNumber, string portName) except +
        void openVirtualPort(string portName) except +
        void sendMessage(vector[unsigned char] *message) except +


# export Api enum values to Python

API_UNSPECIFIED = UNSPECIFIED
API_MACOSX_CORE = MACOSX_CORE
API_LINUX_ALSA = LINUX_ALSA
API_UNIX_JACK = UNIX_JACK
API_WINDOWS_MM = WINDOWS_MM
API_RTMIDI_DUMMY = RTMIDI_DUMMY

# internal functions

cdef void _cb_func(double delta_time, vector[unsigned char] *msg_v,
        void *cb_info) with gil:
    """Wrapper for a Python callback function for MIDI input."""
    func, data = (<object> cb_info)
    message = [msg_v.at(i) for i in range(msg_v.size())]
    func((message, delta_time), data)

def _to_bytes(name):
    """Convert a unicode (Python 2) or str (Python 3) object into bytes."""

    # 'bytes' == 'str' in Python 2 but a separate type in Python 3
    if not isinstance(name, bytes):
        try:
            name = bytes(name, 'utf-8') # Python 3
        except TypeError:
            name = bytes(name.encode('utf-8')) # Python 2

    return name

# Public API

def get_compiled_api():
    """Return a list of low-level MIDI backend APIs this module supports.

    Check for support for a particular API by using the ``API_*`` constants in
    the module namespace, i.e.::

        if rtmidi.API_UNIX_JACK in rtmidi.get_compiled_api():
            ...

    """
    cdef vector[Api] api_v

    RtMidi_getCompiledApi(api_v)
    return [api_v[i] for i in range(api_v.size())]


cdef class MidiIn:
    """Midi input client interface.

    You can specify the low-level MIDI backend API to use via the ``rtapi``
    keyword or the first positional argument, passing one of the module-level
    ``API_*`` constants. You can get a list of compiled-in APIs with the
    module-level ``get_compiled_api`` function. If you pass ``API_UNSPECIFIED``
    (the default), the first compiled-in API, which has any input ports
    available, will be used.

    You can optionally pass a name for the MIDI client with the ``name``
    keyword or the second positional argument. Names with non-ASCII characters
    in  them have to be passed as unicode or utf-8 encoded strings in Python 2.
    The default name is ``"RtMidiIn Client"``.

    .. note::
        With some backend APIs (e.g. ALSA), the client name is set by the
        first ``MidiIn`` *or* ``MidiOut`` created by your program and does not
        change until *all* ``MidiIn`` and ``MidiOut`` instances are deleted and
        then a new one is created.

    The ``queue_size_limit`` argument specifies the size of the internal ring
    buffer in which incoming MIDI events are placed until retrieved via the
    ``get_message`` method (i.e. when no callback function is registered).
    The default value is ``1024`` (overriding the default value ``100`` of the
    underlying C++ RtMidi library).

    """
    cdef RtMidiIn *thisptr
    cdef object _callback
    cdef object _port

    def __cinit__(self, Api rtapi=UNSPECIFIED, name=None,
            unsigned int queue_size_limit=1024):
        """Create a new client instance for MIDI input.

        See the class docstring for a description of the constructor arguments.

        """
        self.thisptr = new RtMidiIn(rtapi, _to_bytes(name or "RtMidiIn Client"),
            queue_size_limit)
        self._callback = None
        self._port = None

    def __dealloc__(self):
        del self.thisptr

    # context management
    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close_port()

    def get_current_api(self):
        """Return the low-level MIDI backend API used by this instance.

        Use this by comparing the returned value to the module-level ``API_*``
        constants, e.g.::

            midiin = rtmidi.MidiIn()

            if midiin.get_current_api() == rtmidi.API_UNIX_JACK:
                print("Using JACK API for MIDI input.")

        """
        return self.thisptr.getCurrentApi()

    def get_port_count(self):
        """Return the number of available MIDI input ports."""

        return self.thisptr.getPortCount()

    def get_port_name(self, unsigned int port, encoding='auto'):
        """Return the name of the MIDI input port with the given number.

        Ports are numbered from zero, separately for input and output ports.
        The number of available ports is returned by the ``get_port_count``
        method.

        The port name is decoded to a (unicode) string with the encoding given
        by ``encoding``. If ``encoding`` is ``"auto"`` (the default) then an
        appropriate encoding is chosen based on the system and the used
        backend API. If ``encoding`` is ``None``, the names are returned
        un-decoded, i.e. as type ``str`` in Python 2 or ``bytes`` in Python 3.

        """
        cdef string name = self.thisptr.getPortName(port)

        if len(name):
            if encoding:
                if encoding == 'auto':
                    if sys.platform.startswith('win'):
                        encoding = 'latin1'
                    elif (self.get_current_api() == API_MACOSX_CORE and
                            sys.platform == 'darwin'):
                        encoding = 'macroman'
                    else:
                        encoding = 'utf-8'
                return name.decode(encoding, "ignore")
            else:
                return name
        else:
            return None

    def get_ports(self, encoding='auto'):
        """Return a list of names of available MIDI input ports.

        The list index of each port name corresponds to its port number.

        The port names are decoded to (unicode) strings with the encoding given
        by ``encoding``. If ``encoding`` is ``"auto"`` (the default) then an
        appropriate encoding is chosen based on the system and the used
        backend API. If ``encoding`` is ``None``, the names are returned
        un-decoded, i.e. as type ``str`` in Python 2 or ``bytes`` in Python 3.

        """
        return [self.get_port_name(p, encoding=encoding)
            for p in range(self.get_port_count())]

    def open_port(self, unsigned int port=0, name=None):
        """Open the MIDI input port with the given port number.

        Only one port can be opened per ``MidiIn`` instance. An ``RtMidiError``
        exception is raised if an attempt is made to open a port on a
        ``MidiIn`` instance, which already opened a (virtual) port.

        You can optionally pass a name for the RtMidi input port with the
        ``name`` keyword or the second positional argument. Names with
        non-ASCII characters in them have to be passed as unicode or utf-8
        encoded strings in Python 2. The default name is "RtMidi Input".

        _ note::
            Closing a port and opening it again with a different name does
            not change the port name. To change the input port name, drop its
            ``MidiIn`` instance, create a new one and open the port again
            giving a different name.

        """
        if self._port == -1:
            raise RtMidiError("%r already opened virtual input port." % self)
        elif self._port is not None:
            raise RtMidiError(
                "%r already opened input port %i." % (self, self._port))

        self.thisptr.openPort(port, _to_bytes(name or "RtMidi Input"))
        self._port = port
        return self

    def open_virtual_port(self, name=None):
        """Open a virtual MIDI input port.

        Only one port can be opened per ``MidiIn`` instance. An ``RtMidiError``
        exception is raised if an attempt is made to open a port on a
        ``MidiIn`` instance, which already opened a (virtual) port.

        A virtual port is not connected to a physical MIDI device or system
        port when fist opened. You can connect it to another MIDI output with
        the OS-dependant tools provided the low-level MIDI framework, e.g.
        ``aconnect`` for ALSA, ``jack_connect`` for JACK, or the Audio & MIDI
        settings dialog for CoreMIDI.

        .. note::
            Virtual ports are not supported by some backend APIs, namely the
            Windows MultiMedia API. You can use special MIDI drivers like
            `MIDI Yoke`_ or loopMIDI_ to provide hardware-independent virtual
            MIDI ports as an alternative.

        You can optionally pass a name for the virtual input port with the
        ``name`` keyword or second positional argument. Names with non-ASCII
        characters in them have to be passed as unicode or utf-8 encoded
        strings in Python 2. The default name is "RtMidi Virtual Input".

        To change the virtual input port name, drop its ``MidiIn`` instance,
        create a new one and open a virtual port again giving a different name.

        Also, to close a virtual input port, you have to delete its ``MidiIn``
        instance.

        Exceptions:

        ``NotImplementedError``
            Raised when trying to open a virtual MIDI port with the Windows
            MultiMedia API, which doesn't support virtual ports.

        .. _midi yoke: http://www.midiox.com/myoke.htm
        .. _loopmidi: http://www.tobias-erichsen.de/software/loopmidi.html

        """
        if self.get_current_api() == API_WINDOWS_MM:
            raise NotImplementedError("Virtual ports are not supported "
                "by the Windows MultiMedia API.")

        if self._port == -1:
            raise RtMidiError("%r already opened virtual input port." % self)
        elif self._port is not None:
            raise RtMidiError(
                "%r already opened input port %i." % (self, self._port))

        self.thisptr.openVirtualPort(
            _to_bytes(name or "RtMidi Virtual Input"))
        self._port = -1
        return self

    def close_port(self):
        """Close the MIDI input port opened via ``open_port``.

        It is safe to call this method repeatedly or if no input port has been
        opened (yet).

        Also cancels a callback function set with ``set_callback``.

        To close a virtual input port opened via ``open_virtual_port``, you
        have to delete its ``MidiIn`` instance.

        """
        if self._port != -1:
            self._port = None
        self.cancel_callback()
        self.thisptr.closePort()

    def ignore_types(self, sysex=True, timing=True, active_sense=True):
        """Enable/Disable input filtering of certain types of MIDI events.

        By default System Exclusive (aka sysex), MIDI Clock and Active Sensing
        messages are filtered from the MIDI input and never reach your code,
        because they can fill up input buffers very quickly.

        To receive them, you can selectively disable the filtering of these
        event types.

        To enable reception, i.e. disable the default filtering of sysex
        messages, pass ``sysex = False``.

        To enable reception of MIDI Clock, pass ``timing = False``.

        To enable reception of Active Sensing, pass ``active_sensing = False``.

        These arguments can of course be combined in one call, and they all
        default to ``True``.

        If you enable reception of any of these event types, be sure to either
        use an input callback function, which returns quickly or poll for MIDI
        input often. Otherwise you might lose MIDI input because the input
        buffer overflows.

        *Windows note:* the Windows Multi Media API uses fixed size buffers for
        the reception of sysex messages, whose number and size is set at
        compile time. Sysex messages longer than the buffer size can not be
        received properly when using the Windows Multi Media API.

        The default distribution of python-rtmidi sets the number of sysex
        buffers to four and the size of each to 8192 bytes. To change these
        values, edit the ``RT_SYSEX_BUFFER_COUNT`` and ``RT_SYSEX_BUFFER_SIZE``
        preprocessor defines in ``RtMidi.cpp`` and recompile.

        """
        self.thisptr.ignoreTypes(sysex, timing, active_sense)

    def get_message(self):
        """Poll for MIDI input.

        Checks whether a MIDI event is available in the input buffer and
        returns a two-element tuple with the MIDI message and a delta time.
        The MIDI message is a list of integers representing the data bytes of
        the message, the delta time is a float representing the time in seconds
        elapsed since the reception of the previous MIDI event.

        The function does not block. When no MIDI message is available, it
        returns ``None``.

        """
        cdef vector[unsigned char] msg_v
        cdef double delta_time = self.thisptr.getMessage(&msg_v)

        if not msg_v.empty():
            message = [msg_v.at(i) for i in range(msg_v.size())]
            return (message, delta_time)
        else:
            return None

    def set_callback(self, func, data=None):
        """Register a callback function for MIDI input.

        The callback function is called whenever a MIDI message is received
        and must take two arguments. The first argument is a two-element tuple
        with the MIDI message and a delta time, like the one returned by the
        ``get_message`` method and the second argument is value of the ``data``
        argument passed to this function when the callback is registered.

        Registering a callback function replaces any previously registered
        callbacḱ.

        The callback function is safely removed when the input port is closed
        or the ``MidiIn`` instance is deleted.

        """
        if self._callback:
            self.cancel_callback()
        self._callback = (func, data)
        self.thisptr.setCallback(&_cb_func, <void *>self._callback)

    def cancel_callback(self):
        """Remove the registered callback function for MIDI input.

        This can be safely called even when no callback function has been
        registered.

        """
        if self._callback:
            self.thisptr.cancelCallback()
            self._callback = None


cdef class MidiOut:
    """Midi output client interface.

    You can specify the low-level MIDI backend API to use via the ``rtapi``
    keyword or the first positional argument, passing one of the module-level
    ``API_*`` constants. You can get a list of compiled-in APIs with the
    module-level ``get_compiled_api`` function. If you pass ``API_UNSPECIFIED``
    (the default), the first compiled-in API, which has any input ports
    available, will be used.

    You can optionally pass a name for the MIDI client with the ``name``
    keyword or the second positional argument. Names with non-ASCII characters
    in them have to be passed as unicode or utf-8 encoded strings in Python 2.
    The default name is ``"RtMidiOut Client"``.

    .. note::
        With some APIs (e.g. ALSA), the client name is set by the first
        ``MidiIn`` *or* ``MidiOut`` created by your program and does not change
        until *all* ``MidiIn`` and ``MidiOut`` instances are deleted and then
        a new one is created.

    """
    cdef RtMidiOut *thisptr
    cdef object _port

    def __cinit__(self, Api rtapi=UNSPECIFIED, name=None):
        """Create a new client instance for MIDI output.

        See the class docstring for a description of the constructor arguments.

        """
        self.thisptr = new RtMidiOut(rtapi, _to_bytes(name or "RtMidiOut Client"))
        self._port = None

    def __dealloc__(self):
        del self.thisptr

    # context management
    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close_port()

    def get_current_api(self):
        """Return the low-level MIDI backend API used by this instance.

        Use this by comparing the returned value to the module-level ``API_*``
        constants, e.g.::

            midiout = rtmidi.MidiOut()

            if midiout.get_current_api() == rtmidi.API_UNIX_JACK:
                print("Using JACK API for MIDI output.")

        """
        return self.thisptr.getCurrentApi()

    def get_port_count(self):
        """Return the number of available MIDI output ports."""

        return self.thisptr.getPortCount()

    def get_port_name(self, unsigned int port, encoding='auto'):
        """Return the name of the MIDI output port with the given number.

        Ports are numbered from zero, separately for input and output ports.
        The number of available ports is returned by the ``get_port_count``
        method.

        The port name is decoded to a (unicode) string with the encoding given
        by ``encoding``. If ``encoding`` is ``"auto"`` (the default) then an
        appropriate encoding is chosen based on the system and the used
        backend API. If ``encoding`` is ``None``, the names are returned
        un-decoded, i.e. as type ``str`` in Python 2 or ``bytes`` in Python 3.

        """
        cdef string name = self.thisptr.getPortName(port)

        if len(name):
            if encoding:
                if encoding == 'auto':
                    if sys.platform.startswith('win'):
                        encoding = 'latin1'
                    elif (self.get_current_api() == API_MACOSX_CORE and
                            sys.platform == 'darwin'):
                        encoding = 'macroman'
                    else:
                        encoding = 'utf-8'
                return name.decode(encoding, "ignore")
            else:
                return name
        else:
            return None

    def get_ports(self, encoding='auto'):
        """Return a list of names of available MIDI output ports.

        The list index of each port name corresponds to its port number.

        The port names are decoded to (unicode) strings with the encoding given
        by ``encoding``. If ``encoding`` is ``"auto"`` (the default) then an
        appropriate encoding is chosen based on the system and the used
        backend API. If ``encoding`` is ``None``, the names are returned
        un-decoded, i.e. as type ``str`` in Python 2 or ``bytes`` in Python 3.

        """
        return [self.get_port_name(p, encoding=encoding)
            for p in range(self.get_port_count())]

    def open_port(self, unsigned int port=0, name=None):
        """Open the MIDI output port with the given port number.

        Only one port can be opened per ``MidiOut`` instance. An
        ``RtMidiError`` exception is raised if an attempt is made to open a
        port on a ``MidiOut`` instance, which already opened a (virtual) port.

        You can optionally pass a name for the RtMidi output port with the
        ``name`` keyword or the second positional argument. Names with
        non-ASCII characters in them have to be passed as unicode or utf-8
        encoded strings in Python 2. The default name is "RtMidi Output".

        Note: Closing a port and opening it again with a different name does
        not change the port name. To change the output port name, drop its
        ``MidiOut`` instance, create a new one and open the port again giving
        a different name.

        """
        if self._port == -1:
            raise RtMidiError("%r already opened virtual output port." % self)
        elif self._port is not None:
            raise RtMidiError(
                "%r already opened output port %i." % (self, self._port))

        self.thisptr.openPort(port, _to_bytes(name or "RtMidi Output"))
        self._port = port
        return self

    def open_virtual_port(self, name=None):
        """Open a virtual MIDI output port.

        A virtual port is not connected to a physical MIDI device or system
        port when fist opened. You can connect it to another MIDI input with
        the OS-dependant tools provided the low-level MIDI framework, e.g.
        ``aconnect`` for ALSA, ``jack_connect`` for JACK, or the Audio & MIDI
        settings dialog for CoreMIDI.

        Only one port can be opened per ``MidiOut`` instance. An
        ``RtMidiError`` exception is raised if an attempt is made to open a
        port on a ``MidiOut`` instance, which already opened a (virtual) port.

        .. note::
            Virtual ports are not supported by some backend APIs, namely the
            Windows MultiMedia API. You can use special MIDI drivers like
            `MIDI Yoke`_ or loopMIDI_ to provide hardware-independent virtual
            MIDI ports as an alternative.

        You can optionally pass a name for the virtual output port with the
        ``name`` keyword or second positional argument. Names with non-ASCII
        characters in them have to be passed as unicode or utf-8 encoded
        strings in Python 2. The default name is "RtMidi Virtual Output".

        To change the virtual output port name, drop its ``MidiOut`` instance,
        create a new one and open a virtual port again giving a different name.

        Also, to close a virtual output port, you have to delete its ``MidiOut``
        instance.

        Exceptions:

        ``NotImplementedError``
            Raised when trying to open a virtual MIDI port with the
            Windows MultiMedia API, which doesn't support this.

        .. _midi yoke: http://www.midiox.com/myoke.htm
        .. _loopmidi: http://www.tobias-erichsen.de/software/loopmidi.html

        """
        if self.get_current_api() == API_WINDOWS_MM:
            raise NotImplementedError("Virtual ports are not supported "
                "by the Windows MultiMedia API.")

        if self._port == -1:
            raise RtMidiError("%r already opened virtual output port." % self)
        elif self._port is not None:
            raise RtMidiError(
                "%r already opened output port %i." % (self, self._port))

        self.thisptr.openVirtualPort(
            _to_bytes(name or "RtMidi Virtual Output"))
        self._port = -1
        return self

    def close_port(self):
        """Close the output port opened via ``open_port``.

        It is safe to call this method repeatedly or if no output port has been
        opened (yet).

        To close a virtual output port opened via ``open_virtual_port``, you
        have to delete its ``MidiOut`` instance.

        """
        if self._port != -1:
            self._port = None
        self.thisptr.closePort()

    def send_message(self, message):
        """Send a MIDI message to the output port.

        The message must be passed as an iterable of integers, each element
        representing one byte of the MIDI message.

        Normal MIDI messages have a length of one to three bytes, but you can
        also send system exclusive messages, which can be arbitrarily long,
        via this method.

        No check is made whether the passed data constitutes a valid MIDI
        message.

        """
        cdef vector[unsigned char] msg_v

        for c in message:
            msg_v.push_back(c)

        self.thisptr.sendMessage(&msg_v)