"""Tests for transcript file manager ([R-003])."""

from pathlib import Path
import re
import tempfile

from rejoice.transcript import manager
from rejoice.transcript.manager import TranscriptMetadata


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
