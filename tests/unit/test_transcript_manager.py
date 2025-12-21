"""Tests for transcript file manager ([R-003])."""

from pathlib import Path
import re
import tempfile
from unittest.mock import patch

import pytest

from rejoice.transcript import manager
from rejoice.transcript.manager import ID_WIDTH, TranscriptMetadata


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

        # Filename should match new format: ID_transcript_YYYYMMDD.md
        pattern = r"^000001_transcript_\d{8}\.md$"
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
        # New format: ID_transcript_YYYYMMDD.md
        assert filepath.name.startswith("000002_transcript_")


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


def test_append_to_transcript_preserves_frontmatter_and_appends_body():
    """GIVEN an existing transcript with frontmatter
    WHEN append_to_transcript is called
    THEN the frontmatter is preserved and new text is appended after the body
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        save_dir = Path(tmpdir)
        filepath, _tid = manager.create_transcript(save_dir)

        initial_content = read_file(filepath)
        assert initial_content.endswith("\n\n")

        manager.append_to_transcript(filepath, "First line.")
        manager.append_to_transcript(filepath, "Second line.")

        updated = read_file(filepath)

        # Frontmatter should be unchanged at the top
        assert updated.startswith(initial_content)

        # Body content should contain both appended lines in order
        body = updated[len(initial_content) :]
        assert "First line." in body
        assert "Second line." in body


def test_append_to_transcript_handles_empty_body_gracefully():
    """GIVEN a transcript that only has frontmatter
    WHEN append_to_transcript is called
    THEN the body is created correctly with proper newlines
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        save_dir = Path(tmpdir)
        filepath, _tid = manager.create_transcript(save_dir)

        initial_content = read_file(filepath)
        assert initial_content.endswith("\n\n")

        manager.append_to_transcript(filepath, "First line.")

        updated = read_file(filepath)
        body = updated[len(initial_content) :]

        # Body should start directly with the appended text, followed by a newline
        assert body.startswith("First line.")
        assert body.endswith("\n")


def test_append_to_transcript_is_atomic(tmp_path: Path):
    """GIVEN an existing transcript
    WHEN append_to_transcript is called
    THEN the file on disk always contains either the old or the full new content
    """
    save_dir = tmp_path
    filepath, _tid = manager.create_transcript(save_dir)

    before = read_file(filepath)

    manager.append_to_transcript(filepath, "Some new content.")

    after = read_file(filepath)

    # We should never see a partially-written file; content is either old or full new
    assert after != ""
    assert before in after


def test_update_status_updates_frontmatter_only(tmp_path: Path):
    """GIVEN an existing transcript
    WHEN update_status is called
    THEN the status field in the YAML frontmatter is updated
    AND the body content is preserved.
    """
    save_dir = tmp_path
    filepath, tid = manager.create_transcript(save_dir)

    # Append some body content so we can verify it is preserved
    manager.append_to_transcript(filepath, "Body content line 1.")
    manager.append_to_transcript(filepath, "Body content line 2.")

    original_content = read_file(filepath)
    assert f"id: '{tid}'" in original_content
    assert "status: recording" in original_content
    assert "Body content line 1." in original_content
    assert "Body content line 2." in original_content

    # WHEN: we update status to completed
    manager.update_status(filepath, "completed")

    updated_content = read_file(filepath)

    # THEN: status is updated, id and body are unchanged
    assert f"id: '{tid}'" in updated_content
    assert "status: completed" in updated_content
    assert "status: recording" not in updated_content
    assert "Body content line 1." in updated_content
    assert "Body content line 2." in updated_content


def test_update_status_is_atomic(tmp_path: Path, monkeypatch):
    """GIVEN an existing transcript
    WHEN update_status is called
    THEN the file is rewritten atomically via write_file_atomic.
    """
    save_dir = tmp_path
    filepath, _tid = manager.create_transcript(save_dir)

    # Patch write_file_atomic to record that it was used. We don't need to
    # delegate to the real implementation here; this test only asserts that
    # update_status *routes* writes through the atomic helper.
    calls = {"used": False}

    def fake_write_file_atomic(target, content):
        calls["used"] = True

    monkeypatch.setattr(manager, "write_file_atomic", fake_write_file_atomic)

    manager.update_status(filepath, "completed")

    assert calls["used"] is True


def test_update_language_updates_frontmatter_only(tmp_path: Path):
    """GIVEN an existing transcript
    WHEN update_language is called
    THEN the language field in the YAML frontmatter is updated
    AND the body content is preserved.
    """
    save_dir = tmp_path
    filepath, tid = manager.create_transcript(save_dir)

    # Append some body content so we can verify it is preserved
    manager.append_to_transcript(filepath, "Body content line 1.")
    manager.append_to_transcript(filepath, "Body content line 2.")

    original_content = read_file(filepath)
    assert f"id: '{tid}'" in original_content
    assert "language: auto" in original_content
    assert "Body content line 1." in original_content
    assert "Body content line 2." in original_content

    # WHEN: we update language to 'en'
    manager.update_language(filepath, "en")

    updated_content = read_file(filepath)

    # THEN: language is updated, id and body are unchanged
    assert f"id: '{tid}'" in updated_content
    assert "language: en" in updated_content
    assert "language: auto" not in updated_content
    assert "Body content line 1." in updated_content
    assert "Body content line 2." in updated_content


def test_update_language_is_atomic(tmp_path: Path, monkeypatch):
    """GIVEN an existing transcript
    WHEN update_language is called
    THEN the file is rewritten atomically via write_file_atomic.
    """
    save_dir = tmp_path
    filepath, _tid = manager.create_transcript(save_dir)

    calls = {"used": False}

    def fake_write_file_atomic(target, content):
        calls["used"] = True

    monkeypatch.setattr(manager, "write_file_atomic", fake_write_file_atomic)

    manager.update_language(filepath, "en")

    assert calls["used"] is True


def test_generate_frontmatter_allows_custom_language():
    """GIVEN transcript metadata with an explicit language
    WHEN generate_frontmatter is called
    THEN the language field reflects the provided value.
    """
    meta = TranscriptMetadata(
        transcript_id="000123",
        created=manager.datetime.now(),
        status="recording",
        language="en",
    )

    frontmatter = manager.generate_frontmatter(meta)
    assert "language: en" in frontmatter


def test_normalize_id_accepts_various_numeric_formats():
    """GIVEN several numeric ID representations
    WHEN normalize_id is called
    THEN they are all normalised to a zero-padded width.
    """
    # Single- and multi-digit forms should all map to the same padded ID
    assert manager.normalize_id("1") == "1".zfill(ID_WIDTH)
    assert manager.normalize_id("01") == "1".zfill(ID_WIDTH)
    assert manager.normalize_id("001") == "1".zfill(ID_WIDTH)
    assert manager.normalize_id("000001") == "1".zfill(ID_WIDTH)

    # Whitespace should be ignored
    assert manager.normalize_id("  42  ") == "42".zfill(ID_WIDTH)


def test_normalize_id_rejects_non_numeric_input():
    """GIVEN non-numeric input
    WHEN normalize_id is called
    THEN a TranscriptError is raised with a helpful message.
    """
    for value in ["abc", "12x", "", " ", "1-2", "00_001"]:
        try:
            manager.normalize_id(value)
        except manager.TranscriptError as exc:
            assert str(value.strip() or value) in exc.message
            assert "valid transcript ID" in exc.message
        else:  # pragma: no cover - defensive; the test will fail via assert
            assert False, f"Expected TranscriptError for input {value!r}"


def test_normalize_id_rejects_out_of_range_values():
    """GIVEN zero, negative or too-large numeric IDs
    WHEN normalize_id is called
    THEN a TranscriptError is raised to prevent invalid IDs.
    """
    too_large = str(10**ID_WIDTH)

    for value in ["0", "-1", too_large]:
        with pytest.raises(manager.TranscriptError) as exc_info:
            manager.normalize_id(value)

        message = str(exc_info.value)
        assert "out of range" in message


def test_get_next_id_returns_zero_when_directory_does_not_exist():
    """GIVEN get_next_id
    WHEN save_dir doesn't exist
    THEN returns "000000" (line 83)"""
    with tempfile.TemporaryDirectory() as tmpdir:
        nonexistent_dir = Path(tmpdir) / "nonexistent"
        next_id = manager.get_next_id(nonexistent_dir)
        assert next_id == "000000"


def test_get_next_id_skips_non_files():
    """GIVEN get_next_id
    WHEN directory contains subdirectories
    THEN subdirectories are skipped (line 89)"""
    with tempfile.TemporaryDirectory() as tmpdir:
        save_dir = Path(tmpdir)
        # Create a subdirectory
        subdir = save_dir / "subdir"
        subdir.mkdir()
        # Create a transcript file
        (save_dir / "transcript_20250101_000001.md").write_text("test")

        next_id = manager.get_next_id(save_dir)
        assert next_id == "000002"


def test_get_next_id_handles_invalid_id_strings():
    """GIVEN get_next_id
    WHEN filename has non-numeric ID
    THEN ValueError is caught and entry is skipped (lines 98-99)"""
    with tempfile.TemporaryDirectory() as tmpdir:
        save_dir = Path(tmpdir)
        # Create file with invalid ID
        (save_dir / "transcript_20250101_invalid.md").write_text("test")
        # Create valid file
        (save_dir / "transcript_20250101_000005.md").write_text("test")

        next_id = manager.get_next_id(save_dir)
        assert next_id == "000006"


def test_create_transcript_handles_collision_retry(monkeypatch):
    """GIVEN create_transcript
    WHEN filename collision occurs
    THEN retries with next ID (lines 185-189)"""
    from datetime import datetime

    # Mock datetime.now() to return a fixed date so the test file matches
    fixed_date = datetime(2025, 1, 1, 12, 0, 0)

    # Create a mock datetime class that has now() returning fixed_date
    # and can be used like the real datetime class
    class MockDatetime:
        @staticmethod
        def now() -> datetime:
            return fixed_date

        @staticmethod
        def strftime(date_obj: datetime, fmt: str) -> str:
            return date_obj.strftime(fmt)

    monkeypatch.setattr(manager, "datetime", MockDatetime)

    with tempfile.TemporaryDirectory() as tmpdir:
        save_dir = Path(tmpdir)
        # Create a file that would cause collision (using the same date as mocked)
        # Use new format: ID_transcript_YYYYMMDD.md
        (save_dir / "000001_transcript_20250101.md").write_text("existing")

        # Mock get_next_id to return same ID first time, then next
        call_count = [0]

        def mock_get_next_id(save_dir):
            call_count[0] += 1
            if call_count[0] == 1:
                return "000001"  # Collision
            return "000002"  # Next attempt

        with patch.object(manager, "get_next_id", side_effect=mock_get_next_id):
            filepath, tid = manager.create_transcript(save_dir)
            assert tid == "000002"
            assert filepath.exists()


def test_append_to_transcript_handles_empty_body():
    """GIVEN append_to_transcript
    WHEN body is empty
    THEN appends correctly (line 211)"""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "transcript.md"
        # Create file with frontmatter but empty body
        content = "---\nid: '000001'\n---\n"
        filepath.write_text(content)

        manager.append_to_transcript(filepath, "new text")

        result = filepath.read_text()
        assert "new text" in result
        assert result.startswith("---")


def test_update_status_handles_missing_frontmatter():
    """GIVEN update_status
    WHEN file doesn't start with ---
    THEN TranscriptError is raised (line 239)"""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "transcript.md"
        filepath.write_text("No frontmatter here")

        with pytest.raises(manager.TranscriptError, match="missing YAML frontmatter"):
            manager.update_status(filepath, "completed")


def test_update_language_handles_missing_frontmatter():
    """GIVEN update_language
    WHEN file doesn't start with ---
    THEN TranscriptError is raised (line 308)"""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "transcript.md"
        filepath.write_text("No frontmatter here")

        with pytest.raises(manager.TranscriptError, match="missing YAML frontmatter"):
            manager.update_language(filepath, "en")


def test_update_language_handles_invalid_yaml():
    """GIVEN update_language
    WHEN frontmatter has invalid YAML
    THEN TranscriptError is raised (line 336)"""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "transcript.md"
        # Invalid YAML in frontmatter
        content = "---\nid: '000001'\ninvalid: [unclosed\n---\nbody"
        filepath.write_text(content)

        with pytest.raises(manager.TranscriptError, match="invalid YAML"):
            manager.update_language(filepath, "en")


# Tests for R-011: Filename Order Normalisation


def test_create_transcript_uses_new_format():
    """GIVEN create_transcript is called
    WHEN a new transcript is created
    THEN it uses the new format: ID_transcript_YYYYMMDD.md"""
    with tempfile.TemporaryDirectory() as tmpdir:
        save_dir = Path(tmpdir)

        filepath, tid = manager.create_transcript(save_dir)

        # Should use new format: {ID}_transcript_{YYYYMMDD}.md
        pattern = rf"^{tid}_transcript_\d{{8}}\.md$"
        assert re.match(
            pattern, filepath.name
        ), f"Filename {filepath.name} doesn't match new format"


def test_get_next_id_recognizes_old_format():
    """GIVEN old-format files exist
    WHEN get_next_id is called
    THEN it finds IDs from old-format files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        save_dir = Path(tmpdir)
        # Create old-format files
        (save_dir / "transcript_20250120_000001.md").write_text("test")
        (save_dir / "transcript_20250121_000005.md").write_text("test")

        next_id = manager.get_next_id(save_dir)

        assert next_id == "000006"


def test_get_next_id_recognizes_new_format():
    """GIVEN new-format files exist
    WHEN get_next_id is called
    THEN it finds IDs from new-format files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        save_dir = Path(tmpdir)
        # Create new-format files
        (save_dir / "000001_transcript_20250120.md").write_text("test")
        (save_dir / "000005_transcript_20250121.md").write_text("test")

        next_id = manager.get_next_id(save_dir)

        assert next_id == "000006"


def test_get_next_id_handles_mixed_formats():
    """GIVEN both old and new format files exist
    WHEN get_next_id is called
    THEN it correctly finds the max ID from both formats"""
    with tempfile.TemporaryDirectory() as tmpdir:
        save_dir = Path(tmpdir)
        # Create mixed format files
        (save_dir / "transcript_20250120_000001.md").write_text("test")  # Old format
        (save_dir / "000005_transcript_20250121.md").write_text("test")  # New format
        (save_dir / "transcript_20250122_000003.md").write_text("test")  # Old format
        (save_dir / "000010_transcript_20250123.md").write_text("test")  # New format

        next_id = manager.get_next_id(save_dir)

        # Should find max ID (000010) and return next (000011)
        assert next_id == "000011"


def test_parse_transcript_filename_old_format():
    """GIVEN an old-format filename
    WHEN parse_transcript_filename is called
    THEN it returns date and ID correctly"""
    result = manager.parse_transcript_filename("transcript_20250120_000042.md")
    assert result == ("20250120", "000042")


def test_parse_transcript_filename_new_format():
    """GIVEN a new-format filename
    WHEN parse_transcript_filename is called
    THEN it returns ID and date correctly"""
    result = manager.parse_transcript_filename("000042_transcript_20250120.md")
    assert result == ("20250120", "000042")


def test_parse_transcript_filename_invalid():
    """GIVEN an invalid filename
    WHEN parse_transcript_filename is called
    THEN it raises TranscriptError"""
    with pytest.raises(manager.TranscriptError):
        manager.parse_transcript_filename("invalid_filename.md")
