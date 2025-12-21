"""Audio archiving utilities for [R-013].

Provides functions to archive temporary audio files to permanent storage
alongside transcript files.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def ensure_audio_directory_exists(transcript_dir: Path) -> Path:
    """Ensure the audio/ subdirectory exists within the transcript directory.

    Args:
        transcript_dir: Directory containing transcript files.

    Returns:
        Path to the audio directory.
    """
    audio_dir = transcript_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    return audio_dir


def get_archived_audio_path(transcript_path: Path) -> Path:
    """Get the expected archive path for an audio file matching a transcript.

    Args:
        transcript_path: Path to the transcript markdown file.

    Returns:
        Path where the audio file should be archived (relative to transcript directory).

    Examples:
        >>> transcript = Path("/transcripts/000054_transcript_20251220.md")
        >>> get_archived_audio_path(transcript)
        Path("/transcripts/audio/000054_transcript_20251220.wav")
    """
    audio_dir = transcript_path.parent / "audio"
    # Use transcript filename stem (without .md) and change extension to .wav
    audio_filename = transcript_path.stem + ".wav"
    return audio_dir / audio_filename


def archive_audio_file(temp_audio_path: Path, transcript_path: Path) -> Path:
    """Move temporary audio file to permanent archive location.

    The audio file is moved to an `audio/` subdirectory within the transcript
    directory, with a filename matching the transcript (e.g., if transcript is
    `000054_transcript_20251220.md`, the audio file will be
    `audio/000054_transcript_20251220.wav`).

    If a file already exists at the target location, a timestamp suffix is
    appended to avoid overwriting (e.g.,
    `000054_transcript_20251220_20251221_143022.wav`).

    Args:
        temp_audio_path: Path to temporary WAV file created during recording.
        transcript_path: Path to the transcript MD file.

    Returns:
        Path to archived audio file.
    """
    # #region agent log
    import json

    try:
        with open(
            "/Users/benjamin/Desktop/CODE/rejoice-slim-v2/.cursor/debug.log", "a"
        ) as f:
            f.write(
                json.dumps(
                    {
                        "sessionId": "debug-session",
                        "runId": "run2",
                        "hypothesisId": "A",
                        "location": "archive.py:archive_audio_file",
                        "message": "Function entry",
                        "data": {
                            "temp_audio_path": str(temp_audio_path),
                            "transcript_path": str(transcript_path),
                            "temp_exists": temp_audio_path.exists(),
                        },
                        "timestamp": int(__import__("time").time() * 1000),
                    }
                )
                + "\n"
            )
    except Exception:
        pass
    # #endregion

    # Ensure audio directory exists
    audio_dir = ensure_audio_directory_exists(transcript_path.parent)

    # Generate target filename matching transcript
    audio_filename = transcript_path.stem + ".wav"
    archived_path = audio_dir / audio_filename

    # Handle existing file by appending timestamp
    if archived_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Insert timestamp before .wav extension
        audio_filename_with_timestamp = f"{transcript_path.stem}_{timestamp}.wav"
        archived_path = audio_dir / audio_filename_with_timestamp
        logger.warning(
            f"Audio file already exists at {audio_dir / audio_filename}, "
            f"archiving with timestamp suffix: {audio_filename_with_timestamp}"
        )

    # #region agent log
    try:
        with open(
            "/Users/benjamin/Desktop/CODE/rejoice-slim-v2/.cursor/debug.log", "a"
        ) as f:
            f.write(
                json.dumps(
                    {
                        "sessionId": "debug-session",
                        "runId": "run2",
                        "hypothesisId": "A",
                        "location": "archive.py:archive_audio_file",
                        "message": "Before rename",
                        "data": {
                            "temp_audio_path": str(temp_audio_path),
                            "archived_path": str(archived_path),
                            "temp_exists": temp_audio_path.exists(),
                            "archived_exists": archived_path.exists(),
                        },
                        "timestamp": int(__import__("time").time() * 1000),
                    }
                )
                + "\n"
            )
    except Exception:
        pass
    # #endregion

    # Move temp file to archive location (atomic operation)
    temp_audio_path.rename(archived_path)

    logger.debug(
        f"Archived audio file: {temp_audio_path.name} -> "
        f"{archived_path.relative_to(transcript_path.parent)}"
    )

    # #region agent log
    try:
        with open(
            "/Users/benjamin/Desktop/CODE/rejoice-slim-v2/.cursor/debug.log", "a"
        ) as f:
            f.write(
                json.dumps(
                    {
                        "sessionId": "debug-session",
                        "runId": "run2",
                        "hypothesisId": "A",
                        "location": "archive.py:archive_audio_file",
                        "message": "Function exit",
                        "data": {
                            "archived_path": str(archived_path),
                            "archived_exists": archived_path.exists(),
                        },
                        "timestamp": int(__import__("time").time() * 1000),
                    }
                )
                + "\n"
            )
    except Exception:
        pass
    # #endregion

    return archived_path
