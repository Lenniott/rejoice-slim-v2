"""Tests for CLI commands."""
from pathlib import Path
from typing import List, Tuple

from click.testing import CliRunner

from rejoice.cli.commands import main, start_recording_session


def test_cli_help():
    """GIVEN rec command
    WHEN --help is called
    THEN help text is displayed"""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Rejoice" in result.output
    assert "rec" in result.output.lower() or "recording" in result.output.lower()


def test_cli_version():
    """GIVEN --version flag
    WHEN main is invoked
    THEN version is displayed"""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "2.0.0" in result.output


def test_cli_debug_flag():
    """GIVEN --debug flag
    WHEN main is invoked
    THEN debug mode is enabled"""
    runner = CliRunner()
    result = runner.invoke(main, ["--debug"])
    assert result.exit_code == 0
    assert "Debug mode enabled" in result.output or "debug" in result.output.lower()


def test_main_starts_recording_when_no_subcommand(monkeypatch):
    """GIVEN rec is invoked without subcommand
    WHEN main is executed
    THEN a recording session is started via helper."""
    runner = CliRunner()

    calls = {"started": False}

    def fake_start_recording_session() -> Tuple[Path, str]:
        calls["started"] = True
        # Return dummy path/id to satisfy any callers
        return Path("/tmp/transcript_20250101_000001.md"), "000001"

    monkeypatch.setattr(
        "rejoice.cli.commands.start_recording_session",
        fake_start_recording_session,
    )

    result = runner.invoke(main, [])

    assert result.exit_code == 0
    assert calls["started"] is True


def test_start_recording_creates_transcript_before_audio(monkeypatch, tmp_path):
    """GIVEN a recording session
    WHEN start_recording_session is called
    THEN transcript file is created before audio capture starts."""

    events: List[str] = []

    # Fake transcript creation that records order and returns a path/id
    def fake_create_transcript(save_dir: Path):
        events.append("create_transcript")
        transcript_path = tmp_path / "transcript_20250101_000001.md"
        # Simulate that file would be created by manager without touching disk here
        return transcript_path, "000001"

    class FakeStream:
        def __init__(self) -> None:
            self.stopped = False
            self.closed = False

        def stop(self) -> None:
            self.stopped = True

        def close(self) -> None:
            self.closed = True

    fake_stream = FakeStream()

    def fake_record_audio(callback, *, device=None, samplerate=16000, channels=1):
        events.append("record_audio")
        # Ensure callback is callable, but don't invoke it here
        assert callable(callback)
        # Return fake stream so cleanup can be exercised
        return fake_stream

    # Avoid blocking on user input by using a no-op wait function
    def fake_wait_for_stop() -> None:
        events.append("wait_for_stop")

    monkeypatch.setattr(
        "rejoice.cli.commands.create_transcript",
        fake_create_transcript,
    )
    monkeypatch.setattr(
        "rejoice.cli.commands.record_audio",
        fake_record_audio,
    )

    # Call the helper under test
    filepath, transcript_id = start_recording_session(wait_for_stop=fake_wait_for_stop)

    # Order: create_transcript -> record_audio -> wait_for_stop
    assert events[0:3] == ["create_transcript", "record_audio", "wait_for_stop"]

    # The helper should return values from create_transcript
    assert filepath.name == "transcript_20250101_000001.md"
    assert transcript_id == "000001"

    # The fake stream should be stopped and closed
    assert fake_stream.stopped is True
    assert fake_stream.closed is True
