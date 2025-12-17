"""Tests for audio device detection and configuration commands."""
from unittest.mock import patch

from click.testing import CliRunner

from rejoice.audio import get_audio_input_devices
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
