#cython: embedsignature=True
#
# rtmidi.pyx
#
"""A Python wrapper for the RtMidi C++ library written with Cython."""

from libcpp cimport bool
from libcpp.string cimport string
from libcpp.vector cimport vector


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
        WINDOWS_KS   "RtMidi::WINDOWS_KS"
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
API_WINDOWS_KS = WINDOWS_KS
API_RTMIDI_DUMMY = RTMIDI_DUMMY

# internal functions

cdef void _cb_func(double delta_time, vector[unsigned char] *msg_v,
        void *cb_info) with gil:
    func, data = (<object> cb_info)
    message = [msg_v.at(i) for i in range(msg_v.size())]
    func((message, delta_time), data)

def _to_bytes(name):
    """Convert a 'unicode' (Python 2) or 'str' (Python 3) object into 'bytes'.
    """
    # 'bytes' == 'str' in Python 2 but a separate type in Python 3
    if not isinstance(name, bytes):
        try:
            name = bytes(name, 'utf-8') # Python 3
        except TypeError:
            name = bytes(name.encode('utf-8')) # Python 2

    return name

# Public API

def get_compiled_api():
    """Return list of MIDI APIs this module supports.

    Check for support for a particular API by using the API_* constants in
    the module namespace, i.e.::

        if rtmidi.API_UNIX_JACK in rtmidi.get_compiled_api():
            ...

    """
    cdef vector[Api] api_v

    RtMidi_getCompiledApi(api_v)
    return [api_v[i] for i in range(api_v.size())]


cdef class MidiIn:
    """Midi input client interface."""
    cdef RtMidiIn *thisptr
    cdef object _callback

    def __cinit__(self, Api rtapi=UNSPECIFIED,
            string name="RtMidi Input Client",
            unsigned int queue_size_limit=100):
        self.thisptr = new RtMidiIn(rtapi, _to_bytes(name), queue_size_limit)
        self._callback = None

    def __dealloc__(self):
        self.cancel_callback()
        del self.thisptr

    def get_current_api(self):
        return self.thisptr.getCurrentApi()

    def get_port_count(self):
        return self.thisptr.getPortCount()

    def get_port_name(self, unsigned int port, encoding='utf-8'):
        """Return name of given port number.

        The port name is decoded to unicode with the encoding given by
        ``encoding`` (defaults to ``'utf-8'``). If ``encoding`` is ``None``,
        return string un-decoded.

        """
        cdef string name = self.thisptr.getPortName(port)

        if len(name):
            if encoding:
                # XXX: kludge, there seems to be a bug in RtMidi as it returns
                # improperly encoded strings from getPortName with some
                # backends, so we just ignore decoding errors
                return name.decode(encoding, errors="ignore")
            else:
                return name
        else:
            return None

    def get_ports(self, encoding='utf-8'):
        return [self.get_port_name(p, encoding=encoding)
            for p in range(self.get_port_count())]

    def open_port(self, unsigned int port=0, string name="RtMidi Input"):
        """Open the MIDI input port with the given port number.

        You can pass an optional name for the RtMidi input port as the second
        argument. Closing a port and opening it again with a different name
        does not change the port name. To change the input port name, drop
        the MidiIn instance and create a new one and open the port again giving
        a different input port name.

        """
        self.thisptr.openPort(port, _to_bytes(name))

    def open_virtual_port(self, string name="RtMidi Input"):
        self.thisptr.openVirtualPort(_to_bytes(name))

    def close_port(self):
        self.cancel_callback()
        self.thisptr.closePort()

    def ignore_types(self, sysex=True, timing=True, active_sense=True):
        self.thisptr.ignoreTypes(sysex, timing, active_sense)

    def get_message(self):
        cdef vector[unsigned char] msg_v
        cdef double delta_time = self.thisptr.getMessage(&msg_v)

        if not msg_v.empty():
            message = [msg_v.at(i) for i in range(msg_v.size())]
            return (message, delta_time)
        else:
            return None

    def set_callback(self, func, data=None):
        if self._callback:
            self.cancel_callback()
        self._callback = (func, data)
        self.thisptr.setCallback(&_cb_func, <void *>self._callback)

    def cancel_callback(self):
        if self._callback:
            self.thisptr.cancelCallback()
            self._callback = None


cdef class MidiOut:
    """Midi output client interface."""
    cdef RtMidiOut *thisptr

    def __cinit__(self, Api rtapi=UNSPECIFIED,
            string name="RtMidi Output Client"):
        self.thisptr = new RtMidiOut(rtapi, _to_bytes(name))

    def __dealloc__(self):
        del self.thisptr

    def get_current_api(self):
        return self.thisptr.getCurrentApi()

    def get_port_count(self):
        return self.thisptr.getPortCount()

    def get_port_name(self, unsigned int port, encoding='utf-8'):
        """Return name of given port number.

        The port name is decoded to unicode with the encoding given by
        ``encoding`` (defaults to ``'utf-8'``). If ``encoding`` is ``None``,
        return string un-decoded.

        """
        cdef string name = self.thisptr.getPortName(port)

        if len(name):
            if encoding:
                # XXX: kludge, there seems to be a bug in RtMidi as it returns
                # improperly encoded strings from getPortName with some
                # backends, so we just ignore decoding errors
                return name.decode(encoding, errors="ignore")
            else:
                return name
        else:
            return None

    def get_ports(self, encoding='utf-8'):
        return [self.get_port_name(p, encoding=encoding)
            for p in range(self.get_port_count())]

    def open_port(self, unsigned int port=0, string name="RtMidi Output"):
        self.thisptr.openPort(port, _to_bytes(name))

    def open_virtual_port(self, string name="RtMidi Output"):
        self.thisptr.openVirtualPort(_to_bytes(name))

    def close_port(self):
        self.thisptr.closePort()

    def send_message(self, message):
        cdef vector[unsigned char] msg_v

        for c in message:
            msg_v.push_back(c)

        self.thisptr.sendMessage(&msg_v)
