# -*- coding: utf-8 -*-
#
# midifilter/filters.py
#
"""Collection of MIDI filter classes."""

from rtmidi.midiconstants import (BANK_SELECT_LSB, BANK_SELECT_MSB, CHANNEL_PRESSURE,
                                  CONTROLLER_CHANGE, NOTE_ON, NOTE_OFF, PROGRAM_CHANGE)


__all__ = (
    'CCToBankChange',
    'MapControllerValue',
    'MidiFilter',
    'MonoPressureToCC',
    'Transpose',
)


class MidiFilter(object):
    """ABC for midi filters."""

    event_types = ()

    def __init__(self, *args, **kwargs):
        self.args = args
        self.__dict__.update(kwargs)

    def process(self, events):
        """Process incoming events.

        Receives a list of MIDI event tuples (message, timestamp).

        Must return an iterable of event tuples.

        """
        raise NotImplementedError("Abstract method 'process()'.")

    def match(self, msg):
        return msg[0] & 0xF0 in self.event_types


class Transpose(MidiFilter):
    """Transpose note on/off events."""

    event_types = (NOTE_ON, NOTE_OFF)

    def process(self, events):
        for msg, timestamp in events:
            if self.match(msg):
                msg[1] = max(0, min(127, msg[1] + self.transpose)) & 0x7F

            yield msg, timestamp


class MapControllerValue(MidiFilter):
    """Map controller values to min/max range."""

    event_types = (CONTROLLER_CHANGE,)

    def __init__(self, cc, min_, max_, *args, **kwargs):
        super(MapControllerValue, self).__init__(*args, **kwargs)
        self.cc = cc
        self.min = min_
        self.max = max_

    def process(self, events):
        for msg, timestamp in events:
            # check controller number
            if self.match(msg) and msg[1] == self.cc:
                # map controller value
                msg[2] = int(self._map(msg[2]))

            yield msg, timestamp

    def _map(self, value):
        return value * (self.max - self.min) / 127. + self.min


class MonoPressureToCC(MidiFilter):
    """Change mono pressure events into controller change events."""

    event_types = (CHANNEL_PRESSURE,)

    def process(self, events):
        for msg, timestamp in events:
            if self.match(msg):
                channel = msg[0] & 0xF
                msg = [CONTROLLER_CHANGE | channel, self.cc, msg[1]]

            yield msg, timestamp


class CCToBankChange(MidiFilter):
    """Map controller change to a bank select, program change sequence."""

    event_types = (CONTROLLER_CHANGE,)

    def process(self, events):
        for msg, timestamp in events:
            channel = msg[0] & 0xF

            # check controller number & channel
            if (self.match(msg) and channel == self.channel and
                    msg[1] == self.cc):
                msb = [CONTROLLER_CHANGE + channel, BANK_SELECT_MSB, self.msb]
                lsb = [CONTROLLER_CHANGE + channel, BANK_SELECT_LSB, self.lsb]
                pc = [PROGRAM_CHANGE + channel, self.program]
                yield msb, timestamp
                yield lsb, timestamp
                yield pc, timestamp
            else:
                yield msg, timestamp
