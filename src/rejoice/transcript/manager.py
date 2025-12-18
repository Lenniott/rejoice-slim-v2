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
