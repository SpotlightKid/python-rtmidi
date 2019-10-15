========
Usage
========

Here's a quick example of how to use **python-rtmidi** to open the first
available MIDI output port and send a middle C note on MIDI channel 1:

.. code-block:: python

    import time
    import rtmidi

    midiout = rtmidi.MidiOut()
    available_ports = midiout.get_ports()

    if available_ports:
        midiout.open_port(0)
    else:
        midiout.open_virtual_port("My virtual output")

    with midiout:
        # channel 1, middle C, velocity 112
        note_on = [0x90, 60, 112]
        note_off = [0x80, 60, 0]
        midiout.send_message(note_on)
        time.sleep(0.5)
        midiout.send_message(note_off)
        time.sleep(0.1)

    del midiout

.. note:: On Windows it may be necessary to insert a small delay after the
    last message is sent and before the output port is closed, otherwise
    the message may be lost.

More usage examples can be found in the examples_ and tests_ directories
of the source repository.


.. _tests: https://github.com/SpotlightKid/python-rtmidi/tree/master/tests
.. _examples: https://github.com/SpotlightKid/python-rtmidi/tree/master/examples
