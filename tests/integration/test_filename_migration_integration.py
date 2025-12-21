"""Integration tests for transcript filename migration ([R-011])."""

from pathlib import Path
import tempfile

from rejoice.transcript.manager import (
    create_transcript,
    migrate_filenames,
    parse_transcript_filename,
)


def test_list_command_after_migration():
    """GIVEN a directory with both old and new format files
    WHEN files are scanned using parse_transcript_filename
    THEN both formats are recognized"""
    with tempfile.TemporaryDirectory() as tmpdir:
        save_dir = Path(tmpdir)

        # Create old-format file
        old_file = save_dir / "transcript_20250120_000001.md"
        old_file.write_text("---\nid: '000001'\n---\n\nOld format content")

        # Create new-format file
        new_file = save_dir / "000002_transcript_20250121.md"
        new_file.write_text("---\nid: '000002'\n---\n\nNew format content")

        # Scan for transcript files (simulating _iter_transcripts)
        transcripts = []
        for entry in save_dir.iterdir():
            if entry.is_file():
                try:
                    parse_transcript_filename(entry.name)
                    transcripts.append(entry)
                except Exception:
                    pass

        # Should find both files
        assert len(transcripts) == 2
        assert old_file in transcripts
        assert new_file in transcripts


def test_view_command_after_migration():
    """GIVEN migrated files
    WHEN files are searched by ID
    THEN they can be found regardless of format"""
    with tempfile.TemporaryDirectory() as tmpdir:
        save_dir = Path(tmpdir)

        # Create old-format file
        old_file = save_dir / "transcript_20250120_000042.md"
        old_file.write_text("---\nid: '000042'\n---\n\nContent")

        # Should be able to parse old-format file
        date_str, id_str = parse_transcript_filename(old_file.name)
        assert id_str == "000042"

        # Migrate to new format
        migrate_filenames(save_dir, dry_run=False)

        # Should still be able to parse new-format file
        new_file = save_dir / "000042_transcript_20250120.md"
        assert new_file.exists()
        date_str2, id_str2 = parse_transcript_filename(new_file.name)
        assert id_str2 == "000042"


def test_migration_cli_workflow():
    """GIVEN old-format files
    WHEN migration is performed
    THEN files can still be parsed and accessed correctly"""
    with tempfile.TemporaryDirectory() as tmpdir:
        save_dir = Path(tmpdir)

        # Create old-format files
        old_file1 = save_dir / "transcript_20250120_000001.md"
        old_file2 = save_dir / "transcript_20250121_000002.md"
        old_file1.write_text("---\nid: '000001'\n---\n\nContent 1")
        old_file2.write_text("---\nid: '000002'\n---\n\nContent 2")

        # Verify files can be parsed before migration
        transcripts_before = []
        for entry in save_dir.iterdir():
            if entry.is_file():
                try:
                    parse_transcript_filename(entry.name)
                    transcripts_before.append(entry)
                except Exception:
                    pass
        assert len(transcripts_before) == 2

        # Perform migration
        result = migrate_filenames(save_dir, dry_run=False)
        assert result["renamed"] == 2
        assert result["failed"] == 0

        # Verify files can still be parsed after migration
        transcripts_after = []
        for entry in save_dir.iterdir():
            if entry.is_file():
                try:
                    date_str, id_str = parse_transcript_filename(entry.name)
                    transcripts_after.append((entry, id_str))
                except Exception:
                    pass
        assert len(transcripts_after) == 2

        # Verify IDs are correct
        ids = {id_str for _, id_str in transcripts_after}
        assert "000001" in ids
        assert "000002" in ids


def test_mixed_formats_after_migration():
    """GIVEN a directory with both old and new format files
    WHEN new transcripts are created
    THEN they use new format and coexist with old format files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        save_dir = Path(tmpdir)

        # Create old-format file
        old_file = save_dir / "transcript_20250120_000001.md"
        old_file.write_text("---\nid: '000001'\n---\n\nOld")

        # Create new transcript (should use new format)
        new_file, new_id = create_transcript(save_dir)

        # Verify new file uses new format
        assert new_file.name.startswith(f"{new_id}_transcript_")

        # Verify both files are found (can be parsed)
        transcripts = []
        for entry in save_dir.iterdir():
            if entry.is_file():
                try:
                    parse_transcript_filename(entry.name)
                    transcripts.append(entry)
                except Exception:
                    pass
        assert len(transcripts) == 2
        assert old_file in transcripts
        assert new_file in transcripts
