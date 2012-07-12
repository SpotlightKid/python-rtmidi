#cython: embedsignature=True
#
# rtmidi.pyx
#
"""A Python wrapper for the RtMidi C++ library written with Cython."""

from cython.operator import dereference
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

# global registry of RtMidiCallbacks for all RtMidiIn instances
_callbacks = {}

# internal functions

cdef void _cb_func(double timeStamp, vector[unsigned char] *message,
        void *userData) with gil:
    cdef int n_bytes, i
    cdef char* c_inst_id = <char *> userData

    inst_id = c_inst_id
    cb_info = _callbacks.get(inst_id)

    if cb_info:
        cb_func, user_data = cb_info
        data = []
        n_bytes = message.size()

        for i from 0 <= i < n_bytes:
            data.append(message.at(i))

        cb_func((data, timeStamp), user_data)
    else:
        print("No callback function registered for instance '%s'" % inst_id)

def _to_bytes(name):
    """Convert a 'unicode' (Python 2) or 'str' (Python 3) object into 'bytes'.
    """
    # 'bytes' == 'str' in Python 2 but a separate type in Python 3
    if not isinstance(name, bytes):
        try:
            name = bytes(name, 'utf-8') # Python 3
        except TypeError:
            name = bytes(name.encode('utf-8')) # Python 3

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
    cdef int size, i

    RtMidi_getCompiledApi(api_v)
    size = api_v.size()
    apis = []

    for i from 0 <= i < size:
        apis.append(api_v[i])

    return apis


cdef class MidiIn:
    """Midi input client interface."""
    cdef RtMidiIn *thisptr

    def __cinit__(self, Api rtapi=UNSPECIFIED,
            string name="RtMidi Input Client",
            unsigned int queue_size_limit=100):
        name = _to_bytes(name)
        self.thisptr = new RtMidiIn(rtapi, name, queue_size_limit)

    def __dealloc__(self):
        self.cancel_callback()
        del self.thisptr

    def get_current_api(self):
        return self.thisptr.getCurrentApi()

    def get_port_count(self):
        return self.thisptr.getPortCount()

    def get_port_name(self, unsigned int portNumber):
        cdef string name = self.thisptr.getPortName(portNumber)

        if len(name):
            return name.decode('utf-8')
        else:
            return None

    def get_ports(self):
        return [self.get_port_name(p) for p in range(self.get_port_count())]

    def open_port(self, unsigned int port=0, string name="RtMidi Input"):
        """Open the MIDI input port with the given port number.

        You can pass an optional name for the RtMidi input port as the second
        argument. Closing a port and openeing it again with a different name
        does not change the port name. To change the input port name, drop
        the MidiIn instance and create a new one and open the port again giving
        a different input port name.

        """
        name = _to_bytes(name)
        self.thisptr.openPort(port, name)

    def open_virtual_port(self, string name="RtMidi Input"):
        name = _to_bytes(name)
        self.thisptr.openVirtualPort(name)

    def close_port(self):
        self.cancel_callback()
        self.thisptr.closePort()

    def ignore_types(self, sysex=True, timing=True, active_sense=True):
        self.thisptr.ignoreTypes(sysex, timing, active_sense)

    def get_message(self):
        cdef vector[unsigned char] msg_v
        cdef int n_bytes, i
        cdef double stamp

        stamp = self.thisptr.getMessage(&msg_v)
        n_bytes = msg_v.size()

        if n_bytes:
            message = []

            for i from 0 <= i < n_bytes:
                message.append(msg_v[i])

            return (message, stamp)
        else:
            return None

    def set_callback(self, func, data=None):
        cdef char * c_inst_id

        inst_id = _to_bytes(str(id(self)))
        c_inst_id = inst_id
        self.cancel_callback()
        _callbacks[inst_id] = (func, data)
        self.thisptr.setCallback(&_cb_func, <void *>c_inst_id)

    def cancel_callback(self):
        inst_id = _to_bytes(str(id(self)))

        if inst_id in _callbacks:
            self.thisptr.cancelCallback()
            del _callbacks[inst_id]


cdef class MidiOut:
    """Midi output client interface."""
    cdef RtMidiOut *thisptr

    def __cinit__(self, Api rtapi=UNSPECIFIED,
            string name="RtMidi Output Client"):
        name = _to_bytes(name)
        self.thisptr = new RtMidiOut(rtapi, name)

    def __dealloc__(self):
        del self.thisptr

    def get_current_api(self):
        return self.thisptr.getCurrentApi()

    def get_port_count(self):
        return self.thisptr.getPortCount()

    def get_port_name(self, unsigned int port):
        cdef string name = self.thisptr.getPortName(port)

        if len(name):
            return name.decode('utf-8')
        else:
            return None

    def get_ports(self):
        return [self.get_port_name(p) for p in range(self.get_port_count())]

    def open_port(self, unsigned int port=0, string name="RtMidi Output"):
        name = _to_bytes(name)
        self.thisptr.openPort(port, name)

    def open_virtual_port(self, string name="RtMidi Output"):
        name = _to_bytes(name)
        self.thisptr.openVirtualPort(name)

    def close_port(self):
        self.thisptr.closePort()

    def send_message(self, message):
        cdef vector[unsigned char] msg_v
        cdef int i

        for i from 0 <= i < len(message):
            msg_v.push_back(message[i])

        self.thisptr.sendMessage(&msg_v)
