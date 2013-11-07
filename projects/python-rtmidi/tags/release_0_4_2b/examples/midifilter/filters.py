# -*- coding: utf-8 -*-
#
# midifilter.filters.py
#
"""Collection MIDI filter classes."""

__all__ = [
    'MidiFilter',
    'Transpose',
    'MapControllerValue',
    'MonoPressureToCC'
]

from rtmidi.midiconstants import *


class MidiFilter(object):
    """ABC for midi filters."""
    def __init__(self, *args, **kwargs):
        self.args = args
        self.__dict__.update(kwargs)

    def process(self, event):
        """Process one event.

        Receives a list of MIDI event tuples (message, timestamp).

        Must return an iterable of event tuples.

        """
        raise NotImplementedError("Abstract method 'process()'.")


class Transpose(MidiFilter):
    """Transpose note on/off events."""

    event_types = (NOTE_ON, NOTE_OFF)

    def process(self, events):
        for event, timestamp in events:
            if event[0] & 0xF0 in self.event_types:
                # transpose note value (data byte 1)
                event[1] = max(0, min(127, event[1] + self.transpose)) & 0x7F
            yield event, timestamp


class MapControllerValue(MidiFilter):
    """Map controller values to min/max range."""

    event_types = (CONTROLLER_CHANGE,)

    def __init__(self, cc, min_, max_, *args, **kwargs):
        super(MapControllerValue, self).__init__(*args, **kwargs)
        self.cc = cc
        self.min = min_
        self.max = max_

    def process(self, events):
        for event, timestamp in events:
            # check controller number
            if event[0] & 0xF0 in self.event_types and event[1] == self.cc:
                # map controller value
                event[2] = int(self._map(event[2]))
            yield event, timestamp

    def _map(self, value):
        return value * (self.max - self.min) / 127. + self.min


class MonoPressureToCC(MidiFilter):
    """Change mono pressure events into controller change events."""

    event_types = (CHANNEL_PRESSURE,)

    def process(self, events):
        for event, timestamp in events:
            if event[0] & 0xF0 in self.event_types:
                channel = event[0] & 0xF
                event = [CONTROLLER_CHANGE | channel, self.cc, event[1]]
            yield event, timestamp
