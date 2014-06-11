# -*- coding: utf-8 -*-
#
# test_oscdispatcher.py
#
"""Unit test-suite for oscdispatcher module."""

import logging
import re
import unittest

from osc2midi.oscdispatcher import OSCDispatcher, Pattern


class TestOSCDispatcher(unittest.TestCase):
    def setUp(self):
        self.dispatchlog = []
        self.dispatcher = OSCDispatcher(patterns=[], search_ns=self)

    def tearDown(self):
        self.dispatchlog = None

    def handler1(self, value=None):
        self.dispatchlog.append((value,))

    def handler2(self, value, cc=0, page=None):
        self.dispatchlog.append((value, cc, page))

    def test_add_pattern(self):
        """Patterns are added correctly to dispatcher."""
        pattern = (r'/(?P<s:value>\w+)$', 'ii', 'handler1')
        self.dispatcher.add_pattern(pattern)

        self.assertEqual(len(self.dispatcher), 1)
        pat = self.dispatcher[0]
        self.assertTrue(isinstance(pat, Pattern))
        self.assertEqual(pat.addrpattern.pattern, r'/(?P<value>\w+)$')
        self.assertEqual(type(pat.addrpattern), type(re.compile('foo')))
        self.assertEqual(pat.typecodes, 'ii')
        self.assertEqual(pat.convdict, {'value': 's'})
        self.assertEqual(pat.handler, 'handler1')
        self.assertEqual(pat.params, {})

        self.dispatcher.add_pattern(
            (r'/bar$', 'f', 'handler2', {'spamm': 'eggs'}))
        self.assertEqual(len(self.dispatcher), 2)
        self.assertEqual(self.dispatcher[1].params.get('spamm'), 'eggs')

    def test_add_patterns(self):
        """List of patterns is added correctly to dispatcher."""
        patterns = [
            (r'/foo$', 'i', 'handler1'),
            (r'/bar$', 'f', 'handler2')
        ]
        self.dispatcher.add_patterns(patterns)
        self.assertEqual(len(self.dispatcher), 2)

    def test_int_param_1(self):
        """Dispatcher correctly converts int type URL params (prefix: 'i')."""
        self.dispatcher.add_pattern(
            (r'/(?P<i:page>\d+)/fader(?P<i:cc>\d+)$', 'f', 'handler2'))
        self.dispatcher.dispatch('/1/fader1', (0.1,), 'f')
        self.assertEqual(len(self.dispatchlog), 1)
        self.assertEqual(self.dispatchlog[-1], (0.1, 1, 1))

    def test_int_param_2(self):
        """Dispatcher correctly converts int type URL params (two-digits)."""
        self.dispatcher.add_pattern(
            (r'/(?P<i:page>\d+)/push(?P<i:cc>\d+)$', 'f', 'handler2'))
        self.dispatcher('/5/push11', (1.0,), 'f')
        self.assertEqual(len(self.dispatchlog), 1)
        self.assertEqual(self.dispatchlog[-1], (1.0, 11, 5))

    def test_int_param_3(self):
        """Dispatcher correctly converts int type URL params (prefix: 'int')."""
        self.dispatcher.add_pattern(
            (r'/(?P<int:page>\d+)/rotary(?P<i:cc>\d+)$', 'f', 'handler2'))
        self.dispatcher('/42/rotary0', (0.5,), 'f')
        self.assertEqual(len(self.dispatchlog), 1)
        self.assertEqual(self.dispatchlog[-1], (0.5, 0, 42))

    def test_str_param_1(self):
        """Dispatcher correctly converts str type URL params (prefix: 's')."""
        self.dispatcher.add_pattern(
            (r'/(?P<s:value>\w+)$', '', 'handler1'))
        self.dispatcher('/page1', (), '')
        self.assertEqual(len(self.dispatchlog), 1)
        self.assertEqual(self.dispatchlog[-1], ('page1',))

    def test_str_param_2(self):
        """Dispatcher correctly converts str type URL params (prefix: 'str')."""
        self.dispatcher.add_pattern(
            (r'/(?P<str:value>\w+)$', '', 'handler1'))
        self.dispatcher('/page2', (), '')
        self.assertEqual(len(self.dispatchlog), 1)
        self.assertEqual(self.dispatchlog[-1], ('page2',))

    def test_float_param_1(self):
        """Dispatcher correctly converts float type URL params (prefix: 'f')."""
        self.dispatcher.add_pattern(
            (r'/(?P<f:value>\d+(\.\d+)*)$', '', 'handler1'))
        self.dispatcher('/1.0', (), '')
        self.assertEqual(len(self.dispatchlog), 1)
        self.assertEqual(self.dispatchlog[-1], (1.0,))

    def test_float_param_2(self):
        """Dispatcher correctly converts float type URL params (prefix: 'float')."""
        self.dispatcher.add_pattern(
            (r'/(?P<float:value>\d+(\.\d+)*)$', '', 'handler1'))
        self.dispatcher('/0.005', (), '')
        self.assertEqual(len(self.dispatchlog), 1)
        self.assertEqual(self.dispatchlog[-1], (0.005,))

    def test_bool_param_1(self):
        """Dispatcher correctly converts bool type URL params (prefix: 'b')."""
        self.dispatcher.add_pattern(
            (r'/foo/(?P<b:value>\w+)/?$', '', 'handler1'))
        self._check_bool_param()

    def test_bool_param_2(self):
        """Dispatcher correctly converts bool type URL params (prefix: 'bool')."""
        self.dispatcher.add_pattern(
            (r'/foo/(?P<bool:value>\w+)/?$', '', 'handler1'))
        self._check_bool_param()

    def _check_bool_param(self):
        self.dispatcher('/foo/on', (), '')
        self.assertEqual(len(self.dispatchlog), 1)
        self.assertEqual(self.dispatchlog[-1], (True,))
        self.dispatcher('/foo/1', (), '')
        self.assertEqual(len(self.dispatchlog), 2)
        self.assertEqual(self.dispatchlog[-1], (True,))
        self.dispatcher('/foo/y', (), '')
        self.assertEqual(len(self.dispatchlog), 3)
        self.assertEqual(self.dispatchlog[-1], (True,))
        self.dispatcher('/foo/yes', (), '')
        self.assertEqual(len(self.dispatchlog), 4)
        self.assertEqual(self.dispatchlog[-1], (True,))
        self.dispatcher('/foo/t/', (), '')
        self.assertEqual(len(self.dispatchlog), 5)
        self.assertEqual(self.dispatchlog[-1], (True,))
        self.dispatcher('/foo/true', (), '')
        self.assertEqual(len(self.dispatchlog), 6)
        self.assertEqual(self.dispatchlog[-1], (True,))
        self.dispatcher('/foo/enable', (), '')
        self.assertEqual(len(self.dispatchlog), 7)
        self.assertEqual(self.dispatchlog[-1], (True,))
        self.dispatcher('/foo/yoah', (), '')
        self.assertEqual(len(self.dispatchlog), 8)
        self.assertEqual(self.dispatchlog[-1], (False,))

    def test_cache_store(self):
        """Matched patterns are store in cache."""
        self.dispatcher = OSCDispatcher([], self, 512)
        ci = self.dispatcher._get_pattern.cache_info
        self.assertEqual(ci().maxsize, 512)
        self.assertEqual(ci().currsize, 0)

        patterns = [
            (r'/foo$', 'i', 'handler1'),
            (r'/bar$', 'f', 'handler2')
        ]
        self.dispatcher.add_patterns(patterns)

        self.dispatcher('/foo', (), 'i')
        self.assertEqual(ci().currsize, 1)
        self.dispatcher('/bar', (2,), 'f')
        self.assertEqual(ci().currsize, 2)
        self.dispatcher('/foo', (), 'i')
        self.assertEqual(ci().currsize, 2)
        self.dispatcher('/foo', (), 'f')
        self.assertEqual(ci().currsize, 2)
        self.dispatcher('/baz', (), '')
        self.assertEqual(ci().currsize, 2)

    def test_cache_usage(self):
        """Pattern cache is initialized and used correctly."""
        self.dispatcher = OSCDispatcher([], self, 512)
        ci = self.dispatcher._get_pattern.cache_info
        self.assertEqual(ci().maxsize, 512)
        self.assertEqual(ci().currsize, 0)

        patterns = [
            (r'/foo$', 'i', 'handler1'),
            (r'/bar$', 'f', 'handler2')
        ]
        self.dispatcher.add_patterns(patterns)

        self.dispatcher('/foo', (), 'i')
        self.assertEqual(ci().hits, 0)
        self.dispatcher('/bar', (2,), 'f')
        self.assertEqual(ci().hits, 0)
        self.dispatcher('/foo', (), 'i')
        self.assertEqual(ci().hits, 1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()
