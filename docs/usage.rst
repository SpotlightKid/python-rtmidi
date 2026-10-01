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

Threads
=======

Calls on one ``MidiIn`` or ``MidiOut`` instance are serialized, so several
threads can share an instance, for example to send messages through one
``MidiOut``. On a free-threaded Python build (3.13t and later),
**python-rtmidi** does not re-enable the GIL, and calls on different instances
run in parallel.

The callback set with ``MidiIn.set_callback`` runs on a thread started by the
MIDI backend, not on one of your threads:

* A new callback set with ``set_callback`` gets the next message. But a
  message that is being delivered while ``cancel_callback`` or ``close_port``
  is called may still reach the old callback after that call returns.
* ``MidiIn.close_port`` and ``MidiIn.delete`` wait for that thread to stop.
  ``close_port`` may be called from inside the callback; ``delete`` may not
  (``InvalidUseError``). While ``close_port`` waits, ``get_message`` returns
  ``None`` and most other calls on the same instance from other threads raise
  ``InvalidUseError``.

``delete`` may be called while another thread is in a call on the same
instance: the C++ instance is then destroyed when that call returns. After
``delete``, methods raise ``InvalidUseError``, except ``get_current_api`` and
``is_port_open``, which still work, and ``close_port`` and ``delete``, which
do nothing.

Reference cycles through an instance's callbacks (for example a callback whose
``data`` is the ``MidiIn`` itself) are collected by the garbage collector like
any other; a message being delivered at that moment is dropped. If the last
reference to a ``MidiIn`` goes away in its own input callback, the C++
instance is destroyed on another thread, which waits for the callback to
return.

More usage examples can be found in the examples_ and tests_ directories
of the source repository.


.. _tests: https://github.com/SpotlightKid/python-rtmidi/tree/master/tests
.. _examples: https://github.com/SpotlightKid/python-rtmidi/tree/master/examples
