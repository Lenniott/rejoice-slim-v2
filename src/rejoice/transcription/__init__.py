"""Transcription functionality.

Implements the core of [T-001] faster-whisper Integration.

This module provides a thin wrapper around the ``faster-whisper`` library so the
rest of the codebase does not depend directly on third-party APIs. It handles
model loading, basic configuration, and exposes a ``Transcriber`` class with a
single ``transcribe_file`` method that yields normalised segments.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Iterable, Iterator, Optional, cast

from rejoice.transcript.manager import append_to_transcript, update_language
from rejoice.core.config import TranscriptionConfig
from rejoice.exceptions import TranscriptionError

try:  # pragma: no cover - happy path is exercised via monkeypatched model
    from faster_whisper import WhisperModel as _WhisperModel
except Exception:  # pragma: no cover - exercised only if dependency is missing
    _WhisperModel = None

# Rebind into a public name so tests and other modules can monkeypatch or
# introspect the model constructor without importing faster-whisper directly.
WhisperModel = _WhisperModel

logger = logging.getLogger(__name__)


class Transcriber:
    """High-level transcription facade wrapping faster-whisper.

    Parameters
    ----------
    config:
        The :class:`~rejoice.core.config.TranscriptionConfig` that controls the
        model size, default language and VAD behaviour.
    device:
        Device string passed through to ``WhisperModel`` (for example, ``"cpu"``
        or ``"cuda"``). Defaults to ``"cpu"``.
    compute_type:
        Compute type string for faster-whisper (for example, ``"int8"`` or
        ``"float16"``). Defaults to ``"int8"`` for modest resource usage.
    """

    def __init__(
        self,
        config: TranscriptionConfig,
        *,
        device: str = "cpu",
        compute_type: str = "int8",
    ) -> None:
        if WhisperModel is None:
            # Provide a clear, actionable error instead of a low-level ImportError.
            raise TranscriptionError(
                "faster-whisper dependency is not available. "
                "Install it via 'pip install faster-whisper' to enable "
                "transcription.",
                suggestion=(
                    "Ensure the 'faster-whisper' package is installed in the same "
                    "environment as Rejoice and try again."
                ),
            )

        self._config = config
        # Track the last language used/detected for [T-002] so that callers
        # can persist it into transcript frontmatter if desired.
        self._last_language: Optional[str] = None

        try:
            self._model = WhisperModel(
                config.model,
                device=device,
                compute_type=compute_type,
            )
        except Exception as exc:  # pragma: no cover - exercised via error tests
            message = f"Failed to load transcription model '{config.model}': {exc}"
            logger.error(message, exc_info=True)
            raise TranscriptionError(
                message,
                suggestion=(
                    "Check that the model name is valid and all dependencies are "
                    "installed."
                ),
            ) from exc

    @property
    def last_language(self) -> Optional[str]:
        """Return the last language used or detected during transcription.

        For ``language='auto'`` this reflects the model-reported detected
        language where available; otherwise it mirrors the configured
        ``TranscriptionConfig.language`` value.
        """
        return self._last_language

    def transcribe_file(self, audio_path: str) -> Iterator[Dict[str, object]]:
        """Transcribe an audio file and yield normalised segment dictionaries.

        Each yielded segment has the shape::

            {
                "text": str,
                "start": float,
                "end": float,
            }

        Parameters
        ----------
        audio_path:
            Path to the input audio file. The file must be readable by
            faster-whisper.

        Raises
        ------
        TranscriptionError
            If the underlying model raises any error during transcription.
        """

        # faster-whisper treats ``language=None`` as "auto-detect", which matches
        # our config semantics where ``language='auto'`` means "let the model
        # decide".
        if self._config.language == "auto":
            language_arg: Optional[str] = None
        else:
            language_arg = self._config.language

        try:
            segments, info = self._model.transcribe(
                audio_path,
                vad_filter=self._config.vad_filter,
                language=language_arg,
            )
        except Exception as exc:
            message = f"Transcription failed for '{audio_path}': {exc}"
            logger.error(message, exc_info=True)
            raise TranscriptionError(
                message,
                suggestion=(
                    "Verify that the audio file exists and is a supported format."
                ),
            ) from exc

        # Derive the effective language for this transcription run.
        detected_language: Optional[str]
        if language_arg is not None:
            detected_language = language_arg
        else:
            # For auto-detection, faster-whisper exposes language information
            # via the ``info`` object; support both attribute and mapping styles.
            detected_language = None
            if hasattr(info, "language"):
                detected_language = getattr(info, "language")
            elif isinstance(info, dict) and "language" in info:
                detected_language = cast(Optional[str], info.get("language"))
            elif hasattr(info, "get") and hasattr(info, "__contains__"):
                # Support dict-like objects that aren't actually dicts
                if "language" in info:
                    detected_language = cast(Optional[str], info.get("language"))

        self._last_language = detected_language

        # Normalise the third-party segment objects into simple dictionaries so
        # the rest of the codebase does not depend on faster-whisper's types.
        for seg in _normalise_iterable(segments):
            yield {
                "text": getattr(seg, "text", "").strip(),
                "start": float(getattr(seg, "start", 0.0)),
                "end": float(getattr(seg, "end", 0.0)),
            }

    def stream_file_to_transcript(
        self, audio_path: str, transcript_path: Path
    ) -> Iterator[Dict[str, object]]:
        """Transcribe ``audio_path`` and append segments to ``transcript_path``.

        This method implements the core of [T-003] \"Streaming Transcription to
        File\" by combining :meth:`transcribe_file` with the transcript manager's
        :func:`append_to_transcript` helper.

        Each segment yielded by :meth:`transcribe_file` is:

        - yielded to the caller as a normalised dictionary; and
        - immediately appended to ``transcript_path`` if it contains non-empty
          text.

        The actual file write is performed atomically by
        :func:`append_to_transcript`, preserving the zero data loss guarantee.
        """

        for segment in self.transcribe_file(audio_path):
            # ``transcribe_file`` guarantees that ``text`` is a string value, but
            # we still cast here so static type checkers understand that the
            # value passed into ``append_to_transcript`` is always ``str``.
            text = cast(str, segment.get("text", "") or "")
            if text.strip():
                append_to_transcript(transcript_path, text)
            yield segment

        # After streaming has completed, persist the effective language into the
        # transcript frontmatter for [T-002]. Prefer the detected language when
        # auto-detection was used, otherwise fall back to the configured value.
        effective_language = self._last_language or self._config.language
        if effective_language is not None:
            update_language(transcript_path, effective_language)


def _normalise_iterable(segments: Iterable[object]) -> Iterable[object]:
    """Return an iterable of segment-like objects from the model output."""
    return segments


__all__ = ["Transcriber", "WhisperModel"]
