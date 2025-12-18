"""Tests for CLI commands."""
from pathlib import Path
from typing import List, Tuple

import click
from click.testing import CliRunner

from rejoice.cli.commands import (
    _default_wait_for_stop,
    main,
    start_recording_session,
    view_transcript,
)


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

    events: List[object] = []

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
    # Avoid touching the filesystem for status updates in this ordering test.
    monkeypatch.setattr(
        "rejoice.cli.commands.update_status",
        lambda path, status: events.append(("update_status", path, status)),
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


def test_default_wait_for_stop_uses_enter_and_getchar(monkeypatch, capsys):
    """GIVEN the default wait_for_stop implementation
    WHEN it is invoked
    THEN it prompts for Enter and calls click.getchar().
    """
    calls = {"getchar_called": False}

    def fake_getchar() -> str:
        calls["getchar_called"] = True
        # Simulate user pressing Enter
        return "\n"

    monkeypatch.setattr(click, "getchar", fake_getchar)

    _default_wait_for_stop()

    captured = capsys.readouterr()
    assert "Press Enter to stop recording." in captured.out
    assert calls["getchar_called"] is True


def test_start_recording_marks_transcript_completed(monkeypatch, tmp_path):
    """GIVEN a recording session
    WHEN start_recording_session finishes normally
    THEN the transcript status is updated to 'completed' via the manager helper.
    """
    events: List[object] = []

    # Use a real file path so status update helpers have something to operate on
    transcript_path = tmp_path / "transcript_20250101_000010.md"
    transcript_path.write_text("initial content", encoding="utf-8")

    def fake_create_transcript(save_dir: Path):
        events.append("create_transcript")
        return transcript_path, "000010"

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
        assert callable(callback)
        return fake_stream

    def fake_wait_for_stop() -> None:
        events.append("wait_for_stop")

    def fake_update_status(path: Path, status: str) -> None:
        events.append(("update_status", path, status))

    monkeypatch.setattr(
        "rejoice.cli.commands.create_transcript",
        fake_create_transcript,
    )
    monkeypatch.setattr(
        "rejoice.cli.commands.record_audio",
        fake_record_audio,
    )
    monkeypatch.setattr(
        "rejoice.cli.commands.update_status",
        fake_update_status,
    )

    filepath, transcript_id = start_recording_session(wait_for_stop=fake_wait_for_stop)

    # Core flow order still respected
    assert events[0:3] == ["create_transcript", "record_audio", "wait_for_stop"]

    # Transcript identity is passed through
    assert filepath == transcript_path
    assert transcript_id == "000010"

    # And status is updated to completed at the end of the session
    assert ("update_status", transcript_path, "completed") in events


def test_start_recording_handles_ctrl_c_and_marks_cancelled(monkeypatch, tmp_path):
    """GIVEN a recording session
    WHEN the user presses Ctrl+C during wait_for_stop
    THEN the session is cancelled and transcript status is updated to 'cancelled'.
    """
    events: List[object] = []

    transcript_path = tmp_path / "transcript_20250101_000020.md"
    transcript_path.write_text("initial content", encoding="utf-8")

    def fake_create_transcript(save_dir: Path):
        events.append("create_transcript")
        return transcript_path, "000020"

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
        assert callable(callback)
        return fake_stream

    def fake_wait_for_stop() -> None:
        events.append("wait_for_stop")
        # Simulate Ctrl+C from user
        raise KeyboardInterrupt()

    # Patch confirmation prompt to simulate user choosing to keep the transcript
    def fake_confirm_keep(*args, **kwargs):
        # First prompt: cancel recording? -> yes
        # Second prompt: delete file? -> no (keep, but mark cancelled)
        events.append(("confirm", args, kwargs))
        # For simplicity in this unit test we always return True on first call
        # and False on second via a simple state flag.
        state = fake_confirm_keep.__dict__.setdefault("state", {"count": 0})
        state["count"] += 1
        return state["count"] == 1

    def fake_update_status(path: Path, status: str) -> None:
        events.append(("update_status", path, status))

    monkeypatch.setattr(
        "rejoice.cli.commands.create_transcript",
        fake_create_transcript,
    )
    monkeypatch.setattr(
        "rejoice.cli.commands.record_audio",
        fake_record_audio,
    )
    monkeypatch.setattr(
        "rejoice.cli.commands.update_status",
        fake_update_status,
    )
    monkeypatch.setattr(
        "rejoice.cli.commands.Confirm.ask",
        fake_confirm_keep,
    )

    filepath, transcript_id = start_recording_session(wait_for_stop=fake_wait_for_stop)

    # Core flow order still respected up to the interrupt
    assert events[0:3] == ["create_transcript", "record_audio", "wait_for_stop"]

    assert filepath == transcript_path
    assert transcript_id == "000020"

    # Status is updated to cancelled, not completed
    assert ("update_status", transcript_path, "cancelled") in events


def test_list_recordings_shows_message_when_no_transcripts(monkeypatch, tmp_path):
    """GIVEN no transcript files in the save directory
    WHEN `rec list` is invoked
    THEN a friendly 'no recordings' message is shown and the command exits successfully.
    """

    class FakeOutputConfig:
        def __init__(self, save_path: str) -> None:
            self.save_path = save_path

    class FakeConfig:
        def __init__(self, save_path: str) -> None:
            self.output = FakeOutputConfig(save_path)

    # Point the CLI at an empty temporary directory for transcripts
    save_dir = tmp_path / "transcripts"
    save_dir.mkdir()

    monkeypatch.setattr(
        "rejoice.cli.commands.load_config",
        lambda: FakeConfig(str(save_dir)),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["list"])

    assert result.exit_code == 0
    assert "No recordings found" in result.output


def test_list_recordings_shows_transcripts_sorted_newest_first(monkeypatch, tmp_path):
    """GIVEN multiple transcript files in the save directory
    WHEN `rec list` is invoked
    THEN transcripts are listed newest-first with ID, date and filename columns.
    """

    class FakeOutputConfig:
        def __init__(self, save_path: str) -> None:
            self.save_path = save_path

    class FakeConfig:
        def __init__(self, save_path: str) -> None:
            self.output = FakeOutputConfig(save_path)

    save_dir = tmp_path / "transcripts"
    save_dir.mkdir()

    # Create a few transcript files that match the manager naming pattern
    first = save_dir / "transcript_20250101_000001.md"
    second = save_dir / "transcript_20250102_000002.md"
    third = save_dir / "transcript_20250103_000003.md"

    for path in (first, second, third):
        path.write_text("dummy content", encoding="utf-8")

    # Point config at our temporary transcripts directory
    monkeypatch.setattr(
        "rejoice.cli.commands.load_config",
        lambda: FakeConfig(str(save_dir)),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["list"])

    assert result.exit_code == 0

    # Expect table-like output; newest (2025-01-03) should appear first.
    output_lines = [
        line for line in result.output.splitlines() if "transcript_2025" in line
    ]

    assert len(output_lines) == 3

    # Check ordering: IDs and dates should be in descending date order
    assert "000003" in output_lines[0]
    assert "2025-01-03" in output_lines[0]
    assert "000002" in output_lines[1]
    assert "2025-01-02" in output_lines[1]
    assert "000001" in output_lines[2]
    assert "2025-01-01" in output_lines[2]


def test_view_transcript_by_id_hides_frontmatter_by_default(monkeypatch, tmp_path):
    """GIVEN an existing transcript
    WHEN `rec view <id>` is invoked
    THEN the body is shown and YAML frontmatter is hidden by default.
    """

    class FakeOutputConfig:
        def __init__(self, save_path: str) -> None:
            self.save_path = save_path

    class FakeConfig:
        def __init__(self, save_path: str) -> None:
            self.output = FakeOutputConfig(save_path)

    save_dir = tmp_path / "transcripts"
    save_dir.mkdir()

    transcript_path = save_dir / "transcript_20250101_000001.md"
    transcript_path.write_text(
        (
            "---\n"
            "id: '000001'\n"
            "type: voice-note\n"
            "status: completed\n"
            "created: 2025-01-01 10:00\n"
            "language: en\n"
            "tags: []\n"
            'summary: ""\n'
            "---\n\n"
            "# My Note\n\n"
            "This is the body of the transcript.\n"
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "rejoice.cli.commands.load_config",
        lambda: FakeConfig(str(save_dir)),
    )

    runner = CliRunner()
    # Use a short numeric ID to exercise ID normalisation.
    result = runner.invoke(view_transcript, ["1"])

    assert result.exit_code == 0
    # Body content should be rendered
    assert "My Note" in result.output
    assert "This is the body of the transcript." in result.output
    # Frontmatter keys should not be shown by default
    assert "id: '000001'" not in result.output
    assert "status: completed" not in result.output


def test_view_transcript_with_show_frontmatter_displays_metadata(
    monkeypatch,
    tmp_path,
):
    """GIVEN an existing transcript
    WHEN `rec view --show-frontmatter <id>` is invoked
    THEN both YAML frontmatter and body are displayed.
    """

    class FakeOutputConfig:
        def __init__(self, save_path: str) -> None:
            self.save_path = save_path

    class FakeConfig:
        def __init__(self, save_path: str) -> None:
            self.output = FakeOutputConfig(save_path)

    save_dir = tmp_path / "transcripts"
    save_dir.mkdir()

    transcript_path = save_dir / "transcript_20250102_000010.md"
    transcript_path.write_text(
        (
            "---\n"
            "id: '000010'\n"
            "type: voice-note\n"
            "status: completed\n"
            "created: 2025-01-02 12:00\n"
            "language: en\n"
            "tags: []\n"
            'summary: ""\n'
            "---\n\n"
            "## Heading\n\n"
            "Body content here.\n"
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "rejoice.cli.commands.load_config",
        lambda: FakeConfig(str(save_dir)),
    )

    runner = CliRunner()
    result = runner.invoke(view_transcript, ["--show-frontmatter", "10"])

    assert result.exit_code == 0
    # Frontmatter metadata should be visible
    assert "id: '000010'" in result.output
    assert "status: completed" in result.output
    # Body content should also be shown
    assert "Heading" in result.output
    assert "Body content here." in result.output


def test_view_latest_shows_most_recent_transcript(monkeypatch, tmp_path):
    """GIVEN multiple transcripts
    WHEN `rec view latest` is invoked
    THEN the most recent transcript (by filename pattern) is displayed.
    """

    class FakeOutputConfig:
        def __init__(self, save_path: str) -> None:
            self.save_path = save_path

    class FakeConfig:
        def __init__(self, save_path: str) -> None:
            self.output = FakeOutputConfig(save_path)

    save_dir = tmp_path / "transcripts"
    save_dir.mkdir()

    older = save_dir / "transcript_20250101_000001.md"
    newer = save_dir / "transcript_20250102_000002.md"

    older.write_text(
        (
            "---\n"
            "id: '000001'\n"
            "type: voice-note\n"
            "status: completed\n"
            "created: 2025-01-01 09:00\n"
            "language: en\n"
            "tags: []\n"
            'summary: ""\n'
            "---\n\n"
            "Older transcript body.\n"
        ),
        encoding="utf-8",
    )
    newer.write_text(
        (
            "---\n"
            "id: '000002'\n"
            "type: voice-note\n"
            "status: completed\n"
            "created: 2025-01-02 10:00\n"
            "language: en\n"
            "tags: []\n"
            'summary: ""\n'
            "---\n\n"
            "NEWEST transcript body.\n"
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "rejoice.cli.commands.load_config",
        lambda: FakeConfig(str(save_dir)),
    )

    runner = CliRunner()
    result = runner.invoke(view_transcript, ["latest"])

    assert result.exit_code == 0
    assert "NEWEST transcript body." in result.output
    assert "Older transcript body." not in result.output


def test_view_invalid_id_shows_clear_error(monkeypatch, tmp_path):
    """GIVEN an invalid transcript ID
    WHEN `rec view` is invoked
    THEN a clear error message is shown and the command fails.
    """

    class FakeOutputConfig:
        def __init__(self, save_path: str) -> None:
            self.save_path = save_path

    class FakeConfig:
        def __init__(self, save_path: str) -> None:
            self.output = FakeOutputConfig(save_path)

    save_dir = tmp_path / "transcripts"
    save_dir.mkdir()

    monkeypatch.setattr(
        "rejoice.cli.commands.load_config",
        lambda: FakeConfig(str(save_dir)),
    )

    runner = CliRunner()
    result = runner.invoke(view_transcript, ["abc"])

    assert result.exit_code != 0
    assert "is not a valid transcript ID" in result.output


def test_view_missing_transcript_shows_friendly_message(monkeypatch, tmp_path):
    """GIVEN a well-formed ID that does not correspond to any file
    WHEN `rec view` is invoked
    THEN a friendly 'not found' message is shown and the command fails.
    """

    class FakeOutputConfig:
        def __init__(self, save_path: str) -> None:
            self.save_path = save_path

    class FakeConfig:
        def __init__(self, save_path: str) -> None:
            self.output = FakeOutputConfig(save_path)

    save_dir = tmp_path / "transcripts"
    save_dir.mkdir()

    monkeypatch.setattr(
        "rejoice.cli.commands.load_config",
        lambda: FakeConfig(str(save_dir)),
    )

    runner = CliRunner()
    result = runner.invoke(view_transcript, ["42"])

    assert result.exit_code != 0
    assert "Transcript with ID 000042 was not found" in result.output
