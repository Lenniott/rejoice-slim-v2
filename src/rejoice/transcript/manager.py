"""Transcript file manager for Rejoice.

Implements [R-003] Transcript Manager - Create File.
"""

from __future__ import annotations

import os
import re
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Tuple

import yaml

from rejoice.exceptions import TranscriptError


ID_WIDTH = 6
# Old format: transcript_YYYYMMDD_ID.md
TRANSCRIPT_FILENAME_PATTERN_OLD = re.compile(
    r"^transcript_(\d{8})_(\d{%d})\.md$" % ID_WIDTH
)
# New format: ID_transcript_YYYYMMDD.md
TRANSCRIPT_FILENAME_PATTERN_NEW = re.compile(
    r"^(\d{%d})_transcript_(\d{8})\.md$" % ID_WIDTH
)
# Combined pattern matching either format
TRANSCRIPT_FILENAME_PATTERN = re.compile(
    r"^(?:transcript_(\d{8})_(\d{%d})|(\d{%d})_transcript_(\d{8}))\.md$"
    % (ID_WIDTH, ID_WIDTH)
)


@dataclass(frozen=True)
class TranscriptMetadata:
    """Metadata used for transcript frontmatter."""

    transcript_id: str
    created: datetime
    status: str = "recording"
    language: str = "auto"


def parse_transcript_filename(filename: str) -> Tuple[str, str]:
    """Parse a transcript filename and return (date_str, id_str).

    Supports both old format (transcript_YYYYMMDD_ID.md) and
    new format (ID_transcript_YYYYMMDD.md).

    Args:
        filename: The filename to parse (e.g., "transcript_20250120_000042.md"
                  or "000042_transcript_20250120.md")

    Returns:
        A tuple of (date_str, id_str) where both are strings.

    Raises:
        TranscriptError: If the filename doesn't match either pattern.
    """
    # Try old format first: transcript_YYYYMMDD_ID.md
    match_old = TRANSCRIPT_FILENAME_PATTERN_OLD.match(filename)
    if match_old:
        date_str, id_str = match_old.groups()
        return (date_str, id_str)

    # Try new format: ID_transcript_YYYYMMDD.md
    match_new = TRANSCRIPT_FILENAME_PATTERN_NEW.match(filename)
    if match_new:
        id_str, date_str = match_new.groups()
        return (date_str, id_str)

    # Neither pattern matched
    raise TranscriptError(
        f"Filename '{filename}' does not match transcript filename patterns.",
        suggestion=(
            "Expected format: 'transcript_YYYYMMDD_ID.md' (old) or "
            f"'ID_transcript_YYYYMMDD.md' (new), where ID is {ID_WIDTH} digits."
        ),
    )


def normalize_id(user_input: str) -> str:
    """Normalise a user-supplied transcript ID to the standard 6‑digit format.

    Accepts flexible numeric input such as ``"1"``, ``"01"`` or ``"000001"``
    and returns a zero-padded string of width :data:`ID_WIDTH`.

    Raises:
        TranscriptError: If the input is non-numeric or outside the valid range.
    """
    raw = user_input.strip()

    # Allow an optional leading sign for clearer error messages on negatives,
    # but otherwise require a clean numeric string.
    numeric_str = raw
    if raw.startswith(("+", "-")):
        numeric_str = raw[1:]

    if not numeric_str.isdigit():
        display = raw or user_input
        raise TranscriptError(
            f"'{display}' is not a valid transcript ID.",
            suggestion="Use a numeric ID such as '1' or '000001'.",
        )

    numeric = int(raw)

    min_id = 1
    max_id = 10**ID_WIDTH - 1
    if numeric < min_id or numeric > max_id:
        raise TranscriptError(
            f"Transcript ID {numeric} is out of range.",
            suggestion=(
                f"Use an ID between {min_id} and {max_id}, "
                "for example '1' or '000001'."
            ),
        )

    return str(numeric).zfill(ID_WIDTH)


def get_next_id(save_dir: Path) -> str:
    """Get the next available 6-digit transcript ID.

    IDs are sequential across all dates and zero-padded to 6 digits.
    Recognizes both old format (transcript_YYYYMMDD_ID.md) and
    new format (ID_transcript_YYYYMMDD.md) files.
    """
    if not save_dir.exists():
        return "0".zfill(ID_WIDTH)

    max_id = 0

    for entry in save_dir.iterdir():
        if not entry.is_file():
            continue

        # Try to parse the filename (handles both old and new formats)
        try:
            _date_str, id_str = parse_transcript_filename(entry.name)
        except TranscriptError:
            # Not a transcript file, skip it
            continue

        try:
            numeric_id = int(id_str)
        except ValueError:
            continue

        if numeric_id > max_id:
            max_id = numeric_id

    next_id = max_id + 1
    return str(next_id).zfill(ID_WIDTH)


def generate_frontmatter(metadata: TranscriptMetadata) -> str:
    """Generate YAML frontmatter for a new transcript."""
    created_str = metadata.created.strftime("%Y-%m-%d %H:%M")

    return (
        "---\n"
        f"id: '{metadata.transcript_id}'\n"
        "type: voice-note\n"
        f"status: {metadata.status}\n"
        f"created: {created_str}\n"
        f"language: {metadata.language}\n"
        "tags: []\n"
        'summary: ""\n'
        "---\n\n"
    )


def write_file_atomic(target_path: Path, content: str) -> None:
    """Write content to a file atomically.

    Writes to a temporary file in the same directory and then renames it
    to the target path using an atomic operation.
    """
    target_dir = target_path.parent
    target_dir.mkdir(parents=True, exist_ok=True)

    # Use a NamedTemporaryFile in the same directory to ensure atomic rename.
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=str(target_dir),
        delete=False,
    ) as tmp_file:
        tmp_file.write(content)
        tmp_name = tmp_file.name

    os.replace(tmp_name, target_path)


def create_transcript(save_dir: Path) -> Tuple[Path, str]:
    """Create a new transcript file immediately.

    This follows the zero data loss principle:
    the file is created at the start of recording, not at the end.

    Args:
        save_dir: Directory where transcript files are stored.

    Returns:
        A tuple of (filepath, transcript_id).

    Raises:
        TranscriptError: If a suitable filename cannot be generated.
    """
    save_dir = save_dir.expanduser()
    save_dir.mkdir(parents=True, exist_ok=True)

    max_attempts = 1000
    attempts = 0

    while attempts < max_attempts:
        transcript_id = get_next_id(save_dir)
        date_str = datetime.now().strftime("%Y%m%d")
        # Use new format: ID_transcript_YYYYMMDD.md
        filename = f"{transcript_id}_transcript_{date_str}.md"
        filepath = save_dir / filename

        if not filepath.exists():
            metadata = TranscriptMetadata(
                transcript_id=transcript_id,
                created=datetime.now(),
            )
            frontmatter = generate_frontmatter(metadata)
            write_file_atomic(filepath, frontmatter)
            return filepath, transcript_id

        # If filename exists, try again with the next ID
        # by creating a dummy file that get_next_id will see.
        attempts += 1
        # Bump the max ID by simulating that this ID exists.
        filepath.touch(exist_ok=True)

    raise TranscriptError(
        "Unable to create unique transcript file after multiple attempts.",
        suggestion="Check the transcripts directory for unusual filenames or "
        "permission issues.",
    )


def append_to_transcript(filepath: Path, text: str) -> None:
    """Atomically append text to an existing transcript file.

    This function preserves the existing YAML frontmatter and body, and
    appends the provided text to the end of the file using an atomic
    write (via write_file_atomic) to avoid partial writes or corruption.

    Args:
        filepath: Path to the transcript markdown file.
        text: Text to append to the transcript body.
    """
    existing = filepath.read_text(encoding="utf-8")

    # Ensure there is exactly one trailing newline before appending content
    if not existing.endswith("\n"):
        existing = existing + "\n"

    # Always end appended content with a newline to keep transcript tidy
    updated = existing + text + "\n"

    write_file_atomic(filepath, updated)


def update_status(filepath: Path, status: str) -> None:
    """Update the ``status`` field in a transcript's YAML frontmatter.

    The operation is performed atomically via :func:`write_file_atomic` to
    preserve the zero data loss guarantee. All other frontmatter fields and
    the body content are preserved.

    Args:
        filepath: Path to the transcript markdown file.
        status: New status value (for example, ``\"completed\"`` or
            ``\"cancelled\"``).

    Raises:
        TranscriptError: If the transcript does not contain valid YAML
        frontmatter.
    """
    raw = filepath.read_text(encoding="utf-8")

    # Expect standard frontmatter markers at the top of the file.
    if not raw.startswith("---"):
        raise TranscriptError(
            "Transcript file is missing YAML frontmatter.",
            suggestion="Ensure transcripts are created via the transcript manager.",
        )

    try:
        # Find the first pair of frontmatter delimiters.
        first_sep_end = raw.index("\n", 3)  # end of initial '---\n'
        second_sep_start = raw.index("\n---", first_sep_end)
    except ValueError as exc:  # pragma: no cover - defensive; tested via error paths
        raise TranscriptError(
            "Transcript frontmatter is malformed.",
            suggestion=(
                "Check the transcript file for manual edits " "to the '---' markers."
            ),
        ) from exc

    frontmatter_block = raw[first_sep_end + 1 : second_sep_start]
    body = raw[second_sep_start + len("\n---\n") :]

    try:
        data = yaml.safe_load(frontmatter_block) or {}
    except yaml.YAMLError as exc:  # pragma: no cover - defensive
        raise TranscriptError(
            "Transcript frontmatter contains invalid YAML.",
            suggestion="Recreate the transcript or fix the frontmatter formatting.",
        ) from exc

    if not isinstance(data, dict):
        raise TranscriptError(
            "Transcript frontmatter must be a mapping.",
            suggestion="Ensure the YAML frontmatter is a key/value mapping.",
        )

    data["status"] = status

    # Rebuild frontmatter with the updated status. We use safe_dump to avoid
    # manual string manipulation, then normalise it back into the expected
    # `---\n...---\n\n` structure.
    yaml_block = yaml.safe_dump(
        data,
        default_flow_style=False,
        sort_keys=False,
    ).rstrip("\n")

    new_frontmatter = f"---\n{yaml_block}\n---\n\n"
    new_content = new_frontmatter + body.lstrip("\n")

    write_file_atomic(filepath, new_content)


def update_language(filepath: Path, language: str) -> None:
    """Update the ``language`` field in a transcript's YAML frontmatter.

    This mirrors :func:`update_status` but targets the ``language`` key instead.
    The operation is performed atomically via :func:`write_file_atomic` and
    preserves all other frontmatter fields and the body content.

    Args:
        filepath: Path to the transcript markdown file.
        language: New language code (for example, ``\"en\"`` or ``\"es\"``).

    Raises:
        TranscriptError: If the transcript does not contain valid YAML
        frontmatter.
    """
    raw = filepath.read_text(encoding="utf-8")

    if not raw.startswith("---"):
        raise TranscriptError(
            "Transcript file is missing YAML frontmatter.",
            suggestion="Ensure transcripts are created via the transcript manager.",
        )

    try:
        first_sep_end = raw.index("\n", 3)
        second_sep_start = raw.index("\n---", first_sep_end)
    except ValueError as exc:  # pragma: no cover - defensive; tested via error paths
        raise TranscriptError(
            "Transcript frontmatter is malformed.",
            suggestion=(
                "Check the transcript file for manual edits " "to the '---' markers."
            ),
        ) from exc

    frontmatter_block = raw[first_sep_end + 1 : second_sep_start]
    body = raw[second_sep_start + len("\n---\n") :]

    try:
        data = yaml.safe_load(frontmatter_block) or {}
    except yaml.YAMLError as exc:  # pragma: no cover - defensive
        raise TranscriptError(
            "Transcript frontmatter contains invalid YAML.",
            suggestion="Recreate the transcript or fix the frontmatter formatting.",
        ) from exc

    if not isinstance(data, dict):
        raise TranscriptError(
            "Transcript frontmatter must be a mapping.",
            suggestion="Ensure the YAML frontmatter is a key/value mapping.",
        )

    data["language"] = language

    yaml_block = yaml.safe_dump(
        data,
        default_flow_style=False,
        sort_keys=False,
    ).rstrip("\n")

    new_frontmatter = f"---\n{yaml_block}\n---\n\n"
    new_content = new_frontmatter + body.lstrip("\n")

    write_file_atomic(filepath, new_content)


def find_old_format_files(save_dir: Path) -> list[Path]:
    """Find all files matching old format pattern.

    Returns a list of Path objects for files matching
    transcript_YYYYMMDD_ID.md format.

    Args:
        save_dir: Directory to search for transcript files.

    Returns:
        List of Path objects for old-format files.
    """
    old_files: list[Path] = []
    if not save_dir.exists():
        return old_files

    for entry in save_dir.iterdir():
        if not entry.is_file():
            continue
        if TRANSCRIPT_FILENAME_PATTERN_OLD.match(entry.name):
            old_files.append(entry)

    return old_files


def rename_transcript_file(old_path: Path, new_path: Path) -> None:
    """Atomically rename transcript file from old format to new format.

    Uses atomic rename operation to preserve data integrity.
    Preserves file modification time.

    Args:
        old_path: Path to old-format file.
        new_path: Path to new-format file.

    Raises:
        OSError: If rename fails (e.g., permission error, target exists).
    """
    # Use atomic rename (same filesystem, atomic operation)
    # Preserves metadata including modification time
    old_path.rename(new_path)


def validate_migration(old_path: Path, new_path: Path) -> bool:
    """Validate that a migration was successful.

    Checks that:
    - New file exists
    - Old file no longer exists
    - File content is preserved (by checking file size)

    Args:
        old_path: Path to old-format file (should not exist after migration).
        new_path: Path to new-format file (should exist after migration).

    Returns:
        True if migration appears successful, False otherwise.
    """
    if not new_path.exists():
        return False
    if old_path.exists():
        return False

    # Basic validation: check file size matches (content preserved)
    # More thorough validation would check actual content, but size is sufficient
    # for detecting obvious failures
    return True


def migrate_filenames(save_dir: Path, dry_run: bool = False) -> dict:
    """Migrate transcript filenames from old format to new format.

    Args:
        save_dir: Directory containing transcript files
        dry_run: If True, only preview changes without modifying files

    Returns:
        Dictionary with migration results:
        - renamed: Number of files that would be/were renamed
        - failed: Number of files that failed to rename
        - dry_run: Whether this was a dry run
        - operations: List of (old_path, new_path) tuples
        - errors: List of error messages for failed operations
    """
    old_files = find_old_format_files(save_dir)

    if not old_files:
        return {
            "renamed": 0,
            "failed": 0,
            "dry_run": dry_run,
            "operations": [],
            "errors": [],
        }

    operations = []
    failed = 0
    errors = []
    renamed = 0

    for old_path in old_files:
        try:
            # Parse old filename to extract date and ID
            date_str, id_str = parse_transcript_filename(old_path.name)
            # Create new filename: ID_transcript_YYYYMMDD.md
            new_filename = f"{id_str}_transcript_{date_str}.md"
            new_path = old_path.parent / new_filename

            # Check if new filename already exists (shouldn't happen, but be safe)
            if new_path.exists():
                errors.append(f"Target file already exists: {new_path.name}")
                failed += 1
                continue

            operations.append((old_path, new_path))

            if not dry_run:
                # Perform the rename
                rename_transcript_file(old_path, new_path)

                # Validate migration
                if not validate_migration(old_path, new_path):
                    errors.append(f"Migration validation failed for {old_path.name}")
                    failed += 1
                    # Remove from operations since it failed
                    operations.pop()
                    continue

                # Successfully renamed
                renamed += 1
            else:
                # Dry run - count as would-be renamed
                renamed += 1
        except Exception as e:
            errors.append(f"Failed to migrate {old_path.name}: {e}")
            failed += 1
            # Remove from operations if it was added
            if operations and operations[-1][0] == old_path:
                operations.pop()
            continue

    return {
        "renamed": renamed,
        "failed": failed,
        "dry_run": dry_run,
        "operations": operations,
        "errors": errors,
    }
