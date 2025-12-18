"""Transcript package.

Provides helpers for managing markdown transcript files.
"""

from .manager import (  # noqa: F401
    TranscriptMetadata,
    create_transcript,
    generate_frontmatter,
    get_next_id,
    write_file_atomic,
)
