"""Tests for transcript file manager ([R-003])."""

from pathlib import Path
import re
import tempfile

from rejoice.transcript import manager


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_create_transcript_creates_file_and_directory():
    """GIVEN an empty directory
    WHEN create_transcript is called
    THEN a transcript file is created with the expected naming pattern
    AND the directory is created if missing
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        save_dir = Path(tmpdir) / "transcripts"

        filepath, tid = manager.create_transcript(save_dir)

        assert filepath.exists()
        assert filepath.parent == save_dir

        # ID should be 6-digit zero-padded
        assert tid == "000001"

        # Filename should match transcript_YYYYMMDD_ID.md
        pattern = r"^transcript_\d{8}_000001\.md$"
        assert re.match(pattern, filepath.name)

        content = read_file(filepath)
        assert content.startswith("---\n")
        assert "id: '000001'" in content
        assert "status: recording" in content


def test_get_next_id_increments_over_existing_files():
    """GIVEN existing transcript files with IDs
    WHEN get_next_id is called
    THEN the next sequential ID is returned
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        save_dir = Path(tmpdir)
        save_dir.mkdir(parents=True, exist_ok=True)

        # Simulate existing transcripts across different dates
        (save_dir / "transcript_20240101_000001.md").write_text("test")
        (save_dir / "transcript_20240102_000002.md").write_text("test")

        next_id = manager.get_next_id(save_dir)

        assert next_id == "000003"


def test_get_next_id_ignores_non_transcript_files():
    """GIVEN a directory with non-transcript files
    WHEN get_next_id is called
    THEN non-matching files are ignored
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        save_dir = Path(tmpdir)
        save_dir.mkdir(parents=True, exist_ok=True)

        # Non-matching files should be ignored
        (save_dir / "notes.md").write_text("test")
        (save_dir / "transcript_invalid.md").write_text("test")

        next_id = manager.get_next_id(save_dir)

        assert next_id == "000001"


def test_create_transcript_avoids_duplicate_ids():
    """GIVEN a conflicting filename for the next ID
    WHEN create_transcript is called
    THEN a new unique ID and filename are chosen
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        save_dir = Path(tmpdir)
        save_dir.mkdir(parents=True, exist_ok=True)

        # Pre-create the file that would correspond to ID 000001
        existing = save_dir / "transcript_20240101_000001.md"
        existing.write_text("existing")

        filepath, tid = manager.create_transcript(save_dir)

        assert filepath.exists()
        assert tid == "000002"
        assert filepath.name.endswith("_000002.md")


def test_frontmatter_contains_expected_fields():
    """GIVEN a newly created transcript
    WHEN the file is inspected
    THEN it contains the expected YAML frontmatter fields
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        save_dir = Path(tmpdir)

        filepath, tid = manager.create_transcript(save_dir)

        content = read_file(filepath)

        # Basic YAML frontmatter structure
        assert content.startswith("---\n")
        assert "\n---\n" in content

        # Required fields
        assert f"id: '{tid}'" in content
        assert "type: voice-note" in content
        assert "status: recording" in content
        assert "language: auto" in content
        assert "tags: []" in content
        assert 'summary: ""' in content


def test_write_file_atomic_writes_full_content(tmp_path: Path):
    """GIVEN a target file path
    WHEN write_file_atomic is used
    THEN the file contains exactly the provided content
    """
    target = tmp_path / "atomic_test.md"
    content = "line1\nline2\n"

    manager.write_file_atomic(target, content)

    assert target.exists()
    assert read_file(target) == content


def test_write_file_atomic_overwrites_existing_file(tmp_path: Path):
    """GIVEN an existing file
    WHEN write_file_atomic is used
    THEN the previous contents are fully replaced
    """
    target = tmp_path / "atomic_test.md"
    target.write_text("old content", encoding="utf-8")

    new_content = "new content\nmore content\n"
    manager.write_file_atomic(target, new_content)

    assert read_file(target) == new_content
