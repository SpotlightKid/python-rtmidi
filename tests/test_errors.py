#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the error conditions"""

import unittest

import rtmidi


class TestErrors(unittest.TestCase):

    INVALID_PORT_NUMBER = 9999

    def setUp(self):
        self.midi_out = rtmidi.MidiOut()
        self.midi_in = rtmidi.MidiIn()

    def test_midiout_open_invalid_port(self):
        with self.assertRaises(RuntimeError):
            self.midi_out.open_port(self.INVALID_PORT_NUMBER)

    def test_midiin_open_invalid_port(self):
        with self.assertRaises(RuntimeError):
            self.midi_in.open_port(self.INVALID_PORT_NUMBER)

    def test_midiout_double_open_port(self):
        self.midi_out.open_port()
        with self.assertRaises(rtmidi.RtMidiError):
            self.midi_out.open_port()

    def test_midiin_double_open_port(self):
        self.midi_in.open_port()
        with self.assertRaises(rtmidi.RtMidiError):
            self.midi_in.open_port()

    def test_midiout_double_open_virtual_port(self):
        self.midi_out.open_virtual_port()
        with self.assertRaises(rtmidi.RtMidiError):
            self.midi_out.open_virtual_port()

    def test_midiin_double_open_virtual_port(self):
        self.midi_in.open_virtual_port()
        with self.assertRaises(rtmidi.RtMidiError):
            self.midi_in.open_virtual_port()


if __name__ == '__main__':
    unittest.main()
