# -*- coding: utf-8 -*-
#
# osc2midi/midievent.py
#
"""MIDI event classes."""

__all__ = ('MidiEvent',)


class MidiEvent(object):
    """Generic MIDI event base class.

    This also serves as a factory for more specific event (sub-)classes.

    Event classes can be registered with this class by calling the 'register'
    class method, passing the class to register. The class must have a 'type'
    attribute, which corresponds to a MIDI status byte. Event objects are
    instantiated by calling the 'fromdata' factory class method, passing the
    MIDI status byte (with the channel bits stripped off for channel voice and
    mode messages), the event data bytes and, optionally, the channel number.
    The factory method then returns an event instance selected based on the
    registered classes and the status byte.

    """

    _event_register = {}

    type = 0xFE

    def __init__(self, type=None, **kwargs):
        if type is not None:
            self.type = type
        self.__dict__.update(kwargs)

    @classmethod
    def register(cls, eventclass):
        cls._event_register[eventclass.type] = eventclass

    @classmethod
    def fromdata(cls, status, data=None, channel=None, timestamp=None):
        if status >= 0xF0:
            status = status & 0xFF
        else:
            status = status & 0xF0
        eventclass = cls._event_register.get(status, cls)
        return eventclass(type=status, data=data or [], channel=channel,
                          timestamp=timestamp)

    def __str__(self):
        s = "Status: %02X " % self.type
        if self.channel is not None:
            s += "CH: %02i " % self.channel
        s += "Data: " + " ".join(["%-3i (%02X)" % (i, i) for i in self.data])
        return s
