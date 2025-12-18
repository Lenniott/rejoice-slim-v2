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
TRANSCRIPT_FILENAME_PATTERN = re.compile(
    r"^transcript_(\d{8})_(\d{%d})\.md$" % ID_WIDTH
)


@dataclass(frozen=True)
class TranscriptMetadata:
    """Metadata used for transcript frontmatter."""

    transcript_id: str
    created: datetime
    status: str = "recording"
    language: str = "auto"


def get_next_id(save_dir: Path) -> str:
    """Get the next available 6-digit transcript ID.

    IDs are sequential across all dates and zero-padded to 6 digits.
    """
    if not save_dir.exists():
        return "0".zfill(ID_WIDTH)

    max_id = 0

    for entry in save_dir.iterdir():
        if not entry.is_file():
            continue

        match = TRANSCRIPT_FILENAME_PATTERN.match(entry.name)
        if not match:
            continue

        _date_str, id_str = match.groups()
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
        filename = f"transcript_{date_str}_{transcript_id}.md"
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
