#!/usr/bin/env python
"""Basic tests that don't need midi ports."""

import unittest
import rtmidi

import pytest


@pytest.mark.ci
class BasicTest(unittest.TestCase):
    def test_get_api_display_name(self):
        self.assertEqual(rtmidi.get_api_display_name(rtmidi.API_LINUX_ALSA), 'ALSA')
        self.assertEqual(rtmidi.get_api_display_name(rtmidi.API_MACOSX_CORE), 'CoreMidi')
        self.assertEqual(rtmidi.get_api_display_name(rtmidi.API_RTMIDI_DUMMY), 'Dummy')
        self.assertEqual(rtmidi.get_api_display_name(rtmidi.API_UNIX_JACK), 'Jack')
        self.assertEqual(rtmidi.get_api_display_name(rtmidi.API_UNSPECIFIED), 'Unknown')
        self.assertEqual(rtmidi.get_api_display_name(rtmidi.API_WINDOWS_MM), 'Windows MultiMedia')
        self.assertEqual(rtmidi.get_api_display_name(rtmidi.API_WEB_MIDI), 'Web MIDI API')

    def test_get_api_name(self):
        self.assertEqual(rtmidi.get_api_name(rtmidi.API_LINUX_ALSA), 'alsa')
        self.assertEqual(rtmidi.get_api_name(rtmidi.API_MACOSX_CORE), 'core')
        self.assertEqual(rtmidi.get_api_name(rtmidi.API_RTMIDI_DUMMY), 'dummy')
        self.assertEqual(rtmidi.get_api_name(rtmidi.API_UNIX_JACK), 'jack')
        self.assertEqual(rtmidi.get_api_name(rtmidi.API_UNSPECIFIED), 'unspecified')
        self.assertEqual(rtmidi.get_api_name(rtmidi.API_WINDOWS_MM), 'winmm')
        self.assertEqual(rtmidi.get_api_name(rtmidi.API_WEB_MIDI), 'web')

    def test_get_compiled_api(self):
        apilist = rtmidi.get_compiled_api()
        self.assertTrue(isinstance(apilist, list))
        self.assertTrue(len(apilist) >= 1)
        for api in apilist:
            self.assertTrue(api <= rtmidi.API_RTMIDI_DUMMY)

    def test_get_compiled_api_by_name(self):
        for api, name in (
                (rtmidi.API_LINUX_ALSA, 'alsa'),
                (rtmidi.API_MACOSX_CORE, 'core'),
                (rtmidi.API_RTMIDI_DUMMY, 'dummy'),
                (rtmidi.API_UNIX_JACK, 'jack'),
                (rtmidi.API_WINDOWS_MM, 'winmm'),
                (rtmidi.API_WEB_MIDI, 'web'),):

            res = rtmidi.get_compiled_api_by_name(name)

            if api in rtmidi.get_compiled_api():
                self.assertEqual(res, api)
            else:
                self.assertEqual(res, rtmidi.API_UNSPECIFIED)

    def test_get_rtmidi_version(self):
        version = rtmidi.get_rtmidi_version()
        self.assertTrue(isinstance(version, str))
        self.assertEqual(version, '5.0.0')

    def test_nondummy_api_present(self):
        # Make sure at least one actual API has been compiled
        apilist = rtmidi.get_compiled_api()
        apiFound = False
        for api in apilist:
            if api != rtmidi.API_RTMIDI_DUMMY:
                apiFound = True
        self.assertTrue(apiFound)


if __name__ == '__main__':
    unittest.main()
