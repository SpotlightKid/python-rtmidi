# cython: embedsignature = True
# cython: language_level = 3
# cython: show_performance_hints = False
# cython: freethreading_compatible = True
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
Python package naming structure. **python-rtmidi** supports Python 3 (3.9+).


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
``API_RWEB_MIDI``
    W3C Web MIDI API



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

cimport cython
from cpython.ref cimport PyObject
from libcpp cimport bool
from libcpp.string cimport string
from libcpp.vector cimport vector


__all__ = (
    'API_UNSPECIFIED', 'API_MACOSX_CORE', 'API_LINUX_ALSA', 'API_UNIX_JACK',
    'API_WINDOWS_MM', 'API_RTMIDI_DUMMY', 'API_WEB_MIDI', 'ERRORTYPE_DEBUG_WARNING',
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

cdef extern from "py_init.h":
    void py_init()

py_init()

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
        WEB_MIDI     "RtMidi::WEB_MIDI_API"
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
                                    void *userData) except * with gil

    ctypedef void (*RtMidiErrorCallback)(ErrorType errorType,
                                         const string errorText,
                                         void *userData) except * with gil

    cdef cppclass RtMidi:
        # nogil: MidiIn.close_port() calls it without the GIL / an attached
        # thread state, because it waits for the input thread (see there).
        void closePort() except * nogil
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
        void setBufferSize(unsigned int size, unsigned int count) except *

    cdef cppclass RtMidiOut(RtMidi):
        Api RtMidiOut(Api rtapi, string clientName) except +
        Api getCurrentApi()
        void sendMessage(vector[unsigned char] *message) except *


# internal functions

cdef extern from *:
    """
    /* The MidiIn whose input callback is running on this thread, if any. */
    static thread_local void *rtmidi_callback_owner = NULL;

    /* Destroys a RtMidiIn on a new thread (the thread that runs this does not
       need a Python thread state); -1 if the thread could not be started. */
    static void rtmidi_destroy_midiin_thread(void *ptr) {
        delete static_cast<RtMidiIn *>(ptr);
    }

    static int rtmidi_destroy_midiin_later(RtMidiIn *ptr) {
        return PyThread_start_new_thread(rtmidi_destroy_midiin_thread, ptr)
            == (unsigned long)-1 ? -1 : 0;
    }

    /* Replaces the tp_clear slot of a GC type that has none; see MidiBase.
       Returns 0 where the slot cannot be set (limited API, not CPython). */
    static int rtmidi_set_tp_clear(PyObject *type, int (*clear)(PyObject *)) {
    #if CYTHON_COMPILING_IN_CPYTHON && !CYTHON_COMPILING_IN_LIMITED_API
        PyTypeObject *tp = (PyTypeObject *)type;

        if (!PyType_HasFeature(tp, Py_TPFLAGS_HAVE_GC) || tp->tp_traverse == NULL)
            return 0;

        tp->tp_clear = clear;
        return 1;
    #else
        return 0;
    #endif
    }
    """
    void *rtmidi_callback_owner
    int rtmidi_destroy_midiin_later(RtMidiIn *ptr)
    int rtmidi_set_tp_clear(PyObject *type, int (*clear)(PyObject *) noexcept)


cdef void _cb_func(double delta_time, vector[unsigned char] *msg_v,
                   void *cb_info) except * with gil:
    """Wrapper for a Python callback function for MIDI input.

    Runs on the backend's input thread. ``cb_info`` is the ``MidiIn``
    instance, borrowed: its deallocator stops this thread before the instance
    goes away, so no reference is taken here (taking one while the instance is
    being deallocated on another thread would corrupt its reference count).

    """
    global rtmidi_callback_owner
    cdef void *outer_owner

    if cb_info == NULL:
        # RtMidi read its user data while cancelCallback() was resetting it.
        return

    callback = (<MidiIn> cb_info)._get_callback()

    if callback is None:
        # The callback was cancelled while this message was in flight.
        return

    func, data = callback
    message = [msg_v.at(i) for i in range(msg_v.size())]
    outer_owner = rtmidi_callback_owner
    rtmidi_callback_owner = cb_info

    try:
        func((message, delta_time), data)
    finally:
        # These may be the last references to the instance (the garbage
        # collector can clear its callbacks while this thread has picked one
        # up). Release them while still marked as the instance's input thread,
        # so that its deallocation does not wait for this thread.
        callback = func = data = None
        rtmidi_callback_owner = outer_owner


cdef void _cb_error_func(ErrorType errorType, const string &errorText,
                         void *cb_info) except * with gil:
    """Wrapper for a Python callback function for errors.

    Called synchronously by the C++ method that hit the error, on the thread
    that called it, which holds a reference to the ``MidiIn`` / ``MidiOut``
    instance passed as ``cb_info``.

    """
    midi = <MidiBase> cb_info
    callback = midi._get_error_callback()

    if callback is None:
        # Deleted while the call that hit the error was in progress.
        return

    func, data = callback
    func(errorType, midi._decode_string(errorText), data)


def _to_bytes(name):
    """Convert a str object into bytes."""
    if isinstance(name, str):
        name = bytes(name, 'utf-8')  # Python 3

    if not isinstance(name, bytes):
        raise TypeError("name must be a bytes instance.")

    return name


# Public API

# export Api enum values to Python

API_UNSPECIFIED = UNSPECIFIED
API_MACOSX_CORE = MACOSX_CORE
API_LINUX_ALSA = LINUX_ALSA
API_UNIX_JACK = UNIX_JACK
API_WINDOWS_MM = WINDOWS_MM
API_WEB_MIDI = WEB_MIDI
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

    All other exceptions in this module derive from this exception.

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


# Thread safety
# -------------
#
# Every public method of ``MidiIn`` / ``MidiOut`` runs in a critical section on
# the instance (``@cython.critical_section``). On a free-threaded build that
# serializes calls on one instance the way the GIL does on a regular build;
# there, it compiles to nothing. Calls on different instances run in parallel.
#
# Like the GIL, a critical section is released while its thread blocks, e.g.
# in an error callback. So methods that use the C++ instance bracket that with
# ``_enter()`` / ``_exit()``, which count the calls in progress: ``delete()``
# leaves the C++ instance to the last of them to free.
#
# The callbacks are passed to RtMidi as the instance itself and the Python
# callable is read under ``_cb_lock``, which is only ever held to read or swap
# the stored reference; so replacing a callback cannot free what the input
# thread is about to call, and the input thread never waits for the critical
# section.
#
# ``MidiIn.close_port()`` and the C++ destructor (``MidiIn.delete()``,
# ``__dealloc__``) wait for the input thread to stop, and that thread may be
# waiting to run a callback. So they wait without the GIL (regular build) or
# with the thread state detached (free-threaded build). While ``close_port()``
# waits, other calls on the instance raise ``InvalidUseError`` (or, for
# ``get_message()``, return ``None``). Neither can be done by the input thread
# itself: ``delete()`` raises there, and a deallocation there leaves the
# destruction to another thread (``rtmidi_callback_owner`` tells).
#
# Garbage collection: the callbacks can be part of a reference cycle (e.g.
# ``midiin.set_callback(func, midiin)``), which the garbage collector must be
# able to break. Cython's generated ``tp_clear`` would store to the callback
# fields without ``_cb_lock``, racing with the input thread, which reads them
# under it (on a free-threaded build the collector runs while other threads
# do). So the classes are ``no_gc_clear``, which makes Cython generate no
# ``tp_clear`` (``tp_traverse`` stays), and ``_install_gc_clear()`` sets
# ``_gc_clear`` as their ``tp_clear`` at import. That drops the callbacks the
# way ``_swap_callback()`` replaces them: under ``_cb_lock``, releasing the old
# references after it. The input thread either got a callback before (and
# holds its own references, which keep the instance alive) or finds ``None``.
# Python subclasses reach it through ``subtype_clear``. Only unreachable
# instances are cleared, so no method call on one is in progress: callers hold
# a reference to it. The exception is the input thread, which is handed the
# instance without one: it may pick up a callback after the collector found
# the instance unreachable and before it clears it. The thread then holds the
# last references to the instance, so ``_cb_func`` releases them before it
# stops being the instance's ``rtmidi_callback_owner``, and
# ``MidiIn.__dealloc__`` leaves the destruction of the C++ instance to another
# thread if it runs on the input thread anyway.
#
# Where ``tp_clear`` cannot be set (limited API, not CPython), the classes
# keep Cython's no_gc_clear behavior: cycles through callbacks are only broken
# by ``close_port()`` and ``delete()``.

@cython.no_gc_clear
cdef class MidiBase:
    cdef object _port
    cdef object _error_callback
    cdef bint _deleted
    cdef Api _api  # fixed when the C++ instance is created
    cdef cython.pymutex _cb_lock
    # Calls in progress that use the C++ instance (see _enter()), and the C++
    # instance that delete() left for the last of them to free.
    cdef int _calls
    cdef RtMidi *_doomed
    # True while MidiIn.close_port() waits for the input thread without the
    # critical section (see there).
    cdef bint _closing

    cdef RtMidi* baseptr(self) noexcept:
        # The C++ instance, NULL once deleted.
        return NULL

    cdef void _forget_ptr(self) noexcept:
        pass

    cdef void _destroy(self, RtMidi *ptr) noexcept nogil:
        # Deletes through the concrete type (RtMidi's destructor is protected).
        pass

    cdef RtMidi* _enter(self) except NULL:
        # Call with the critical section on self held; pair with _exit().
        if self._deleted:
            raise InvalidUseError("%r has been deleted." % self)
        if self._closing:
            raise InvalidUseError("%r is closing its port." % self)

        self._calls += 1
        return self.baseptr()

    cdef void _exit(self) noexcept:
        # Call with the critical section on self held.
        cdef RtMidi *ptr = self._doomed
        self._calls -= 1

        # Not on the input thread of this instance: see _delete().
        if self._calls == 0 and ptr != NULL and rtmidi_callback_owner != <void *>self:
            self._doomed = NULL
            self._free(ptr)

    cdef int _delete(self) except -1:
        cdef RtMidi *ptr

        with cython.critical_section(self):
            if self._deleted:
                return 0

            if rtmidi_callback_owner == <void *>self:
                # The destructor would stop and join the thread running this.
                raise InvalidUseError("%r cannot be deleted from its own input "
                                      "callback." % self)

            ptr = self.baseptr()
            self._forget_ptr()
            self._deleted = True

            if self._calls:
                self._doomed = ptr
                return 0

        self._free(ptr)
        return 0

    cdef void _free(self, RtMidi *ptr) noexcept:
        # The destructor stops the input thread, which may be waiting to run a
        # callback, so let it run.
        with nogil:
            self._destroy(ptr)

        # They may be part of a reference cycle.
        self._drop_callbacks()

    cdef void _drop_callbacks(self) noexcept:
        self._swap_error_callback(None)

    cdef object _get_error_callback(self):
        with self._cb_lock:
            return self._error_callback

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

    cdef str _check_port(self):
        inout = "input" if isinstance(self, MidiIn) else "output"
        if self._port == -1:
            raise InvalidUseError("%r already opened virtual %s port." %
                                  (self, inout))
        elif self._port is not None:
            raise InvalidUseError("%r already opened %s port %i." %
                                  (self, inout, self._port))
        return inout

    cdef object _decode_string(self, s, encoding='auto'):
        """Decode given byte string with given encoding."""
        if encoding == 'auto':
            if sys.platform.startswith('win'):
                encoding = 'latin1'
            elif (self._api == API_MACOSX_CORE and
                  sys.platform == 'darwin'):
                encoding = 'macroman'
            else:
                encoding = 'utf-8'

        return s.decode(encoding, "ignore")

    @cython.critical_section
    def get_port_count(self):
        """Return the number of available MIDI input or output ports."""
        cdef RtMidi *ptr = self._enter()

        try:
            return ptr.getPortCount()
        finally:
            self._exit()

    @cython.critical_section
    def get_port_name(self, unsigned int port, encoding='auto'):
        """Return the name of the MIDI input or output port with given number.

        Ports are numbered from zero, separately for input and output ports.
        The number of available ports is returned by the ``get_port_count``
        method.

        The port name is decoded to a (unicode) string with the encoding given
        by ``encoding``. If ``encoding`` is ``"auto"`` (the default), then an
        appropriate encoding is chosen based on the system and the used backend
        API. If ``encoding`` is ``None``, the name is returned un-decoded, i.e.
        as type ``bytes``.

        """
        cdef RtMidi *ptr = self._enter()
        cdef string name

        try:
            name = ptr.getPortName(port)
        finally:
            self._exit()

        if len(name):
            return self._decode_string(name, encoding) if encoding else name

    def get_ports(self, encoding='auto'):
        """Return a list of names of available MIDI input or output ports.

        The list index of each port name corresponds to its port number.

        The port names are decoded to (unicode) strings with the encoding given
        by ``encoding``. If ``encoding`` is ``"auto"`` (the default), then an
        appropriate encoding is chosen based on the system and the used backend
        API. If ``encoding`` is ``None``, the names are returned un-decoded,
        i.e. as type ``bytes``.

        """
        return [self.get_port_name(p, encoding=encoding)
                for p in range(self.get_port_count())]

    @cython.critical_section
    def is_port_open(self):
        """Return ``True`` if a port has been opened and ``False`` if not.

        .. note::
            The ``isPortOpen`` method of the RtMidi C++ library does not
            return ``True`` when a virtual port has been openend. The
            python-rtmidi implementation, on the other hand, does.

        """
        return self._port is not None

    @cython.critical_section
    def open_port(self, unsigned int port=0, name=None):
        """Open the MIDI input or output port with the given port number.

        Only one port can be opened per ``MidiIn`` or ``MidiOut`` instance. An
        ``InvalidUseError`` exception is raised if an attempt is made to open a
        port on a ``MidiIn`` or ``MidiOut`` instance, which already opened a
        (virtual) port.

        You can optionally pass a name for the RtMidi port with the ``name``
        keyword or the second positional argument. Names with non-ASCII
        characters in them have to be passed as a (unicode) str or UTF-8
        encoded bytes. The default name is "RtMidi input" resp. "RtMidi
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

        cdef RtMidi *ptr = self._enter()

        try:
            ptr.openPort(port, _to_bytes(name))
        finally:
            self._exit()

        self._port = port
        return self

    @cython.critical_section
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
        characters in them have to be passed as a (unicode) str or UTF-8
        encoded bytes. The default name is "RtMidi virtual input" resp.
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
        if self._api == API_WINDOWS_MM:
            raise NotImplementedError("Virtual ports are not supported "
                                      "by the Windows MultiMedia API.")

        inout = self._check_port()
        cdef RtMidi *ptr = self._enter()

        try:
            ptr.openVirtualPort(_to_bytes(("RtMidi virtual %s" % inout)
                                          if name is None else name))
        finally:
            self._exit()

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
        cdef RtMidi *ptr

        with cython.critical_section(self):
            if self._deleted:
                return

            if self._port != -1:
                self._port = None

            ptr = self._enter()

            try:
                ptr.closePort()
            finally:
                self._exit()

    @cython.critical_section
    def set_client_name(self, name):
        """Set the name of the MIDI client.

        Names with non-ASCII characters in them have to be passed as a (unicode)
        str or UTF-8 encoded bytes.

        Currently only supported by the ALSA API backend.

        Exceptions:

        ``TypeError``
            Raised when an incompatible value type is passed for the ``name``
            parameter.
        ``UnsupportedOperationError``
            Raised when trying the backend API does not support changing the
            client name.

        """
        if self._api in (API_MACOSX_CORE, API_UNIX_JACK, API_WINDOWS_MM):
            raise NotImplementedError(
                "API backend does not support changing the client name.")

        cdef RtMidi *ptr = self._enter()

        try:
            ptr.setClientName(_to_bytes(name))
        finally:
            self._exit()

    @cython.critical_section
    def set_port_name(self, name):
        """Set the name of the currently opened port.

        Names with non-ASCII characters in them have to be passed as a (unicode)
        str or UTF-8 encoded bytes.

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
        if self._api in (API_MACOSX_CORE, API_WINDOWS_MM):
            raise UnsupportedOperationError(
                "API backend does not support changing the port name.")

        if self._port is None:
            raise InvalidUseError("No port currently opened.")

        cdef RtMidi *ptr = self._enter()

        try:
            ptr.setPortName(_to_bytes(name))
        finally:
            self._exit()

    @cython.critical_section
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
        cdef RtMidi *ptr = self._enter()

        try:
            # Released at the end, after the C++ call.
            old = self._swap_error_callback((func, data))
            ptr.setErrorCallback(&_cb_error_func, <void *>self)
        finally:
            self._exit()

    cdef object _swap_error_callback(self, callback):
        # Returns the old callback, so that it is released after _cb_lock is.
        with self._cb_lock:
            old = self._error_callback
            self._error_callback = callback
        return old

    def cancel_error_callback(self):
        """Remove the registered callback function for errors.

        This can be safely called even when no callback function has been
        registered and reinstates the default error handler.

        """
        self.set_error_callback(_default_error_handler)


@cython.no_gc_clear
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
    in them have to be passed as a (unicode) str or UTF-8 encoded bytes.
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

    cdef RtMidi* baseptr(self) noexcept:
        return self.thisptr

    cdef void _forget_ptr(self) noexcept:
        self.thisptr = NULL

    cdef void _destroy(self, RtMidi *ptr) noexcept nogil:
        cdef RtMidiIn *midiin = <RtMidiIn *>ptr
        del midiin

    cdef void _drop_callbacks(self) noexcept:
        MidiBase._drop_callbacks(self)
        self._swap_callback(None)

    cdef object _get_callback(self):
        with self._cb_lock:
            return self._callback

    cdef object _swap_callback(self, callback):
        # Returns the old callback, so that it is released after _cb_lock is.
        with self._cb_lock:
            old = self._callback
            self._callback = callback
        return old

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

        self._api = self.thisptr.getCurrentApi()
        self._callback = None
        self._port = None
        self._deleted = False
        self.set_error_callback(_default_error_handler)

    def get_current_api(self):
        """Return the low-level MIDI backend API used by this instance.

        Use this by comparing the returned value to the module-level ``API_*``
        constants, e.g.::

            midiin = rtmidi.MidiIn()

            if midiin.get_current_api() == rtmidi.API_UNIX_JACK:
                print("Using JACK API for MIDI input.")

        """
        return self._api

    def __dealloc__(self):
        """De-allocate pointer to C++ class instance."""
        cdef RtMidi *ptr = self._doomed if self.thisptr == NULL else <RtMidi *>self.thisptr

        if ptr == NULL:
            return

        if rtmidi_callback_owner == <void *>self:
            # The last reference went away in this instance's own input
            # callback, and the destructor cannot stop the thread it runs on.
            # So stop the thread from calling into this instance (and its
            # error callback, which the destructor may call) and destroy the
            # C++ instance on another thread, which waits for this one. If no
            # thread can be started, it is leaked.
            self._swap_error_callback(None)

            try:
                (<RtMidiIn *>ptr).cancelCallback()
            except BaseException:
                pass

            ptr.setErrorCallback(NULL, NULL)
            rtmidi_destroy_midiin_later(<RtMidiIn *>ptr)
            return

        # The destructor stops the input thread, which may be waiting to run a
        # callback, so let it run.
        with nogil:
            self._destroy(ptr)

    def delete(self):
        """De-allocate pointer to C++ class instance.

        .. note:: after calling this method, all other methods of the
            instance, except ``get_current_api``, ``is_port_open``,
            ``close_port`` and the ``is_deleted`` property, raise
            ``InvalidUseError``. If another thread is in a call on the
            instance, the C++ instance is destroyed when that call returns.

            The reason this method exists is that in some cases it is
            desirable to destroy the internal ``RtMidiIn`` C++ class instance
            with immediate effect, thereby closing the backend MIDI API client
            and all the ports it opened. By merely using ``del`` on the
            ``rtmidi.MidiIn`` Python instance, the destruction of the C++
            instance may be delayed until the last reference to it is gone,
            which may only happen when the Python garbage collector runs.

        It is safe to call this method repeatedly, but not from the input
        callback of the same instance (``InvalidUseError``): the destructor
        waits for the thread that runs it.

        """
        self._delete()

    @property
    def is_deleted(self):
        return self._deleted

    def cancel_callback(self):
        """Remove the registered callback function for MIDI input.

        This can be safely called even when no callback function has been
        registered.

        """
        cdef RtMidi *ptr

        with cython.critical_section(self):
            if self._deleted or self._closing or self._callback is None:
                return

            ptr = self._enter()

            try:
                # Released at the end, after the C++ call.
                old = self._swap_callback(None)
                (<RtMidiIn *>ptr).cancelCallback()
            finally:
                self._exit()

    def close_port(self):
        cdef RtMidi *ptr
        cdef bint had_callback

        with cython.critical_section(self):
            if self._deleted or self._closing:
                # Deleted, or another thread is closing it already.
                return

            ptr = self._enter()
            self._closing = True
            # Messages that arrive while the port closes are dropped.
            had_callback = self._swap_callback(None) is not None

            if self._port != -1:
                self._port = None

        # closePort() waits for the input thread, which may be waiting to run
        # a callback. So it runs without the GIL (regular build) or with the
        # thread state detached (free-threaded build), which also suspends the
        # critical section; _closing makes other calls on this instance raise
        # InvalidUseError meanwhile, rather than use the C++ instance with it.
        try:
            with nogil:
                ptr.closePort()
        finally:
            with cython.critical_section(self):
                self._closing = False

                try:
                    if had_callback:
                        # Only after closePort(): RtMidi does not synchronize
                        # cancelCallback() with its input thread.
                        (<RtMidiIn *>ptr).cancelCallback()
                finally:
                    self._exit()

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
        cdef double delta_time
        cdef RtMidi *ptr

        with cython.critical_section(self):
            if self._closing:
                # Another thread is closing the port.
                return None

            ptr = self._enter()

            try:
                delta_time = (<RtMidiIn *>ptr).getMessage(&msg_v)
            finally:
                self._exit()

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
        for the reception of sysex messages. You can change the number and
        size of the buffers with the ``set_buffer_size`` method.

        """
        cdef RtMidi *ptr

        with cython.critical_section(self):
            ptr = self._enter()

            try:
                (<RtMidiIn *>ptr).ignoreTypes(sysex, timing, active_sense)
            finally:
                self._exit()

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
        cdef RtMidi *ptr

        with cython.critical_section(self):
            ptr = self._enter()

            try:
                # Released at the end, after the C++ call.
                old = self._swap_callback((func, data))

                # Otherwise RtMidi already calls _cb_func with this instance,
                # which picks up the new callback. Not cancelling and setting
                # it again in RtMidi avoids its input thread racing with the
                # change: RtMidi does not synchronize them, and could call a
                # null pointer.
                if old is None:
                    try:
                        (<RtMidiIn *>ptr).setCallback(&_cb_func, <void *>self)
                    except BaseException:
                        self._swap_callback(None)
                        raise
            finally:
                self._exit()

    def set_buffer_size(self, size, count):
        """Set the size and number of MIDI input buffers."""
        cdef RtMidi *ptr

        with cython.critical_section(self):
            ptr = self._enter()

            try:
                (<RtMidiIn *>ptr).setBufferSize(size, count)
            finally:
                self._exit()


@cython.no_gc_clear
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
    in them have to be passed as a (unicode) str or UTF-8 encoded bytes.
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

    cdef RtMidi* baseptr(self) noexcept:
        return self.thisptr

    cdef void _forget_ptr(self) noexcept:
        self.thisptr = NULL

    cdef void _destroy(self, RtMidi *ptr) noexcept nogil:
        cdef RtMidiOut *midiout = <RtMidiOut *>ptr
        del midiout

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

        self._api = self.thisptr.getCurrentApi()
        self._port = None
        self._deleted = False
        self.set_error_callback(_default_error_handler)

    def __dealloc__(self):
        """De-allocate pointer to C++ class instance."""
        cdef RtMidi *ptr = self._doomed if self.thisptr == NULL else <RtMidi *>self.thisptr

        if ptr != NULL:
            self._destroy(ptr)

    def delete(self):
        """De-allocate pointer to C++ class instance.

        .. note:: after calling this method, all other methods of the
            instance, except ``get_current_api``, ``is_port_open``,
            ``close_port`` and the ``is_deleted`` property, raise
            ``InvalidUseError``. If another thread is in a call on the
            instance, the C++ instance is destroyed when that call returns.

            The reason this method exists is that in some cases it is
            desirable to destroy the internal ``RtMidiOut`` C++ class instance
            with immediate effect, thereby closing the backend MIDI API client
            and all the ports it opened. By merely using ``del`` on the
            ``rtmidi.MidiOut`` Python instance, the destruction of the C++
            instance may be delayed until the last reference to it is gone,
            which may only happen when the Python garbage collector runs.

        It is safe to call this method repeatedly.

        """
        self._delete()

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
        return self._api

    def send_message(self, message):
        """Send a MIDI message to the output port.

        The message must be passed as an iterable yielding integers, each
        element representing one byte of the MIDI message.

        Normal MIDI messages have a length of one to three bytes, but you can
        also send System Exclusive messages, which can be arbitrarily long, via
        this method.

        No check is made whether the passed data constitutes a valid MIDI
        message but if it is longer than 3 bytes, the value of the first byte
        must be a start-of-sysex status byte, i.e. 0xF0.

        .. note:: with some backend APIs (notably ```WINDOWS_MM``) this function
            blocks until the whole message is sent.

        Exceptions:

        ``ValueError``
            Raised if ``message`` argument is empty or more than 3 bytes long
            and not a SysEx message.

        """
        cdef vector[unsigned char] msg_v

        try:
            msg_v.reserve(len(message))
        except TypeError:
            pass

        for c in message:
            msg_v.push_back(c)

        if msg_v.size() == 0:
            raise ValueError("'message' must not be empty.")
        elif msg_v.size() > 3 and msg_v.at(0) != 0xF0:
            raise ValueError("'message' longer than 3 bytes but does not "
                             "start with 0xF0.")

        cdef RtMidi *ptr

        with cython.critical_section(self):
            ptr = self._enter()

            try:
                (<RtMidiOut *>ptr).sendMessage(&msg_v)
            finally:
                self._exit()


cdef int _gc_clear(PyObject *o) noexcept:
    # tp_clear of the classes above (see "Garbage collection"). Must not raise.
    (<MidiBase>o)._drop_callbacks()
    return 0


cdef void _install_gc_clear() noexcept:
    # Before any instance exists, so that no subclass has inherited a slot yet.
    # MidiIn and MidiOut have their own tp_traverse, so they do not inherit
    # their base's tp_clear.
    rtmidi_set_tp_clear(<PyObject *>MidiBase, &_gc_clear)
    rtmidi_set_tp_clear(<PyObject *>MidiIn, &_gc_clear)
    rtmidi_set_tp_clear(<PyObject *>MidiOut, &_gc_clear)


_install_gc_clear()
