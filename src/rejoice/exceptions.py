"""Custom exceptions for Rejoice."""
from typing import Optional


class RejoiceError(Exception):
    """Base exception for Rejoice errors."""

    def __init__(self, message: str, suggestion: Optional[str] = None):
        """Initialize Rejoice error.

        Args:
            message: Error message
            suggestion: Optional suggestion for fixing the error
        """
        self.message = message
        self.suggestion = suggestion
        super().__init__(self.message)


class AudioError(RejoiceError):
    """Audio-related errors."""

    pass


class TranscriptionError(RejoiceError):
    """Transcription-related errors."""

    pass


class ConfigError(RejoiceError):
    """Configuration-related errors."""

    pass


class TranscriptError(RejoiceError):
    """Transcript file-related errors."""

    pass


class AIError(RejoiceError):
    """AI enhancement-related errors."""

    pass
