"""Tests for audio device detection and configuration commands."""

from unittest.mock import patch

from click.testing import CliRunner

from rejoice.audio import get_audio_input_devices, record_audio
from rejoice.cli.commands import main


def test_get_audio_input_devices_filters_input_only():
    """GIVEN sounddevice reports multiple devices
    WHEN get_audio_input_devices is called
    THEN only input-capable devices are returned"""

    fake_devices = [
        {"name": "Built-in Output", "max_input_channels": 0, "max_output_channels": 2},
        {"name": "USB Mic", "max_input_channels": 1, "max_output_channels": 0},
    ]

    with patch("rejoice.audio.sd.query_devices", return_value=fake_devices):
        devices = get_audio_input_devices()

    assert len(devices) == 1
    assert devices[0]["name"] == "USB Mic"
    assert devices[0]["index"] == 1  # index should match position from sounddevice


def test_config_list_mics_shows_devices():
    """GIVEN rec config list-mics
    WHEN invoked with available devices
    THEN device list is shown in the output"""

    fake_devices = [
        {"name": "Built-in Output", "max_input_channels": 0, "max_output_channels": 2},
        {"name": "USB Mic", "max_input_channels": 1, "max_output_channels": 0},
    ]

    with patch("rejoice.audio.sd.query_devices", return_value=fake_devices):
        runner = CliRunner()
        result = runner.invoke(main, ["config", "list-mics"])

    assert result.exit_code == 0
    assert "USB Mic" in result.output
    assert "Index" in result.output or "index" in result.output.lower()


def test_config_list_mics_handles_no_devices_gracefully():
    """GIVEN rec config list-mics
    WHEN no audio devices are available
    THEN a clear warning is shown and command succeeds"""

    with patch("rejoice.audio.sd.query_devices", return_value=[]):
        runner = CliRunner()
        result = runner.invoke(main, ["config", "list-mics"])

    assert result.exit_code == 0
    assert (
        "No audio input devices" in result.output or "no audio" in result.output.lower()
    )


def test_record_audio_uses_correct_parameters(monkeypatch):
    """GIVEN a callback and device
    WHEN record_audio is called
    THEN sounddevice.InputStream is created with 16kHz mono and started."""

    created_streams = []

    class DummyStream:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.started = False
            created_streams.append(self)

        def start(self):
            self.started = True

    def fake_input_stream(**kwargs):
        return DummyStream(**kwargs)

    def callback(indata, frames, time, status):  # pragma: no cover - callback not run
        pass

    monkeypatch.setattr("rejoice.audio.sd.InputStream", fake_input_stream)

    stream = record_audio(callback=callback, device="USB Mic")

    assert created_streams, "InputStream should have been created"
    created = created_streams[0]

    assert created.kwargs["samplerate"] == 16000
    assert created.kwargs["channels"] == 1
    assert created.kwargs["callback"] is callback
    assert created.kwargs["device"] == "USB Mic"
    assert created.started is True
    assert stream is created


def test_record_audio_raises_if_sounddevice_unavailable(monkeypatch):
    """GIVEN sounddevice dependency is unavailable
    WHEN record_audio is called
    THEN a helpful RuntimeError is raised."""

    monkeypatch.setattr("rejoice.audio.sd", None)

    def dummy_callback(indata, frames, time, status):  # pragma: no cover
        pass

    try:
        record_audio(dummy_callback)
    except RuntimeError as exc:
        message = str(exc).lower()
        assert "sounddevice" in message
        assert "not available" in message or "missing" in message
    else:  # pragma: no cover - defensive
        raise AssertionError("record_audio() should raise RuntimeError when sd is None")


def test_record_audio_wraps_sounddevice_errors(monkeypatch):
    """GIVEN sounddevice raises an error when creating the stream
    WHEN record_audio is called
    THEN a RuntimeError with a clear message is raised."""

    class BoomError(Exception):
        pass

    def boom_input_stream(**kwargs):
        raise BoomError("device busy")

    def dummy_callback(indata, frames, time, status):  # pragma: no cover
        pass

    monkeypatch.setattr("rejoice.audio.sd.InputStream", boom_input_stream)

    try:
        record_audio(dummy_callback, device="Busy Device")
    except RuntimeError as exc:
        message = str(exc)
        assert "failed to start audio input stream" in message.lower()
        assert "device busy" in message.lower()
    else:  # pragma: no cover - defensive
        raise AssertionError(
            "record_audio() should wrap sounddevice errors in RuntimeError"
        )


def test_get_audio_input_devices_handles_default_device_tuple(monkeypatch):
    """GIVEN get_audio_input_devices
    WHEN default.device is a tuple/list
    THEN default_index is extracted correctly (line 50)"""
    fake_devices = [
        {"name": "Mic 1", "max_input_channels": 1, "index": 0},
        {"name": "Mic 2", "max_input_channels": 1, "index": 1},
    ]

    # Mock sd.default.device as tuple (input, output)
    mock_default = type("obj", (object,), {"device": (0, 1)})()
    mock_sd = type(
        "obj",
        (object,),
        {
            "query_devices": lambda *args, **kwargs: fake_devices,
            "default": mock_default,
        },
    )()

    with patch("rejoice.audio.sd", mock_sd):
        devices = get_audio_input_devices()

    # First device should be marked as default
    assert any(d["is_default"] for d in devices)
