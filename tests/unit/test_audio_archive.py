"""Tests for audio archiving utilities ([R-013])."""

from pathlib import Path
import tempfile

from rejoice.audio.archive import (
    archive_audio_file,
    ensure_audio_directory_exists,
    get_archived_audio_path,
)


def test_ensure_audio_directory_exists_creates_directory():
    """GIVEN a transcript directory without audio/ subdirectory
    WHEN ensure_audio_directory_exists is called
    THEN the audio/ directory is created
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        transcript_dir = Path(tmpdir) / "transcripts"
        transcript_dir.mkdir(parents=True, exist_ok=True)

        audio_dir = ensure_audio_directory_exists(transcript_dir)

        assert audio_dir.exists()
        assert audio_dir.is_dir()
        assert audio_dir.name == "audio"
        assert audio_dir.parent == transcript_dir


def test_ensure_audio_directory_exists_handles_existing_directory():
    """GIVEN a transcript directory with existing audio/ subdirectory
    WHEN ensure_audio_directory_exists is called
    THEN the existing directory is used without error
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        transcript_dir = Path(tmpdir) / "transcripts"
        transcript_dir.mkdir(parents=True, exist_ok=True)
        existing_audio_dir = transcript_dir / "audio"
        existing_audio_dir.mkdir(parents=True, exist_ok=True)

        audio_dir = ensure_audio_directory_exists(transcript_dir)

        assert audio_dir.exists()
        assert audio_dir == existing_audio_dir


def test_get_archived_audio_path_generates_correct_path():
    """GIVEN a transcript file path
    WHEN get_archived_audio_path is called
    THEN the correct audio archive path is returned
    """
    transcript_path = Path("/tmp/transcripts/000054_transcript_20251220.md")

    archived_path = get_archived_audio_path(transcript_path)

    assert archived_path.parent.name == "audio"
    assert archived_path.parent.parent == transcript_path.parent
    assert archived_path.name == "000054_transcript_20251220.wav"


def test_archive_audio_file_moves_to_correct_location(tmp_path: Path):
    """GIVEN a temporary audio file and transcript path
    WHEN archive_audio_file is called
    THEN the audio file is moved to the correct archive location
    AND the filename matches the transcript (with .wav extension)
    """
    # Create transcript file structure
    transcript_dir = tmp_path / "transcripts"
    transcript_dir.mkdir()
    transcript_path = transcript_dir / "000054_transcript_20251220.md"
    transcript_path.write_text("test transcript")

    # Create temporary audio file
    temp_audio = tmp_path / "temp_audio.wav"
    temp_audio.write_bytes(b"fake audio data")

    archived_path = archive_audio_file(temp_audio, transcript_path)

    # Verify temp file is gone
    assert not temp_audio.exists()

    # Verify archived file exists at correct location
    assert archived_path.exists()
    assert archived_path.name == "000054_transcript_20251220.wav"
    assert archived_path.parent.name == "audio"
    assert archived_path.parent.parent == transcript_dir

    # Verify audio data is preserved
    assert archived_path.read_bytes() == b"fake audio data"


def test_archive_audio_file_creates_audio_directory(tmp_path: Path):
    """GIVEN a transcript directory without audio/ subdirectory
    WHEN archive_audio_file is called
    THEN the audio/ directory is created automatically
    """
    transcript_dir = tmp_path / "transcripts"
    transcript_dir.mkdir()
    transcript_path = transcript_dir / "000054_transcript_20251220.md"
    transcript_path.write_text("test")

    temp_audio = tmp_path / "temp_audio.wav"
    temp_audio.write_bytes(b"audio")

    archived_path = archive_audio_file(temp_audio, transcript_path)

    assert archived_path.parent.exists()
    assert archived_path.parent.is_dir()
    assert archived_path.parent.name == "audio"


def test_archive_audio_file_handles_existing_file(tmp_path: Path):
    """GIVEN an existing audio file at the archive location
    WHEN archive_audio_file is called
    THEN a timestamp suffix is appended to avoid overwriting
    """
    transcript_dir = tmp_path / "transcripts"
    transcript_dir.mkdir()
    audio_dir = transcript_dir / "audio"
    audio_dir.mkdir()

    transcript_path = transcript_dir / "000054_transcript_20251220.md"
    transcript_path.write_text("test")

    # Create existing audio file
    existing_audio = audio_dir / "000054_transcript_20251220.wav"
    existing_audio.write_bytes(b"existing audio")

    # Create new temp audio file
    temp_audio = tmp_path / "temp_audio.wav"
    temp_audio.write_bytes(b"new audio")

    archived_path = archive_audio_file(temp_audio, transcript_path)

    # Verify original file still exists
    assert existing_audio.exists()

    # Verify new file has timestamp suffix
    assert archived_path.exists()
    assert archived_path.name.startswith("000054_transcript_20251220_")
    assert archived_path.name.endswith(".wav")
    # Timestamp format: YYYYMMDD_HHMMSS
    assert len(archived_path.stem.split("_")) >= 5  # ID_transcript_DATE_TIMESTAMP


def test_archive_audio_file_returns_correct_path(tmp_path: Path):
    """GIVEN a temporary audio file
    WHEN archive_audio_file is called
    THEN the function returns the Path to the archived file
    """
    transcript_dir = tmp_path / "transcripts"
    transcript_dir.mkdir()
    transcript_path = transcript_dir / "000054_transcript_20251220.md"
    transcript_path.write_text("test")

    temp_audio = tmp_path / "temp_audio.wav"
    temp_audio.write_bytes(b"audio")

    archived_path = archive_audio_file(temp_audio, transcript_path)

    assert isinstance(archived_path, Path)
    assert archived_path.exists()


def test_archive_audio_file_preserves_audio_data(tmp_path: Path):
    """GIVEN a temporary audio file with specific content
    WHEN archive_audio_file is called
    THEN the audio data is preserved in the archived file
    """
    transcript_dir = tmp_path / "transcripts"
    transcript_dir.mkdir()
    transcript_path = transcript_dir / "000054_transcript_20251220.md"
    transcript_path.write_text("test")

    # Create audio file with specific content
    audio_content = b"This is fake WAV file content" * 100
    temp_audio = tmp_path / "temp_audio.wav"
    temp_audio.write_bytes(audio_content)

    archived_path = archive_audio_file(temp_audio, transcript_path)

    assert archived_path.read_bytes() == audio_content


def test_get_archived_audio_path_uses_relative_structure(tmp_path: Path):
    """GIVEN a transcript path
    WHEN get_archived_audio_path is called
    THEN the returned path maintains correct directory structure
    """
    transcript_path = tmp_path / "transcripts" / "000054_transcript_20251220.md"
    transcript_path.parent.mkdir(parents=True, exist_ok=True)
    transcript_path.write_text("test")

    archived_path = get_archived_audio_path(transcript_path)

    # Verify structure: transcripts/audio/filename.wav
    assert archived_path.parent.parent == transcript_path.parent
    assert archived_path.parent.name == "audio"
    assert archived_path.name == "000054_transcript_20251220.wav"


def test_archive_audio_file_handles_special_characters_in_path(tmp_path: Path):
    """GIVEN a transcript path with special characters
    WHEN archive_audio_file is called
    THEN audio file is archived correctly"""
    # Create directory with space in name
    transcript_dir = tmp_path / "transcripts with spaces"
    transcript_dir.mkdir(parents=True, exist_ok=True)
    transcript_path = transcript_dir / "000054_transcript_20251220.md"
    transcript_path.write_text("test")

    temp_audio = tmp_path / "temp_audio.wav"
    temp_audio.write_bytes(b"audio")

    archived_path = archive_audio_file(temp_audio, transcript_path)

    assert archived_path.exists()
    assert archived_path.name == "000054_transcript_20251220.wav"


def test_archive_audio_file_handles_empty_audio_file(tmp_path: Path):
    """GIVEN an empty audio file
    WHEN archive_audio_file is called
    THEN empty file is still archived"""
    transcript_dir = tmp_path / "transcripts"
    transcript_dir.mkdir()
    transcript_path = transcript_dir / "000054_transcript_20251220.md"
    transcript_path.write_text("test")

    temp_audio = tmp_path / "temp_audio.wav"
    temp_audio.write_bytes(b"")  # Empty file

    archived_path = archive_audio_file(temp_audio, transcript_path)

    assert archived_path.exists()
    assert archived_path.read_bytes() == b""
