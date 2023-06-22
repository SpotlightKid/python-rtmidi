"""Tests for wheels built by CI."""

import sys

import pytest

import rtmidi


@pytest.mark.linux
@pytest.mark.skipif(not sys.platform.lower().startswith("linux"))
def test_linux_supports_alsa():
    assert rtmidi.API_LINUX_ALSA in rtmidi.get_compiled_api()


@pytest.mark.linux
@pytest.mark.skipif(not sys.platform.lower().startswith("linux"))
def test_linux_supports_jack():
    assert rtmidi.API_UNIX_JACK in rtmidi.get_compiled_api()


@pytest.mark.macos
@pytest.mark.skipif(not sys.platform.lower().startswith("darwin"))
def test_macos_supports_coremidi():
    assert rtmidi.API_MACOSX_CORE in rtmidi.get_compiled_api()


@pytest.mark.windows
@pytest.mark.skipif(not sys.platform.lower().startswith("win"))
def test_windows_supports_winmm():
    assert rtmidi.API_WINDOWS_MM in rtmidi.get_compiled_api()
