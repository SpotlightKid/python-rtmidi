#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for the rtmidi module."""

import gc
import unittest

import rtmidi


class TestDelete(unittest.TestCase):

    def setUp(self):
        self.midiout = rtmidi.MidiOut()
        self.midiin = rtmidi.MidiIn()

    def test_midiin_delete(self):
        midiin_ports = self.midiin.get_ports()
        print("Input ports:")
        print(midiin_ports)

        ports_init = self.midiout.get_ports()
        print("output ports initially:")
        print(ports_init)

        if midiin_ports:
            self.midiin.open_port(0)
        else:
            self.midiin.open_virtual_port("My virtual output")

        ports_before = self.midiout.get_ports()

        self.assertEqual(len(ports_before), len(ports_init) + 1)
        print("Output ports BEFORE deleting MidiIn instance:")
        print(ports_before)

        self.midiin.delete()

        ports_after = self.midiout.get_ports()
        print("Output ports AFTER deleting MidiIn instance:")
        print(ports_after)

        self.assertEqual(set(ports_init), set(ports_after))

    def test_midiout_delete(self):
        midiout_ports = self.midiout.get_ports()
        print("Output ports:")
        print(midiout_ports)

        ports_init = self.midiin.get_ports()
        print("Input ports initially:")
        print(ports_init)

        if midiout_ports:
            self.midiout.open_port(0)
        else:
            self.midiout.open_virtual_port("My virtual output")

        ports_before = self.midiin.get_ports()

        self.assertEqual(len(ports_before), len(ports_init) + 1)
        print("Input ports BEFORE deleting MidiOut instance:")
        print(ports_before)

        self.midiout.delete()

        ports_after = self.midiin.get_ports()
        print("Input ports AFTER deleting MidiOut instance:")
        print(ports_after)

        self.assertEqual(set(ports_init), set(ports_after))

    def test_double_delete(self):
        self.assertFalse(self.midiout.is_deleted)
        self.midiout.delete()
        self.assertTrue(self.midiout.is_deleted)
        self.midiout.delete()
        self.assertTrue(self.midiout.is_deleted)

    def test_del_after_delete(self):
        self.midiout.delete()
        self.assertTrue(self.midiout.is_deleted)
        self.assertTrue(hasattr(self, 'midiout'))
        del self.midiout
        gc.collect()
        self.assertFalse(hasattr(self, 'midiout'))


if __name__ == '__main__':
    unittest.main()
