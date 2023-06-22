#!/usr/bin/env python
"""Unit tests for the rtmidi module."""

import time
import unittest

import pytest

import rtmidi


class BaseTests:
    NOTE_ON = [0x90, 48, 100]
    NOTE_OFF = [0x80, 48, 16]
    IN_CLIENT_NAME = "RtMidiTestCase In"
    OUT_CLIENT_NAME = "RtMidiTestCase Out"
    IN_PORT_NAME = 'testin'
    OUT_PORT_NAME = 'testout'
    DELAY = 0.1
    API = rtmidi.API_UNSPECIFIED

    def setUp(self):
        self.midi_in = rtmidi.MidiIn(rtapi=self.API, name=self.IN_CLIENT_NAME)
        self.midi_out = rtmidi.MidiOut(rtapi=self.API, name=self.OUT_CLIENT_NAME)

    def tearDown(self):
        self.midi_in.close_port()
        del self.midi_in
        self.midi_out.close_port()
        del self.midi_out

    def test_is_port_open(self):
        assert not self.midi_in.is_port_open()
        self.midi_in.open_port(0)
        assert self.midi_in.is_port_open()
        self.midi_in.close_port()
        assert not self.midi_in.is_port_open()

        assert not self.midi_out.is_port_open()
        self.midi_out.open_port(0)
        assert self.midi_out.is_port_open()
        self.midi_out.close_port()
        assert not self.midi_out.is_port_open()

    def test_get_current_api(self):
        assert self.midi_in.get_current_api() == self.API
        assert self.midi_out.get_current_api() == self.API


class VirtualPortsSupportedTests:
    def test_is_port_open_virtual(self):
        # virtual ports can't be closed
        assert not self.midi_in.is_port_open()
        self.midi_in.open_virtual_port()
        assert self.midi_in.is_port_open()
        self.midi_in.close_port()
        assert self.midi_in.is_port_open()

        assert not self.midi_out.is_port_open()
        self.midi_out.open_virtual_port()
        assert self.midi_out.is_port_open()
        self.midi_out.close_port()
        assert self.midi_out.is_port_open()

    def test_send_and_get_message(self):
        self.set_up_loopback()
        self.midi_out.send_message(self.NOTE_ON)
        self.midi_out.send_message(self.NOTE_OFF)
        time.sleep(self.DELAY)
        message_1, _ = self.midi_in.get_message()
        message_2, _ = self.midi_in.get_message()
        self.assertEqual(message_1, self.NOTE_ON)
        self.assertEqual(message_2, self.NOTE_OFF)

    def test_callback(self):
        messages = []

        def callback(event, data):
            messages.append((event[0], data))

        self.set_up_loopback()
        self.midi_in.set_callback(callback, data=42)
        self.midi_out.send_message(self.NOTE_ON)
        self.midi_out.send_message(self.NOTE_OFF)
        time.sleep(self.DELAY)
        self.assertEqual(messages[0], (self.NOTE_ON, 42))
        self.assertEqual(messages[1], (self.NOTE_OFF, 42))

        self.midi_in.cancel_callback()
        messages = []
        self.midi_out.send_message(self.NOTE_ON)
        self.midi_out.send_message(self.NOTE_OFF)
        time.sleep(self.DELAY)
        self.assertEqual(messages, [])

    def set_up_loopback(self):
        # TODO: find better solution than this hack-ish strategy to find out
        # the port number of the virtual output port, which we have to use,
        # because for ALSA virtual ports, their name includes the client id.
        # See: https://github.com/thestk/rtmidi/issues/88
        ports_before = self.midi_in.get_ports()
        self.midi_out.open_virtual_port(name=self.OUT_PORT_NAME)
        ports_after = self.midi_in.get_ports()
        self.midi_out_port_name = list(set(ports_after).difference(ports_before))[0]

        for portnum, port in enumerate(ports_after):
            if port == self.midi_out_port_name:
                self.midi_in.open_port(portnum)
                break
        else:
            raise IOError("Could not find MIDI output port.")


class VirtualPortsUnsupportedTests:
    def test_is_port_open_virtual(self):
        # virtual ports can't be closed
        assert not self.midi_in.is_port_open()
        self.assertRaises(NotImplementedError, self.midi_in.open_virtual_port)


class SetPortNameSupportedTests:
    def test_set_port_name_supported(self):
        self.midi_out.open_virtual_port(name=self.OUT_PORT_NAME)
        found = False
        for port in self.midi_in.get_ports():
            client, port = port.split(':', 1)
            if client.startswith(self.OUT_CLIENT_NAME) and port.startswith(self.OUT_PORT_NAME):
                found = True
                break

        assert found

        self.midi_out.set_port_name("new_port")

        found = False
        for port in self.midi_in.get_ports():
            client, port = port.split(':', 1)
            if client.startswith(self.OUT_CLIENT_NAME) and port.startswith("new_port"):
                found = True
                break

        assert found


class SetPortNameUnsupportedTests:
    def test_set_port_name_unsupported(self):
        self.assertRaises(NotImplementedError, self.midi_out.set_port_name, "new_port")


class SetClientNameSupportedTests:
    def test_set_client_name_supported(self):
        self.midi_out.open_virtual_port(name=self.OUT_PORT_NAME)
        found = False
        for port in self.midi_in.get_ports():
            client, port = port.split(':', 1)
            if client.startswith(self.OUT_CLIENT_NAME) and port.startswith(self.OUT_PORT_NAME):
                found = True
                break

        assert found

        self.midi_out.set_client_name("new_client")

        found = False
        for port in self.midi_in.get_ports():
            client, port = port.split(':', 1)
            if client.startswith("new_client") and port.startswith(self.OUT_PORT_NAME):
                found = True
                break

        assert found


class SetClientNameUnsupportedTests:
    def test_set_client_name_unsupported(self):
        self.assertRaises(NotImplementedError, self.midi_out.set_client_name, "new_client")


if rtmidi.API_LINUX_ALSA in rtmidi.get_compiled_api():
    class ALSATestCase(BaseTests, SetPortNameSupportedTests, SetClientNameSupportedTests,
                       VirtualPortsSupportedTests, unittest.TestCase):
        API = rtmidi.API_LINUX_ALSA


if rtmidi.API_UNIX_JACK in rtmidi.get_compiled_api():
    @pytest.mark.jack
    class JACKTestCase(BaseTests, SetPortNameSupportedTests, SetClientNameUnsupportedTests,
                       VirtualPortsSupportedTests, unittest.TestCase):
        API = rtmidi.API_UNIX_JACK


if rtmidi.API_MACOSX_CORE in rtmidi.get_compiled_api():
    class CoreMIDITestCase(BaseTests, SetPortNameUnsupportedTests, SetClientNameUnsupportedTests,
                           VirtualPortsSupportedTests, unittest.TestCase):
        API = rtmidi.API_MACOSX_CORE


if rtmidi.API_WINDOWS_MM in rtmidi.get_compiled_api():
    class WindowsMMTestCase(BaseTests, SetPortNameUnsupportedTests, SetClientNameUnsupportedTests,
                            VirtualPortsUnsupportedTests, unittest.TestCase):
        API = rtmidi.API_WINDOWS_MM


if __name__ == '__main__':
    unittest.main()
