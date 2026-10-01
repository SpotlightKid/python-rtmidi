#!/usr/bin/env python
"""Tests for using MidiIn / MidiOut instances from several threads.

They matter most on free-threaded Python builds, where no GIL serializes calls
into the extension module, but they run on every build. They use virtual ports,
so they are skipped on backends without them (Windows MM).

Each stress test runs for ``RTMIDI_STRESS_SECONDS`` (default 1) seconds.

"""

import gc
import os
import subprocess
import sys
import sysconfig
import textwrap
import threading
import time
import unittest

import pytest

import rtmidi


def _find_api():
    for api in (rtmidi.API_LINUX_ALSA, rtmidi.API_MACOSX_CORE):
        if api in rtmidi.get_compiled_api():
            try:
                rtmidi.MidiOut(api).delete()
            except rtmidi.SystemError:  # e.g. no ALSA sequencer device
                return None
            return api


API = _find_api()

DURATION = float(os.environ.get("RTMIDI_STRESS_SECONDS", "1"))
# Port names are system-wide; this keeps concurrent test runs apart.
PREFIX = "rtmidi-thr-%d" % os.getpid()
# How long a thread may take to finish after it was told to stop, before the
# test counts it as hung.
JOIN_TIMEOUT = 30
FREE_THREADED = bool(sysconfig.get_config_var("Py_GIL_DISABLED"))


def find_port(midi, name, timeout=2):
    # Listing ports is not atomic: while other clients come and go (other
    # threads here, or other programs), one can be missed or fail to list.
    deadline = time.monotonic() + timeout

    while True:
        try:
            ports = midi.get_ports()
        except rtmidi.InvalidPortError:
            ports = []

        for i, port in enumerate(ports):
            if port and name in port:
                return i

        if time.monotonic() > deadline:
            raise AssertionError("port %r not found in %r" % (name, ports))

        time.sleep(0.01)


def open_named(midi, name):
    """Open the port with ``name`` in its name on ``midi``."""
    # By number: another client (another thread or program) adding or removing
    # a port in between can make the number invalid, so look it up again.
    deadline = time.monotonic() + 2

    while True:
        try:
            return midi.open_port(find_port(midi, name))
        except rtmidi.InvalidPortError:
            if time.monotonic() > deadline:
                raise


def port_names():
    """Names of all ports that a MidiIn or MidiOut can list."""
    names = []
    probes = [rtmidi.MidiOut(API), rtmidi.MidiIn(API)]

    try:
        for probe in probes:
            try:
                names.extend(p for p in probe.get_ports() if p)
            except rtmidi.InvalidPortError:  # one vanished while listing
                pass
    finally:
        for probe in probes:
            probe.delete()

    return names


def has_port(name):
    return any(name in p for p in port_names())


def run_threads(*targets, duration=DURATION):
    """Run each ``target(stop)`` in its own thread for ``duration`` seconds.

    ``stop`` is a ``threading.Event``; targets loop until it is set. Re-raises
    the first exception a target raised, and fails if a thread does not finish.

    """
    stop = threading.Event()
    errors = []

    def wrap(target):
        def run():
            try:
                target(stop)
            except BaseException as exc:
                errors.append(exc)
                stop.set()
        return run

    threads = [threading.Thread(target=wrap(t), daemon=True) for t in targets]

    for thread in threads:
        thread.start()

    stop.wait(duration)
    stop.set()

    for thread in threads:
        thread.join(JOIN_TIMEOUT)

    hung = [t for t in threads if t.is_alive()]

    if errors:
        raise errors[0]

    assert not hung, "%d thread(s) did not finish (deadlock?)" % len(hung)


@unittest.skipIf(not FREE_THREADED, "free-threaded Python build only")
class GILTests(unittest.TestCase):
    def test_import_keeps_gil_disabled(self):
        code = textwrap.dedent("""
            import sys, warnings
            warnings.simplefilter("error", RuntimeWarning)
            import rtmidi
            print(sys._is_gil_enabled())
        """)
        env = {k: v for k, v in os.environ.items() if k != "PYTHON_GIL"}
        out = subprocess.run([sys.executable, "-c", code], env=env, check=True,
                             capture_output=True, text=True).stdout
        self.assertEqual(out.strip(), "False")


@unittest.skipIf(API is None, "needs a backend with virtual ports")
# Polling get_message() while another thread has set a callback warns.
@pytest.mark.filterwarnings("ignore:.*a user callback is currently set:UserWarning")
class ThreadTests(unittest.TestCase):

    def setUp(self):
        self.objects = []

    def tearDown(self):
        for obj in self.objects:
            obj.delete()

    def midi_in(self):
        obj = rtmidi.MidiIn(API, name="RtMidiThreadTest In")
        self.objects.append(obj)
        return obj

    def midi_out(self):
        obj = rtmidi.MidiOut(API, name="RtMidiThreadTest Out")
        self.objects.append(obj)
        return obj

    def loopback(self, name):
        """Return (midi_in, midi_out): a virtual input port and an output
        connected to it."""
        midi_in = self.midi_in()
        midi_in.open_virtual_port(name)
        midi_out = self.midi_out()
        open_named(midi_out, name)
        return midi_in, midi_out

    def test_shared_midiout(self):
        # Several threads send through one MidiOut; every message that arrives
        # must be one that was sent, intact.
        midi_in, midi_out = self.loopback(PREFIX + "-shared")
        received = []
        midi_in.set_callback(lambda event, data: received.append(event[0]))
        sent = [[0x90, note, 100] for note in range(4)]

        def sender(message):
            def run(stop):
                while not stop.is_set():
                    midi_out.send_message(message)
                    time.sleep(0.0005)
            return run

        run_threads(*[sender(m) for m in sent])
        time.sleep(0.1)
        self.assertTrue(received)
        self.assertEqual([m for m in received if m not in sent], [])

    def test_replace_callback_while_receiving(self):
        # Replacing a callback must never free one that the input thread is
        # about to call. (Not cancel_callback() here: RtMidi itself does not
        # synchronize cancelling a callback with its input thread.)
        midi_in, midi_out = self.loopback(PREFIX + "-callback")
        wrong = []

        def make_callback(expected):
            def callback(event, data):
                if data != expected:
                    wrong.append((expected, data))
            return callback

        def flood(stop):
            while not stop.is_set():
                midi_out.send_message([0x90, 60, 100])

        def swap(n):
            def run(stop):
                while not stop.is_set():
                    midi_in.set_callback(make_callback(n), n)
            return run

        run_threads(flood, swap(1), swap(2))
        self.assertEqual(wrong, [])

    def test_close_port_while_receiving(self):
        # close_port() waits for the input thread, which may be waiting to run
        # a callback. This used to deadlock on regular builds, too.
        # The MidiIn is closed by the thread that created it: when another
        # thread closes it, RtMidi's ALSA backend can join the wrong thread and
        # hang (thestk/rtmidi#395), which is not what this test is about.
        source = self.midi_out()
        source.open_virtual_port(PREFIX + "-close")
        shared = []
        created = threading.Event()
        received = []

        def flood(stop):
            while not stop.is_set():
                source.send_message([0x90, 60, 100])

        def open_close(stop):
            midi_in = self.midi_in()
            shared.append(midi_in)
            created.set()

            while not stop.is_set():
                open_named(midi_in, PREFIX + "-close")
                midi_in.set_callback(lambda event, data: received.append(event))
                time.sleep(0.001)
                midi_in.close_port()

        def poll(stop):
            if not created.wait(JOIN_TIMEOUT):
                return

            midi_in = shared[0]

            while not stop.is_set():
                try:
                    midi_in.get_message()
                    midi_in.ignore_types(timing=True)
                except rtmidi.InvalidUseError:
                    pass  # close_port() in progress in another thread

        run_threads(flood, open_close, poll)
        self.assertTrue(received)

    def test_delete_while_in_use(self):
        # Deleted by the thread that created them; see
        # test_close_port_while_receiving.
        shared = {}
        created = threading.Event()
        started = threading.Event()

        def use(name, *calls):
            def run(stop):
                if not created.wait(JOIN_TIMEOUT):
                    return

                obj = shared[name]
                started.set()

                while not stop.is_set():
                    try:
                        for call in calls:
                            call(obj)
                    except rtmidi.InvalidUseError:
                        if not obj.is_deleted:
                            raise
                        return
            return run

        def create_and_delete(stop):
            shared["in"], shared["out"] = self.loopback(PREFIX + "-delete")
            shared["in"].set_callback(lambda event, data: None)
            created.set()
            started.wait(JOIN_TIMEOUT)
            time.sleep(DURATION / 2)
            shared["out"].delete()
            shared["in"].delete()

        run_threads(
            use("out", lambda o: o.send_message([0x90, 60, 100]),
                lambda o: o.get_port_count()),
            use("in", lambda o: o.get_message(), lambda o: o.get_port_count(),
                lambda o: o.set_callback(lambda event, data: None)),
            create_and_delete,
        )

        for obj in (shared["in"], shared["out"]):
            self.assertTrue(obj.is_deleted)
            obj.close_port()  # a no-op after delete()
            obj.delete()  # likewise
            self.assertRaises(rtmidi.InvalidUseError, obj.get_port_count)

    def test_error_callback_replaced_concurrently(self):
        midi_out = self.midi_out()
        wrong = []

        def make_handler(expected):
            def handler(etype, msg, data):
                if data != expected:
                    wrong.append((expected, data))
            return handler

        def trigger(stop):
            while not stop.is_set():
                midi_out.open_port(9999)  # invalid port: calls the error callback
                midi_out.close_port()  # the handler does not raise

        def swap(n):
            def run(stop):
                while not stop.is_set():
                    midi_out.set_error_callback(make_handler(n), n)
            return run

        midi_out.set_error_callback(make_handler(0), 0)
        run_threads(trigger, swap(1), swap(2))
        self.assertEqual(wrong, [])

    def test_create_and_drop_in_threads(self):
        # Dropping the last reference must close the client, including its
        # input thread, also when a callback is set and messages arrive.
        # Ports are opened by number, and numbers shift as other threads add
        # and remove ports, so do that under a lock.
        port_lock = threading.Lock()

        def churn(n):
            def run(stop):
                name = "%s-churn-%d" % (PREFIX, n)
                while not stop.is_set():
                    midi_in = rtmidi.MidiIn(API)
                    midi_in.set_callback(lambda event, data: None)
                    midi_out = rtmidi.MidiOut(API)
                    with port_lock:
                        midi_in.open_virtual_port(name)
                        open_named(midi_out, name)
                    midi_out.send_message([0x90, 60, 100])
                    with port_lock:
                        del midi_in, midi_out
            return run

        run_threads(*[churn(n) for n in range(3)])
        ports = rtmidi.MidiOut(API).get_ports()
        self.assertEqual([p for p in ports if PREFIX + "-churn" in p], [])


@unittest.skipIf(API is None, "needs a backend with virtual ports")
class DeleteTests(unittest.TestCase):

    def test_delete_while_error_callback_blocks(self):
        # A blocking error callback releases the critical section (and, on a
        # regular build, the GIL); delete() must not free the C++ instance
        # under the call that is still in it.
        midi_out = rtmidi.MidiOut(API)
        entered = threading.Event()

        def slow_handler(etype, msg, data):
            entered.set()
            time.sleep(0.2)

        midi_out.set_error_callback(slow_handler)
        opener = threading.Thread(target=midi_out.open_port, args=(9999,))
        opener.start()
        self.assertTrue(entered.wait(JOIN_TIMEOUT))
        midi_out.delete()
        opener.join(JOIN_TIMEOUT)
        self.assertFalse(opener.is_alive())
        self.assertTrue(midi_out.is_deleted)
        self.assertRaises(rtmidi.InvalidUseError, midi_out.get_port_count)

    def test_delete_while_closing(self):
        # close_port() waits for a callback that is still running; delete()
        # from another thread meanwhile must not raise, and the C++ instance
        # goes away once close_port() returns.
        midi_in = rtmidi.MidiIn(API)
        source = rtmidi.MidiOut(API)
        source.open_virtual_port(PREFIX + "-delclose")
        open_named(midi_in, PREFIX + "-delclose")
        in_callback = threading.Event()
        closing = threading.Event()
        results = []

        def slow_callback(event, data):
            in_callback.set()
            time.sleep(0.3)

        def delete_while_closing():
            closing.wait(JOIN_TIMEOUT)
            time.sleep(0.05)
            try:
                results.append(midi_in.get_message())  # closing: None
                midi_in.delete()
            except Exception as exc:
                results.append(exc)

        midi_in.set_callback(slow_callback)
        source.send_message([0x90, 60, 100])
        self.assertTrue(in_callback.wait(JOIN_TIMEOUT))
        deleter = threading.Thread(target=delete_while_closing)
        deleter.start()
        closing.set()
        midi_in.close_port()  # in the creating thread; see test_close_port...
        deleter.join(JOIN_TIMEOUT)
        self.assertEqual(results, [None])
        self.assertTrue(midi_in.is_deleted)
        source.delete()

    def test_delete_in_own_callback(self):
        # The destructor waits for the input thread, so the callback running
        # on it cannot delete its own instance.
        midi_in = rtmidi.MidiIn(API)
        midi_in.open_virtual_port(PREFIX + "-selfdelete")
        midi_out = rtmidi.MidiOut(API)
        open_named(midi_out, PREFIX + "-selfdelete")
        raised = []
        done = threading.Event()

        def callback(event, data):
            try:
                midi_in.delete()
            except rtmidi.InvalidUseError as exc:
                raised.append(exc)
            done.set()

        midi_in.set_callback(callback)
        midi_out.send_message([0x90, 60, 100])
        self.assertTrue(done.wait(JOIN_TIMEOUT))
        self.assertEqual(len(raised), 1)
        self.assertFalse(midi_in.is_deleted)
        midi_in.delete()
        midi_out.delete()


@unittest.skipIf(API is None, "needs a backend with virtual ports")
class DeallocTests(unittest.TestCase):
    def test_del_closes_client(self):
        # The C++ instance used to be leaked on deallocation, leaving its
        # ports open and its input thread running.
        midi_in = rtmidi.MidiIn(API)
        midi_in.set_callback(lambda event, data: None)
        midi_in.open_virtual_port(PREFIX + "-dealloc")
        probe = rtmidi.MidiOut(API)
        self.assertTrue(any(PREFIX + "-dealloc" in p for p in probe.get_ports()))
        del midi_in
        self.assertFalse(any(PREFIX + "-dealloc" in p for p in probe.get_ports()))
        probe.delete()

    def test_close_port_breaks_callback_cycle(self):
        # close_port() releases the input callback, so a cycle through it does
        # not need the garbage collector.
        midi_in = rtmidi.MidiIn(API)
        midi_in.open_virtual_port(PREFIX + "-cycle")
        midi_in.set_callback(lambda event, data: None, midi_in)
        midi_in.close_port()
        del midi_in
        self.assertFalse(has_port(PREFIX + "-cycle"))

    def check_collected(self, name, make):
        # ``make(name)`` returns an instance with an open virtual port ``name``
        # that is part of a reference cycle, which only the garbage collector
        # can break.
        gc.collect()
        gc.disable()  # not before we say so

        try:
            instance = make(name)
            self.assertTrue(has_port(name))
            del instance
            self.assertTrue(has_port(name), "not in a cycle")
            gc.collect()
            self.assertFalse(has_port(name), "cycle was not collected")
        finally:
            gc.enable()

    def test_gc_collects_input_callback_data_cycle(self):
        def make(name):
            midi_in = rtmidi.MidiIn(API)
            midi_in.open_virtual_port(name)
            midi_in.set_callback(lambda event, data: None, midi_in)
            return midi_in

        self.check_collected(PREFIX + "-gc-data", make)

    def test_gc_collects_subclass_bound_method_cycle(self):
        class Receiver(rtmidi.MidiIn):
            def start(self, name):
                self.open_virtual_port(name)
                self.set_callback(self.on_message)  # self -> bound method -> self
                self.myself = self  # a cycle through __dict__ as well

            def on_message(self, event, data):
                pass

        def make(name):
            receiver = Receiver(API)
            receiver.start(name)
            return receiver

        self.check_collected(PREFIX + "-gc-method", make)

    def test_gc_collects_error_callback_data_cycle(self):
        def make_in(name):
            midi_in = rtmidi.MidiIn(API)
            midi_in.open_virtual_port(name)
            midi_in.set_error_callback(lambda *args: None, midi_in)
            return midi_in

        def make_out(name):
            midi_out = rtmidi.MidiOut(API)
            midi_out.open_virtual_port(name)
            midi_out.set_error_callback(lambda *args: None, midi_out)
            return midi_out

        self.check_collected(PREFIX + "-gc-errin", make_in)
        self.check_collected(PREFIX + "-gc-errout", make_out)

    def test_gc_keeps_callbacks_of_live_instance(self):
        # An instance in a cycle that is still referenced keeps its callbacks.
        received = []
        midi_in = rtmidi.MidiIn(API)
        midi_in.open_virtual_port(PREFIX + "-gc-live")
        midi_in.set_callback(lambda event, data: received.append(event[0]), midi_in)
        gc.collect()
        midi_out = rtmidi.MidiOut(API)
        open_named(midi_out, PREFIX + "-gc-live")
        midi_out.send_message([0x90, 60, 100])
        deadline = time.monotonic() + JOIN_TIMEOUT

        while not received and time.monotonic() < deadline:
            time.sleep(0.01)

        self.assertEqual(received, [[0x90, 60, 100]])
        midi_in.delete()
        midi_out.delete()

    def test_gc_collects_cycles_while_receiving(self):
        # The collector clears an instance's callbacks while its input thread
        # may be picking them up: another thread floods its port, a second one
        # collects garbage, and each instance is dropped in the middle of it.
        delivered = []

        class Receiver(rtmidi.MidiIn):
            received = 0

            def start(self, name):
                self.open_virtual_port(name)
                self.set_callback(self.on_message, self)

            def on_message(self, event, data):
                self.received += 1
                delivered.append(1)

        def flood(source, stop):
            while not stop.is_set():
                try:
                    source.send_message([0x90, 60, 100])
                except rtmidi.RtMidiError:
                    return

        names = []

        def churn(stop):
            while not stop.is_set():
                name = "%s-gc-race-%d" % (PREFIX, len(names))
                names.append(name)
                receiver = Receiver(API)
                receiver.start(name)
                source = rtmidi.MidiOut(API)
                open_named(source, name)
                flooding = threading.Event()
                sender = threading.Thread(target=flood, args=(source, flooding))
                sender.start()
                deadline = time.monotonic() + JOIN_TIMEOUT

                while not receiver.received and time.monotonic() < deadline:
                    time.sleep(0.001)

                del receiver
                gc.collect()
                flooding.set()
                sender.join(JOIN_TIMEOUT)
                source.delete()

        def collect(stop):
            while not stop.is_set():
                gc.collect()
                time.sleep(0.0005)

        run_threads(churn, collect)
        self.assertTrue(delivered)
        left = names
        deadline = time.monotonic() + JOIN_TIMEOUT

        while left and time.monotonic() < deadline:
            gc.collect()
            left = [n for n in names if has_port(n)]
            time.sleep(0.05)

        self.assertEqual(left, [], "instances not destroyed")


if __name__ == "__main__":
    unittest.main()
