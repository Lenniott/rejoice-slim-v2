"""Tests for transcript filename migration helper ([R-011])."""

from pathlib import Path
import tempfile

from rejoice.transcript.manager import (
    find_old_format_files,
    migrate_filenames,
    rename_transcript_file,
    validate_migration,
)


def test_find_old_format_files():
    """GIVEN a directory with old-format files
    WHEN find_old_format_files is called
    THEN it returns all files matching old format"""
    with tempfile.TemporaryDirectory() as tmpdir:
        save_dir = Path(tmpdir)

        # Create old-format files
        (save_dir / "transcript_20250120_000001.md").write_text("test1")
        (save_dir / "transcript_20250121_000002.md").write_text("test2")

        # Create new-format file (should be ignored)
        (save_dir / "000003_transcript_20250122.md").write_text("test3")

        # Create non-transcript file (should be ignored)
        (save_dir / "other_file.md").write_text("test4")

        old_files = find_old_format_files(save_dir)

        assert len(old_files) == 2
        assert all(f.name.startswith("transcript_") for f in old_files)


def test_find_old_format_files_empty_directory():
    """GIVEN an empty directory
    WHEN find_old_format_files is called
    THEN it returns an empty list"""
    with tempfile.TemporaryDirectory() as tmpdir:
        save_dir = Path(tmpdir)

        old_files = find_old_format_files(save_dir)

        assert old_files == []


def test_find_old_format_files_nonexistent_directory():
    """GIVEN a nonexistent directory
    WHEN find_old_format_files is called
    THEN it returns an empty list"""
    with tempfile.TemporaryDirectory() as tmpdir:
        nonexistent_dir = Path(tmpdir) / "nonexistent"

        old_files = find_old_format_files(nonexistent_dir)

        assert old_files == []


def test_rename_transcript_file_atomic():
    """GIVEN an old-format file
    WHEN rename_transcript_file is called
    THEN the file is renamed to new format atomically"""
    with tempfile.TemporaryDirectory() as tmpdir:
        old_path = Path(tmpdir) / "transcript_20250120_000042.md"
        new_path = Path(tmpdir) / "000042_transcript_20250120.md"

        content = "test content"
        old_path.write_text(content)

        rename_transcript_file(old_path, new_path)

        # Old file should not exist
        assert not old_path.exists()

        # New file should exist with same content
        assert new_path.exists()
        assert new_path.read_text() == content


def test_validate_migration_success():
    """GIVEN a successful migration
    WHEN validate_migration is called
    THEN it returns True"""
    with tempfile.TemporaryDirectory() as tmpdir:
        old_path = Path(tmpdir) / "transcript_20250120_000042.md"
        new_path = Path(tmpdir) / "000042_transcript_20250120.md"

        # Simulate successful migration
        old_path.write_text("test")
        old_path.rename(new_path)

        assert validate_migration(old_path, new_path) is True


def test_validate_migration_failure_old_exists():
    """GIVEN a migration where old file still exists
    WHEN validate_migration is called
    THEN it returns False"""
    with tempfile.TemporaryDirectory() as tmpdir:
        old_path = Path(tmpdir) / "transcript_20250120_000042.md"
        new_path = Path(tmpdir) / "000042_transcript_20250120.md"

        # Both files exist (migration incomplete)
        old_path.write_text("test")
        new_path.write_text("test")

        assert validate_migration(old_path, new_path) is False


def test_validate_migration_failure_new_missing():
    """GIVEN a migration where new file doesn't exist
    WHEN validate_migration is called
    THEN it returns False"""
    with tempfile.TemporaryDirectory() as tmpdir:
        old_path = Path(tmpdir) / "transcript_20250120_000042.md"
        new_path = Path(tmpdir) / "000042_transcript_20250120.md"

        # Old file exists, new doesn't (migration failed)
        old_path.write_text("test")

        assert validate_migration(old_path, new_path) is False


def test_migrate_filenames_dry_run():
    """GIVEN old-format files
    WHEN migrate_filenames is called with dry_run=True
    THEN files are not modified"""
    with tempfile.TemporaryDirectory() as tmpdir:
        save_dir = Path(tmpdir)

        # Create old-format files
        old_file1 = save_dir / "transcript_20250120_000001.md"
        old_file2 = save_dir / "transcript_20250121_000002.md"
        old_file1.write_text("content1")
        old_file2.write_text("content2")

        result = migrate_filenames(save_dir, dry_run=True)

        # Files should still exist with old names
        assert old_file1.exists()
        assert old_file2.exists()

        # Result should indicate dry run
        assert result["dry_run"] is True
        assert result["renamed"] == 2
        assert len(result["operations"]) == 2


def test_migrate_filenames_execute():
    """GIVEN old-format files
    WHEN migrate_filenames is called with dry_run=False
    THEN files are renamed to new format"""
    with tempfile.TemporaryDirectory() as tmpdir:
        save_dir = Path(tmpdir)

        # Create old-format files
        old_file1 = save_dir / "transcript_20250120_000001.md"
        old_file2 = save_dir / "transcript_20250121_000002.md"
        content1 = "content1"
        content2 = "content2"
        old_file1.write_text(content1)
        old_file2.write_text(content2)

        result = migrate_filenames(save_dir, dry_run=False)

        # Old files should not exist
        assert not old_file1.exists()
        assert not old_file2.exists()

        # New files should exist with correct names and content
        new_file1 = save_dir / "000001_transcript_20250120.md"
        new_file2 = save_dir / "000002_transcript_20250121.md"
        assert new_file1.exists()
        assert new_file2.exists()
        assert new_file1.read_text() == content1
        assert new_file2.read_text() == content2

        # Result should indicate success
        assert result["dry_run"] is False
        assert result["renamed"] == 2
        assert result["failed"] == 0


def test_migrate_filenames_handles_mixed_formats():
    """GIVEN a directory with both old and new format files
    WHEN migrate_filenames is called
    THEN only old-format files are migrated"""
    with tempfile.TemporaryDirectory() as tmpdir:
        save_dir = Path(tmpdir)

        # Create old-format file
        old_file = save_dir / "transcript_20250120_000001.md"
        old_file.write_text("old format")

        # Create new-format file (should be left alone)
        new_file = save_dir / "000002_transcript_20250121.md"
        new_file.write_text("new format")

        result = migrate_filenames(save_dir, dry_run=False)

        # Old file should be migrated
        assert not old_file.exists()
        assert (save_dir / "000001_transcript_20250120.md").exists()

        # New file should be unchanged
        assert new_file.exists()

        # Only one file should be migrated
        assert result["renamed"] == 1


def test_migrate_filenames_handles_collision():
    """GIVEN an old-format file where new filename already exists
    WHEN migrate_filenames is called
    THEN migration fails gracefully for that file"""
    with tempfile.TemporaryDirectory() as tmpdir:
        save_dir = Path(tmpdir)

        # Create old-format file
        old_file = save_dir / "transcript_20250120_000001.md"
        old_file.write_text("old format")

        # Create new-format file with same ID and date (collision)
        new_file = save_dir / "000001_transcript_20250120.md"
        new_file.write_text("new format")

        result = migrate_filenames(save_dir, dry_run=False)

        # Old file should still exist (migration failed)
        assert old_file.exists()

        # New file should be unchanged
        assert new_file.exists()
        assert new_file.read_text() == "new format"

        # Migration should report failure
        assert result["failed"] == 1
        assert result["renamed"] == 0


def test_migrate_filenames_empty_directory():
    """GIVEN an empty directory
    WHEN migrate_filenames is called
    THEN it returns empty results"""
    with tempfile.TemporaryDirectory() as tmpdir:
        save_dir = Path(tmpdir)

        result = migrate_filenames(save_dir, dry_run=False)

        assert result["renamed"] == 0
        assert result["failed"] == 0
        assert result["operations"] == []


def test_migrate_filenames_preserves_content():
    """GIVEN old-format files with content
    WHEN migrate_filenames is called
    THEN file content is preserved"""
    with tempfile.TemporaryDirectory() as tmpdir:
        save_dir = Path(tmpdir)

        # Create old-format file with specific content
        old_file = save_dir / "transcript_20250120_000042.md"
        original_content = "---\nid: '000042'\n---\n\nThis is the transcript content."
        old_file.write_text(original_content)

        result = migrate_filenames(save_dir, dry_run=False)

        # New file should have same content
        new_file = save_dir / "000042_transcript_20250120.md"
        assert new_file.exists()
        assert new_file.read_text() == original_content

        assert result["renamed"] == 1
