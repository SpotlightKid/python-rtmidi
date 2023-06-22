"""Tests for wheels built by CI."""

import sys

import pytest

import rtmidi


@pytest.mark.ci
@pytest.mark.skipif(not sys.platform.lower().startswith("linux"), reason="requires Linux OS")
def test_linux_supports_alsa():
    assert rtmidi.API_LINUX_ALSA in rtmidi.get_compiled_api()


@pytest.mark.ci
@pytest.mark.skipif(not sys.platform.lower().startswith("linux"), reason="requires Linux OS")
def test_linux_supports_jack():
    assert rtmidi.API_UNIX_JACK in rtmidi.get_compiled_api()


@pytest.mark.ci
@pytest.mark.skipif(not sys.platform.lower().startswith("darwin"), reason="requires macOS")
def test_macos_supports_coremidi():
    assert rtmidi.API_MACOSX_CORE in rtmidi.get_compiled_api()


@pytest.mark.ci
@pytest.mark.skipif(not sys.platform.lower().startswith("win"), reason="requires Windows OS")
def test_windows_supports_winmm():
    assert rtmidi.API_WINDOWS_MM in rtmidi.get_compiled_api()
