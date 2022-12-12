# cython: embedsignature = True
# cython: language_level = 3
# distutils: language = c++
#
# rtmidi.pyx
#
"""A Python binding for the RtMidi C++ library implemented using Cython.

Overview
========

**RtMidi** is a set of C++ classes which provides a concise and simple,
cross-platform API (Application Programming Interface) for realtime MIDI
input / output across Linux (ALSA & JACK), macOS / OS X (CoreMIDI & JACK),
and Windows (MultiMedia System) operating systems.

**python-rtmidi** is a Python binding for RtMidi implemented using Cython_ and
provides a thin wrapper around the RtMidi C++ interface. The API is basically
the same as the C++ one but with the naming scheme of classes, methods and
parameters adapted to the Python PEP-8 conventions and requirements of the
Python package naming structure. **python-rtmidi** supports Python 3 (3.6, 3.7,
3.8, and 3.9).


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

    with midiout:
        note_on = [0x90, 60, 112] # channel 1, middle C, velocity 112
        note_off = [0x80, 60, 0]
        midiout.send_message(note_on)
        time.sleep(0.5)
        midiout.send_message(note_off)
        time.sleep(0.1)

    del midiout


Constants
=========


Low-level APIs
--------------

These constants are returned by the ``get_compiled_api`` function and the
``MidiIn.get_current_api`` resp. ``MidiOut.get_current_api`` methods and are
used to specify the low-level MIDI backend API to use when creating a
``MidiIn`` or ``MidiOut`` instance.

``API_UNSPECIFIED``
    Use first compiled-in API, which has any input resp. output ports
``API_MACOSX_CORE``
    macOS (OS X) CoreMIDI
``API_LINUX_ALSA``
    Linux ALSA
``API_UNIX_JACK``
    Jack Client
``API_WINDOWS_MM``
    Windows MultiMedia
``API_RTMIDI_DUMMY``
    RtMidi Dummy API (used when no suitable API was found)


Error types
-----------

These constants are passed as the first argument to an error handler
function registered with ``set_error_callback`` method of a ``MidiIn``
or ``MidiOut`` instance. For the meaning of each value, please see
the `RtMidi API reference`_.

* ``ERRORTYPE_DEBUG_WARNING``
* ``ERRORTYPE_DRIVER_ERROR``
* ``ERRORTYPE_INVALID_DEVICE``
* ``ERRORTYPE_INVALID_PARAMETER``
* ``ERRORTYPE_INVALID_USE``
* ``ERRORTYPE_MEMORY_ERROR``
* ``ERRORTYPE_NO_DEVICES_FOUND``
* ``ERRORTYPE_SYSTEM_ERROR``
* ``ERRORTYPE_THREAD_ERROR``
* ``ERRORTYPE_UNSPECIFIED``
* ``ERRORTYPE_WARNING``


.. _cython: http://cython.org/
.. _rtmidi api reference:
    http://www.music.mcgill.ca/~gary/rtmidi/classRtMidiError.html

"""

import sys
import warnings

from libcpp cimport bool
from libcpp.string cimport string
from libcpp.vector cimport vector


__all__ = (
    'API_UNSPECIFIED', 'API_MACOSX_CORE', 'API_LINUX_ALSA', 'API_UNIX_JACK',
    'API_WINDOWS_MM', 'API_RTMIDI_DUMMY', 'ERRORTYPE_DEBUG_WARNING',
    'ERRORTYPE_DRIVER_ERROR', 'ERRORTYPE_INVALID_DEVICE',
    'ERRORTYPE_INVALID_PARAMETER', 'ERRORTYPE_INVALID_USE',
    'ERRORTYPE_MEMORY_ERROR', 'ERRORTYPE_NO_DEVICES_FOUND',
    'ERRORTYPE_SYSTEM_ERROR', 'ERRORTYPE_THREAD_ERROR',
    'ERRORTYPE_UNSPECIFIED', 'ERRORTYPE_WARNING', 'InvalidPortError',
    'InvalidUseError', 'MemoryAllocationError', 'MidiIn', 'MidiOut',
    'NoDevicesError', 'RtMidiError', 'SystemError',
    'UnsupportedOperationError', 'get_api_display_name', 'get_api_name',
    'get_compiled_api', 'get_compiled_api_by_name', 'get_rtmidi_version'
)

if bytes is str:
    string_types = (str, unicode)
else:
    string_types = (str,)

cdef extern from "Python.h":
    void Py_Initialize()

Py_Initialize()

# Declarations for RtMidi C++ classes and their methods we use

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

    cdef enum ErrorType "RtMidiError::Type":
        ERR_WARNING           "RtMidiError::WARNING"
        ERR_DEBUG_WARNING     "RtMidiError::DEBUG_WARNING"
        ERR_UNSPECIFIED       "RtMidiError::UNSPECIFIED"
        ERR_NO_DEVICES_FOUND  "RtMidiError::NO_DEVICES_FOUND"
        ERR_INVALID_DEVICE    "RtMidiError::INVALID_DEVICE"
        ERR_MEMORY_ERROR      "RtMidiError::MEMORY_ERROR"
        ERR_INVALID_PARAMETER "RtMidiError::INVALID_PARAMETER"
        ERR_INVALID_USE       "RtMidiError::INVALID_USE"
        ERR_DRIVER_ERROR      "RtMidiError::DRIVER_ERROR"
        ERR_SYSTEM_ERROR      "RtMidiError::SYSTEM_ERROR"
        ERR_THREAD_ERROR      "RtMidiError::THREAD_ERROR"

    # Another work-around for calling C++ static methods:
    cdef string RtMidi_getApiDisplayName "RtMidi::getApiDisplayName"(Api rtapi)
    cdef string RtMidi_getApiName "RtMidi::getApiName"(Api rtapi)
    cdef void RtMidi_getCompiledApi "RtMidi::getCompiledApi"(vector[Api] &apis)
    cdef Api RtMidi_getCompiledApiByName "RtMidi::getCompiledApiByName"(string)
    cdef string RtMidi_getVersion "RtMidi::getVersion"()

    ctypedef void (*RtMidiCallback)(double timeStamp,
                                    vector[unsigned char] *message,
                                    void *userData)

    ctypedef void (*RtMidiErrorCallback)(ErrorType errorType,
                                         const string errorText,
                                         void *userData) except *

    cdef cppclass RtMidi:
        void closePort() except *
        unsigned int getPortCount() except *
        string getPortName(unsigned int portNumber) except *
        void openPort(unsigned int portNumber, string &portName) except *
        void openVirtualPort(string portName) except *
        void setClientName(string &clientName) except *
        void setErrorCallback(RtMidiErrorCallback callback, void *userData) except *
        void setPortName(string &portName) except *

    cdef cppclass RtMidiIn(RtMidi):
        Api RtMidiIn(Api rtapi, string clientName,
                     unsigned int queueSizeLimit) except +
        void cancelCallback() except *
        Api getCurrentApi()
        double getMessage(vector[unsigned char] *message) except *
        void ignoreTypes(bool midiSysex, bool midiTime, bool midiSense) except *
        void setCallback(RtMidiCallback callback, void *data) except *

    cdef cppclass RtMidiOut(RtMidi):
        Api RtMidiOut(Api rtapi, string clientName) except +
        Api getCurrentApi()
        void sendMessage(vector[unsigned char] *message) nogil except *


# internal functions

cdef void _cb_func(double delta_time, vector[unsigned char] *msg_v,
                   void *cb_info) with gil:
    """Wrapper for a Python callback function for MIDI input."""
    func, data = (<object> cb_info)
    message = [msg_v.at(i) for i in range(msg_v.size())]
    func((message, delta_time), data)


cdef void _cb_error_func(ErrorType errorType, const string &errorText,
                         void *cb_info) except * with gil:
    """Wrapper for a Python callback function for errors."""
    func, data, decoder = (<object> cb_info)
    func(errorType, decoder(errorText), data)


def _to_bytes(name):
    """Convert a unicode (Python 2) or str (Python 3) object into bytes."""
    # 'bytes' == 'str' in Python 2 but a separate type in Python 3
    if isinstance(name, string_types):
        try:
            name = bytes(name, 'utf-8')  # Python 3
        except TypeError:
            name = name.encode('utf-8')  # Python 2

    if not isinstance(name, bytes):
        raise TypeError("name must be bytes or (unicode) string.")

    return name


# Public API

# export Api enum values to Python

API_UNSPECIFIED = UNSPECIFIED
API_MACOSX_CORE = MACOSX_CORE
API_LINUX_ALSA = LINUX_ALSA
API_UNIX_JACK = UNIX_JACK
API_WINDOWS_MM = WINDOWS_MM
API_RTMIDI_DUMMY = RTMIDI_DUMMY

# export error values to Python

ERRORTYPE_WARNING = ERR_WARNING
ERRORTYPE_DEBUG_WARNING = ERR_DEBUG_WARNING
ERRORTYPE_UNSPECIFIED = ERR_UNSPECIFIED
ERRORTYPE_NO_DEVICES_FOUND = ERR_NO_DEVICES_FOUND
ERRORTYPE_INVALID_DEVICE = ERR_INVALID_DEVICE
ERRORTYPE_MEMORY_ERROR = ERR_MEMORY_ERROR
ERRORTYPE_INVALID_PARAMETER = ERR_INVALID_PARAMETER
ERRORTYPE_INVALID_USE = ERR_INVALID_USE
ERRORTYPE_DRIVER_ERROR = ERR_DRIVER_ERROR
ERRORTYPE_SYSTEM_ERROR = ERR_SYSTEM_ERROR
ERRORTYPE_THREAD_ERROR = ERR_THREAD_ERROR


# custom exceptions

class RtMidiError(Exception):
    """Base general RtMidi exception.

    All other exceptions in this module derive form this exception.

    Instances have a ``type`` attribute that maps to one of the
    ``ERRORTYPE_*`` constants.

    """
    type = ERR_UNSPECIFIED

    def __init__(self, msg, type=None):
        super().__init__(msg)
        self.type = self.type if type is None else type


class InvalidPortError(RtMidiError, ValueError):
    """Raised when an invalid port number is used.

    Also derives from ``ValueError``.

    """
    type = ERR_INVALID_PARAMETER


class InvalidUseError(RtMidiError, RuntimeError):
    """Raised when an method call is not allowed in the current state.

    Also derives from ``RuntimeError``.

    """
    type = ERR_INVALID_USE


class MemoryAllocationError(RtMidiError, MemoryError):
    """Raised if a memory allocation failed on the C++ level.

    Also derives from ``MemoryError``.

    """
    type = ERR_MEMORY_ERROR


class SystemError(RtMidiError, OSError):
    """Raised if an error happened at the MIDI driver or OS level.

    Also derives from ``OSError``.

    """
    pass


class NoDevicesError(SystemError):
    """Raised if no MIDI devices are found.

    Derives from ``rtmidi.SystemError``.

    """
    type = ERR_NO_DEVICES_FOUND


class UnsupportedOperationError(RtMidiError, RuntimeError):
    """Raised if a method is not supported by the low-level API.

    Also derives from ``RuntimeError``.

    """
    pass


# wrappers for RtMidi's static methods and classes

def get_api_display_name(api):
    """Return the display name of a specified MIDI API.

    This returns a long name used for display purposes.

    The ``api`` should be given as the one of ``API_*`` constants in the
    module namespace, e.g.::

        display_name = rtmidi.get_api_display_name(rtmidi.API_UNIX_JACK)

    If the API is unknown, this function will return the empty string.

    """
    return RtMidi_getApiDisplayName(api).decode('utf-8')


def get_api_name(api):
    """Return the name of a specified MIDI API.

    This returns a short lower-case name used for identification purposes.

    The ``api`` should be given as the one of ``API_*`` constants in the
    module namespace, e.g.::

        name = rtmidi.get_api_name(rtmidi.API_UNIX_JACK)

    If the API is unknown, this function will return the empty string.

    """
    return RtMidi_getApiName(api).decode('utf-8')


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


def get_compiled_api_by_name(name):
    """Return the compiled MIDI API having the given name.

    A case insensitive comparison will check the specified name against the
    list of compiled APIs, and return the one which matches. On failure, the
    function returns ``API_UNSPECIFIED``.

    """
    return RtMidi_getCompiledApiByName(_to_bytes(name))


def get_rtmidi_version():
    """Return the version string of the wrapped RtMidi library."""
    return RtMidi_getVersion().decode('utf-8')


def _default_error_handler(etype, msg, data=None):
    if etype == ERR_MEMORY_ERROR:
        raise MemoryAllocationError(msg)
    elif etype == ERR_INVALID_PARAMETER:
        raise InvalidPortError(msg)
    elif etype in (ERR_DRIVER_ERROR, ERR_SYSTEM_ERROR, ERR_THREAD_ERROR):
        raise SystemError(msg, type=etype)
    elif etype in (ERR_WARNING, ERR_DEBUG_WARNING):
        if 'portNumber' in msg and msg.endswith('is invalid.'):
            raise InvalidPortError(msg)
        elif msg.endswith('no ports available!'):
            raise InvalidPortError(msg)
        elif msg.endswith('error looking for port name!'):
            raise InvalidPortError(msg)
        elif msg.endswith('event parsing error!'):
            raise ValueError(msg)
        elif msg.endswith('error sending MIDI message to port.'):
            raise SystemError(msg, type=ERR_DRIVER_ERROR)
        elif msg.endswith('error sending MIDI to virtual destinations.'):
            raise SystemError(msg, type=ERR_DRIVER_ERROR)
        elif msg.endswith('JACK server not running?'):
            raise SystemError(msg, type=ERR_DRIVER_ERROR)
        else:
            warnings.warn(msg)
            return

    raise RtMidiError(msg, type=etype)


cdef class MidiBase:
    cdef object _port
    cdef object _error_callback
    cdef object _deleted

    cdef RtMidi* baseptr(self):
        return NULL

    # context management
    def __enter__(self):
        """Support context manager protocol.

        This means you can use ``MidiIn`` / ``MidiOut`` instances like this:

        :

            midiout = MidiIn()
            midiout.open_port(0)

            with midiout:
                midiout.send_message([...])

        and ``midiout.close_port()`` will be called automatically when exiting
        the ``with`` block.

        Since ``open_port()`` also returns the instance, you can even do:

        :

            midiout = MidiIn()

            with midiout.open_port(0):
                midiout.send_message([...])

        """
        return self

    def __exit__(self, *exc_info):
        """Support context manager protocol.

        This method is called when using a ``MidiIn`` / ``MidiOut`` instance as
        a context manager and closes open ports when exiting the ``with`` block.

        """
        self.close_port()

    def _check_port(self):
        inout = "input" if isinstance(self, MidiIn) else "output"
        if self._port == -1:
            raise InvalidUseError("%r already opened virtual %s port." %
                                  (self, inout))
        elif self._port is not None:
            raise InvalidUseError("%r already opened %s port %i." %
                                  (self, inout, self._port))
        return inout

    def _decode_string(self, s, encoding='auto'):
        """Decode given byte string with given encoding."""
        if encoding == 'auto':
            if sys.platform.startswith('win'):
                encoding = 'latin1'
            elif (self.get_current_api() == API_MACOSX_CORE and
                  sys.platform == 'darwin'):
                encoding = 'macroman'
            else:
                encoding = 'utf-8'

        return s.decode(encoding, "ignore")

    def get_port_count(self):
        """Return the number of available MIDI input or output ports."""
        return self.baseptr().getPortCount()

    def get_port_name(self, unsigned int port, encoding='auto'):
        """Return the name of the MIDI input or output port with given number.

        Ports are numbered from zero, separately for input and output ports.
        The number of available ports is returned by the ``get_port_count``
        method.

        The port name is decoded to a (unicode) string with the encoding given
        by ``encoding``. If ``encoding`` is ``"auto"`` (the default), then an
        appropriate encoding is chosen based on the system and the used backend
        API. If ``encoding`` is ``None``, the name is returned un-decoded, i.e.
        as type ``str`` in Python 2 or ``bytes`` in Python 3.

        """
        cdef string name = self.baseptr().getPortName(port)

        if len(name):
            return self._decode_string(name, encoding) if encoding else name

    def get_ports(self, encoding='auto'):
        """Return a list of names of available MIDI input or output ports.

        The list index of each port name corresponds to its port number.

        The port names are decoded to (unicode) strings with the encoding given
        by ``encoding``. If ``encoding`` is ``"auto"`` (the default), then an
        appropriate encoding is chosen based on the system and the used backend
        API. If ``encoding`` is ``None``, the names are returned un-decoded,
        i.e. as type ``str`` in Python 2 or ``bytes`` in Python 3.

        """
        return [self.get_port_name(p, encoding=encoding)
                for p in range(self.get_port_count())]

    def is_port_open(self):
        """Return ``True`` if a port has been opened and ``False`` if not.

        .. note::
            The ``isPortOpen`` method of the RtMidi C++ library does not
            return ``True`` when a virtual port has been openend. The
            python-rtmidi implementation, on the other hand, does.

        """
        return self._port is not None

    def open_port(self, unsigned int port=0, name=None):
        """Open the MIDI input or output port with the given port number.

        Only one port can be opened per ``MidiIn`` or ``MidiOut`` instance. An
        ``InvalidUseError`` exception is raised if an attempt is made to open a
        port on a ``MidiIn`` or ``MidiOut`` instance, which already opened a
        (virtual) port.

        You can optionally pass a name for the RtMidi port with the ``name``
        keyword or the second positional argument. Names with non-ASCII
        characters in them have to be passed as unicode or UTF-8 encoded
        strings in Python 2. The default name is "RtMidi input" resp. "RtMidi
        output".

        .. note::
            Closing a port and opening it again with a different name does not
            change the port name. To change the port name, use the
            ``set_port_name`` method where supported, or delete its instance,
            create a new one and open the port again giving a different name.

        Exceptions:

        ``InvalidPortError``
            Raised when an invalid port number is passed.
        ``InvalidUseError``
            Raised when trying to open a MIDI port when a (virtual) port has
            already been opened by this instance.
        ``TypeError``
            Raised when an incompatible value type is passed for the ``port``
            or ``name`` parameter.

        """
        inout = self._check_port()

        if name is None:
            name = "RtMidi %s" % inout

        self.baseptr().openPort(port, _to_bytes(name))
        self._port = port
        return self

    def open_virtual_port(self, name=None):
        """Open a virtual MIDI input or output port.

        Only one port can be opened per ``MidiIn`` or ``MidiOut`` instance. An
        ``InvalidUseError`` exception is raised if an attempt is made to open a
        port on a ``MidiIn`` or ``MidiOut`` instance, which already opened a
        (virtual) port.

        A virtual port is not connected to a physical MIDI device or system
        port when first opened. You can connect it to another MIDI output with
        the OS-dependent tools provided by the low-level MIDI framework, e.g.
        ``aconnect`` for ALSA, ``jack_connect`` for JACK, or the Audio & MIDI
        settings dialog for CoreMIDI.

        .. note::
            Virtual ports are not supported by some backend APIs, namely the
            Windows MultiMedia API. You can use special MIDI drivers like `MIDI
            Yoke`_ or loopMIDI_ to provide hardware-independent virtual MIDI
            ports as an alternative.

        You can optionally pass a name for the RtMidi port with the ``name``
        keyword or the second positional argument. Names with non-ASCII
        characters in them have to be passed as unicode or UTF-8 encoded
        strings in Python 2. The default name is "RtMidi virtual input" resp.
        "RtMidi virtual output".

        .. note::
            Closing a port and opening it again with a different name does not
            change the port name. To change the port name, use the
            ``set_port_name`` method where supported, or delete its instance,
            create a new one and open the port again giving a different name.

            Also, to close a virtual input port, you have to delete its
            ``MidiIn`` or ``MidiOut`` instance.

        Exceptions:

        ``InvalidUseError``
            Raised when trying to open a virtual port when a (virtual) port has
            already been opened by this instance.
        ``TypeError``
            Raised when an incompatible value type is passed for the ``name``
            parameter.
        ``UnsupportedOperationError``
            Raised when trying to open a virtual MIDI port with the Windows
            MultiMedia API, which doesn't support virtual ports.

        .. _midi yoke: http://www.midiox.com/myoke.htm
        .. _loopmidi: http://www.tobias-erichsen.de/software/loopmidi.html

        """
        if self.get_current_api() == API_WINDOWS_MM:
            raise NotImplementedError("Virtual ports are not supported "
                                      "by the Windows MultiMedia API.")

        inout = self._check_port()
        self.baseptr().openVirtualPort(_to_bytes(("RtMidi virtual %s" % inout)
                                                if name is None else name))
        self._port = -1
        return self

    def close_port(self):
        """Close the MIDI input or output port opened via ``open_port``.

        It is safe to call this method repeatedly or if no port has been opened
        (yet) by this instance.

        Also cancels a callback function set with ``set_callback``.

        To close a virtual port opened via ``open_virtual_port``, you have to
        delete its ``MidiIn`` or ``MidiOut`` instance.

        """
        if self._port != -1:
            self._port = None
        self.baseptr().closePort()

    def set_client_name(self, name):
        """Set the name of the MIDI client.

        Names with non-ASCII characters in them have to be passed as unicode
        or UTF-8 encoded strings in Python 2.

        Currently only supported by the ALSA API backend.

        Exceptions:

        ``TypeError``
            Raised when an incompatible value type is passed for the ``name``
            parameter.
        ``UnsupportedOperationError``
            Raised when trying the backend API does not support changing the
            client name.

        """
        if self.get_current_api() in (API_MACOSX_CORE, API_UNIX_JACK, API_WINDOWS_MM):
            raise NotImplementedError(
                "API backend does not support changing the client name.")

        self.baseptr().setClientName(_to_bytes(name))

    def set_port_name(self, name):
        """Set the name of the currently opened port.

        Names with non-ASCII characters in them have to be passed as unicode
        or UTF-8 encoded strings in Python 2.

        Currently only supported by the ALSA and JACK API backends.

        Exceptions:

        ``InvalidUseError``
            Raised when no port is currently opened.
        ``TypeError``
            Raised when an incompatible value type is passed for the ``name``
            parameter.
        ``UnsupportedOperationError``
            Raised when trying the backend API does not support changing the
            port name.

        """
        if self.get_current_api() in (API_MACOSX_CORE, API_WINDOWS_MM):
            raise UnsupportedOperationError(
                "API backend does not support changing the port name.")

        if self._port is None:
            raise InvalidUseError("No port currently opened.")

        self.baseptr().setPortName(_to_bytes(name))

    def set_error_callback(self, func, data=None):
        """Register a callback function for errors.

        The callback function is called when an error occurs and must take
        three arguments. The first argument is a member of enum
        ``RtMidiError::Type``, represented by one of the ``ERRORTYPE_*``
        constants. The second argument is an error message. The third argument
        is the value of the ``data`` argument passed to this function when the
        callback is registered.

        .. note::
            A default error handler function is registered on new instances of
            ``MidiIn`` and ``MidiOut``, which turns errors reported by the C++
            layer into custom exceptions derived from ``RtMidiError``.

            If you replace this default error handler, be aware that the
            exception handling in your code probably needs to be adapted.

        Registering an error callback function replaces any previously
        registered error callback, including the above mentioned default error
        handler.

        """
        self._error_callback = (func, data, self._decode_string)
        self.baseptr().setErrorCallback(&_cb_error_func,
                                        <void *>self._error_callback)

    def cancel_error_callback(self):
        """Remove the registered callback function for errors.

        This can be safely called even when no callback function has been
        registered and reinstates the default error handler.

        """
        self.set_error_callback(_default_error_handler)


cdef class MidiIn(MidiBase):
    """Midi input client interface.

    ``rtmidi.MidiIn(rtapi=API_UNSPECIFIED, name="RtMidi Client", queue_size_limit=1024)``

    You can specify the low-level MIDI backend API to use via the ``rtapi``
    keyword or the first positional argument, passing one of the module-level
    ``API_*`` constants. You can get a list of compiled-in APIs with the
    module-level ``get_compiled_api`` function. If you pass ``API_UNSPECIFIED``
    (the default), the first compiled-in API, which has any input ports
    available, will be used.

    You can optionally pass a name for the MIDI client with the ``name``
    keyword or the second positional argument. Names with non-ASCII characters
    in them have to be passed as unicode or UTF-8 encoded strings in Python 2.
    The default name is ``"RtMidiIn Client"``.

    .. note::
        With some backend APIs (e.g. ALSA), the client name is set by the first
        ``MidiIn`` *or* ``MidiOut`` created by your program and does not change
        unless you either use the ``set_client_name`` method, or until *all*
        ``MidiIn`` and ``MidiOut`` instances are deleted and then a new one is
        created.

    The ``queue_size_limit`` argument specifies the size of the internal ring
    buffer in which incoming MIDI events are placed until retrieved via the
    ``get_message`` method (i.e. when no callback function is registered).
    The default value is ``1024`` (overriding the default value ``100`` of the
    underlying C++ RtMidi library).

    Exceptions:

    ``SystemError``
        Raised when the RtMidi backend initialization fails. The execption
        message should have more information on the cause of the error.

    ``TypeError``
        Raised when an incompatible value type is passed for a parameter.

    """

    cdef RtMidiIn *thisptr
    cdef object _callback

    cdef RtMidi* baseptr(self):
        return self.thisptr

    def __cinit__(self, Api rtapi=UNSPECIFIED, name=None,
                  unsigned int queue_size_limit=1024):
        """Create a new client instance for MIDI input.

        See the class docstring for a description of the constructor arguments.

        """
        if name is None:
            name = "RtMidiIn Client"

        try:
            self.thisptr = new RtMidiIn(rtapi, _to_bytes(name), queue_size_limit)
        except RuntimeError as exc:
            raise SystemError(str(exc), type=ERR_DRIVER_ERROR)

        self.set_error_callback(_default_error_handler)
        self._callback = None
        self._port = None
        self._deleted = False

    def get_current_api(self):
        """Return the low-level MIDI backend API used by this instance.

        Use this by comparing the returned value to the module-level ``API_*``
        constants, e.g.::

            midiin = rtmidi.MidiIn()

            if midiin.get_current_api() == rtmidi.API_UNIX_JACK:
                print("Using JACK API for MIDI input.")

        """
        return self.thisptr.getCurrentApi()

    def __dealloc__(self):
        """De-allocate pointer to C++ class instance."""
        if hasattr(self, "thisptr"):
            del self.thisptr

    def delete(self):
        """De-allocate pointer to C++ class instance.

        .. warning:: the instance **must not** be used anymore after calling
            this method, otherwise the program will crash with a segmentation
            fault!

            The reason this potentially dangerous method exists is that in
            some cases it is desirable to destroy the internal ``RtMidiIn``
            C++ class instance with immediate effect, thereby closing the
            backend MIDI API client and all the ports it opened. By merely
            using ``del`` on the ``rtmidi.MidiIn`` Python instance, the
            destruction of the C++ instance may be delayed for an arbitrary
            amount of time, until the Python garbage collector cleans up the
            instance.

        """
        if not self._deleted:
            del self.thisptr
            self._deleted = True

    @property
    def is_deleted(self):
        return self._deleted

    def cancel_callback(self):
        """Remove the registered callback function for MIDI input.

        This can be safely called even when no callback function has been
        registered.

        """
        if self._callback:
            self.thisptr.cancelCallback()
            self._callback = None

    def close_port(self):
        self.cancel_callback()
        MidiBase.close_port(self)

    close_port.__doc__ == MidiBase.close_port.__doc__

    def get_message(self):
        """Poll for MIDI input.

        Checks whether a MIDI event is available in the input buffer and
        returns a two-element tuple with the MIDI message and a delta time. The
        MIDI message is a list of integers representing the data bytes of the
        message, the delta time is a float representing the time in seconds
        elapsed since the reception of the previous MIDI event.

        The function does not block. When no MIDI message is available, it
        returns ``None``.

        """
        cdef vector[unsigned char] msg_v
        cdef double delta_time = self.thisptr.getMessage(&msg_v)

        if not msg_v.empty():
            message = [msg_v.at(i) for i in range(msg_v.size())]
            return (message, delta_time)

    def ignore_types(self, sysex=True, timing=True, active_sense=True):
        """Enable/Disable input filtering of certain types of MIDI events.

        By default System Exclusive (aka sysex), MIDI Clock and Active Sensing
        messages are filtered from the MIDI input and never reach your code,
        because they can fill up input buffers very quickly.

        To receive them, you can selectively disable the filtering of these
        event types.

        To enable reception - i.e. turn off the default filtering - of sysex
        messages, pass ``sysex = False``.

        To enable reception of MIDI Clock, pass ``timing = False``.

        To enable reception of Active Sensing, pass ``active_sense = False``.

        These arguments can of course be combined in one call, and they all
        default to ``True``.

        If you enable reception of any of these event types, be sure to either
        use an input callback function, which returns quickly or poll for MIDI
        input often. Otherwise you might lose MIDI input because the input
        buffer overflows.

        **Windows note:** the Windows Multi Media API uses fixed size buffers
        for the reception of sysex messages, whose number and size is set at
        compile time. Sysex messages longer than the buffer size can not be
        received properly when using the Windows Multi Media API.

        The default distribution of python-rtmidi sets the number of sysex
        buffers to four and the size of each to 8192 bytes. To change these
        values, edit the ``RT_SYSEX_BUFFER_COUNT`` and ``RT_SYSEX_BUFFER_SIZE``
        preprocessor defines in ``RtMidi.cpp`` and recompile.

        """
        self.thisptr.ignoreTypes(sysex, timing, active_sense)

    def set_callback(self, func, data=None):
        """Register a callback function for MIDI input.

        The callback function is called whenever a MIDI message is received and
        must take two arguments. The first argument is a two-element tuple with
        the MIDI message and a delta time, like the one returned by the
        ``get_message`` method. The second argument is value of the ``data``
        argument passed to ``set_callback`` when the callback is registered.
        The value of ``data`` can be any Python object. It can be used inside
        the callback function to access data that would not be in scope
        otherwise.

        Registering a callback function replaces any previously registered
        callback.

        The callback function is safely removed when the input port is closed
        or the ``MidiIn`` instance is deleted.

        """
        if self._callback:
            self.cancel_callback()

        self._callback = (func, data)
        self.thisptr.setCallback(&_cb_func, <void *>self._callback)


cdef class MidiOut(MidiBase):
    """Midi output client interface.

    ``rtmidi.MidiOut(rtapi=API_UNSPECIFIED, name="RtMidi Client")``

    You can specify the low-level MIDI backend API to use via the ``rtapi``
    keyword or the first positional argument, passing one of the module-level
    ``API_*`` constants. You can get a list of compiled-in APIs with the
    module-level ``get_compiled_api`` function. If you pass ``API_UNSPECIFIED``
    (the default), the first compiled-in API, which has any input ports
    available, will be used.

    You can optionally pass a name for the MIDI client with the ``name``
    keyword or the second positional argument. Names with non-ASCII characters
    in them have to be passed as unicode or UTF-8 encoded strings in Python 2.
    The default name is ``"RtMidiOut Client"``.

    .. note::
        With some backend APIs (e.g. ALSA), the client name is set by the first
        ``MidiIn`` *or* ``MidiOut`` created by your program and does not change
        unless you either use the ``set_client_name`` method, or until *all*
        ``MidiIn`` and ``MidiOut`` instances are deleted and then a new one is
        created.

    Exceptions:

    ``SystemError``
        Raised when the RtMidi backend initialization fails. The execption
        message should have more information on the cause of the error.

    ``TypeError``
        Raised when an incompatible value type is passed for a parameter.

    """

    cdef RtMidiOut *thisptr

    cdef RtMidi* baseptr(self):
        return self.thisptr

    def __cinit__(self, Api rtapi=UNSPECIFIED, name=None):
        """Create a new client instance for MIDI output.

        See the class docstring for a description of the constructor arguments.

        """
        if name is None:
            name = "RtMidiOut Client"

        try:
            self.thisptr = new RtMidiOut(rtapi, _to_bytes(name))
        except RuntimeError as exc:
            raise SystemError(str(exc), type=ERR_DRIVER_ERROR)

        self.set_error_callback(_default_error_handler)
        self._port = None
        self._deleted = False

    def __dealloc__(self):
        """De-allocate pointer to C++ class instance."""
        if hasattr(self, "thisptr"):
            del self.thisptr

    def delete(self):
        """De-allocate pointer to C++ class instance.

        .. warning:: the instance **must not** be used anymore after calling
            this method, otherwise the program will crash with a segmentation
            fault!

            The reason this potentially dangerous method exists is that in
            some cases it is desirable to destroy the internal ``RtMidiOut``
            C++ class instance with immediate effect, thereby closing the
            backend MIDI API client and all the ports it opened. By merely
            using ``del`` on the ``rtmidi.MidiOut`` Python instance, the
            destruction of the C++ instance may be delayed for an arbitrary
            amount of time, until the Python garbage collector cleans up the
            instance.

        """
        if not self._deleted:
            del self.thisptr
            self._deleted = True

    @property
    def is_deleted(self):
        return self._deleted

    def get_current_api(self):
        """Return the low-level MIDI backend API used by this instance.

        Use this by comparing the returned value to the module-level ``API_*``
        constants, e.g.::

            midiout = rtmidi.MidiOut()

            if midiout.get_current_api() == rtmidi.API_UNIX_JACK:
                print("Using JACK API for MIDI output.")

        """
        return self.thisptr.getCurrentApi()

    def send_message(self, message):
        """Send a MIDI message to the output port.

        The message must be passed as an iterable yielding integers, each
        element representing one byte of the MIDI message.

        Normal MIDI messages have a length of one to three bytes, but you can
        also send system exclusive messages, which can be arbitrarily long, via
        this method.

        No check is made whether the passed data constitutes a valid MIDI
        message but if it is longer than 3 bytes, the value of the first byte
        must be a start-of-sysex status byte, i.e. 0xF0.

        .. note:: with some backend APIs (notably ```WINDOWS_MM``) this function
            blocks until the whole message is sent. While sending the message
            the global interpreter lock is released, so multiple Python threads
            can send messages using *different* MidiOut instances concurrently.

        Exceptions:

        ``ValueError``
            Raised if ``message`` argument is empty or more than 3 bytes long
            and not a SysEx message.

        """
        cdef vector[unsigned char] msg_v

        if not message:
            raise ValueError("'message' must not be empty.")

        if len(message) > 3 and message[0] != 0xF0:
            raise ValueError("'message' longer than 3 bytes but does not "
                             "start with 0xF0.")

        for c in message:
            msg_v.push_back(c)

        with nogil:
            self.thisptr.sendMessage(&msg_v)
