# -*- coding: utf-8 -*-
#
# osc2midi/device.py
#
"""MIDI device abstraction classes."""

__all__ = [
    "RtMidiDevice"
]

import logging
import time

import rtmidi

log = logging.getLogger(__name__)


class RtMidiDevice(object):
    """Provides a common API for different MIDI driver implementations."""

    def __init__(self, name="RtMidiDevice", port=None, portname=None):
        self.name = name
        self.port = port
        self.portname = portname
        self._output = None

    def __str__(self):
        return self.name

    def open_output(self):
        self._output = rtmidi.MidiOut(name=self.name)
        if self.port is None:
            if self.portname is None:
                self.portname = "RtMidi Virtual Output"
            log.info("Opening virtual MIDI output port.")
            self._output.open_virtual_port(self.portname)
        else:
            if self.portname is None:
                self.portname = self._output.get_port_name(self.port)
            log.info("Opening MIDI output port #%i (%s).",
                self.port, self.portname)
            self._output.open_port(self.port, self.portname)

    def close_output(self):
        if self._output is not None:
            self._output.close_port()

    def send(self, events):
        if self._output:
            for ev in events:
                self._output.send_message(ev)

    def send_sysex(self, msg):
        if self._output:
            self._output.send_message([ord(c) for c in msg])

    @classmethod
    def time(cls):
        return time.time() / 1000.
