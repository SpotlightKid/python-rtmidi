#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the error conditions"""

import unittest

import rtmidi
from rtmidi import InvalidPortError, InvalidUseError


class TestErrors(unittest.TestCase):

    INVALID_PORT_NUMBER = 9999
    INVALID_NAME_TYPES = (0, 666, 3.141, object)

    def setUp(self):
        self.midi_out = rtmidi.MidiOut()
        self.midi_in = rtmidi.MidiIn()

    def test_midiout_invalid_client_name_type(self):
        for name in self.INVALID_NAME_TYPES:
            with self.assertRaises(TypeError):
                rtmidi.MidiOut(rtapi=rtmidi.API_RTMIDI_DUMMY, name=name)

    def test_midiin_invalid_client_name_type(self):
        for name in self.INVALID_NAME_TYPES:
            with self.assertRaises(TypeError):
                rtmidi.MidiIn(rtapi=rtmidi.API_RTMIDI_DUMMY, name=name)

    def test_midiout_open_invalid_port(self):
        with self.assertRaises(InvalidPortError):
            self.midi_out.open_port(self.INVALID_PORT_NUMBER)

    def test_midiin_open_invalid_port(self):
        with self.assertRaises(InvalidPortError):
            self.midi_in.open_port(self.INVALID_PORT_NUMBER)

    def test_midiout_open_invalid_port_name_type(self):
        for name in self.INVALID_NAME_TYPES:
            with self.assertRaises(TypeError):
                self.midi_out.open_port(name=name)

    def test_midiin_open_invalid_port_name_type(self):
        for name in self.INVALID_NAME_TYPES:
            with self.assertRaises(TypeError):
                self.midi_in.open_port(name=name)

    def test_midiout_double_open_port(self):
        self.midi_out.open_port()
        with self.assertRaises(InvalidUseError):
            self.midi_out.open_port()

    def test_midiin_double_open_port(self):
        self.midi_in.open_port()
        with self.assertRaises(InvalidUseError):
            self.midi_in.open_port()

    def test_midiout_double_open_virtual_port(self):
        self.midi_out.open_virtual_port()
        with self.assertRaises(InvalidUseError):
            self.midi_out.open_virtual_port()

    def test_midiin_double_open_virtual_port(self):
        self.midi_in.open_virtual_port()
        with self.assertRaises(InvalidUseError):
            self.midi_in.open_virtual_port()


if __name__ == '__main__':
    unittest.main()
