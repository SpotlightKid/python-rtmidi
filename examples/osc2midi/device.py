# -*- coding: utf-8 -*-
#
# osc2midi/device.py
#
"""MIDI device abstraction classes."""

import logging
import time

from rtmidi.midiutil import open_midioutput


__all__ = ["RtMidiDevice"]
log = logging.getLogger(__name__)


class RtMidiDevice(object):
    """Provides a common API for different MIDI driver implementations."""

    def __init__(self, name="RtMidiDevice", port=None, portname=None):
        self.name = name
        self.port = port
        self.portname = portname
        self._output = None

    def __str__(self):
        return self.portname

    def open_output(self):
        self._output, self.portname = open_midioutput(self.port, interactive=False,
                                                      client_name=self.name)

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
