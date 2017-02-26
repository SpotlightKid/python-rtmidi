#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Wrap MidiOut to add convenience methods for sending common MIDI events."""

import time

import rtmidi
from rtmidi.midiconstants import NOTE_OFF, NOTE_ON, PROGRAM_CHANGE


class MidiOutWrapper:
    def __init__(self, midi, ch=1):
        self.channel = ch
        self._midi = midi

    def channel_message(self, command, *data, ch=None):
        """Send a MIDI channel mode message."""
        command = (command & 0xf0) | ((ch if ch else self.channel) - 1 & 0xf)
        msg = [command] + [value & 0x7f for value in data]
        self._midi.send_message(msg)

    def note_off(self, note, velocity=0, ch=None):
        """Send a 'Note Off' message."""
        self.channel_message(NOTE_OFF, note, velocity, ch=ch)

    def note_on(self, note, velocity=127, ch=None):
        """Send a 'Note On' message."""
        self.channel_message(NOTE_ON, note, velocity, ch=ch)

    def program_change(self, program, ch=None):
        """Send a 'Program Change' message."""
        self.channel_message(PROGRAM_CHANGE, program, ch=ch)

    # add more convenience methods for other common MIDI events here...


if __name__ == '__main__':
    mout = rtmidi.MidiOut()
    mout.open_virtual_port()
    input('Connect to new MIDI port and then press key...')
    mw = MidiOutWrapper(mout, ch=3)
    mw.program_change(40)
    mw.note_on(60)
    time.sleep(1)
    mw.note_off(60)
