"""Tests for custom exceptions."""
from rejoice.exceptions import (
    RejoiceError,
    AudioError,
    TranscriptionError,
    ConfigError,
    TranscriptError,
    AIError,
)


def test_rejoice_error_basic():
    """
    Test RejoiceError basic functionality.

    GIVEN RejoiceError
    WHEN created with message
    THEN error message is set correctly
    """
    error = RejoiceError("Test error message")
    assert str(error) == "Test error message"
    assert error.message == "Test error message"
    assert error.suggestion is None


def test_rejoice_error_with_suggestion():
    """
    Test RejoiceError with suggestion.

    GIVEN RejoiceError
    WHEN created with message and suggestion
    THEN both are set correctly
    """
    error = RejoiceError("Test error", "Try this fix")
    assert error.message == "Test error"
    assert error.suggestion == "Try this fix"


def test_audio_error():
    """
    Test AudioError inheritance.

    GIVEN AudioError
    WHEN created
    THEN it is a RejoiceError
    """
    error = AudioError("Audio problem")
    assert isinstance(error, RejoiceError)
    assert error.message == "Audio problem"


def test_transcription_error():
    """
    Test TranscriptionError inheritance.

    GIVEN TranscriptionError
    WHEN created
    THEN it is a RejoiceError
    """
    error = TranscriptionError("Transcription problem")
    assert isinstance(error, RejoiceError)
    assert error.message == "Transcription problem"


def test_config_error():
    """
    Test ConfigError inheritance.

    GIVEN ConfigError
    WHEN created
    THEN it is a RejoiceError
    """
    error = ConfigError("Config problem")
    assert isinstance(error, RejoiceError)
    assert error.message == "Config problem"


def test_transcript_error():
    """
    Test TranscriptError inheritance.

    GIVEN TranscriptError
    WHEN created
    THEN it is a RejoiceError
    """
    error = TranscriptError("Transcript problem")
    assert isinstance(error, RejoiceError)
    assert error.message == "Transcript problem"


def test_ai_error():
    """
    Test AIError inheritance.

    GIVEN AIError
    WHEN created
    THEN it is a RejoiceError
    """
    error = AIError("AI problem")
    assert isinstance(error, RejoiceError)
    assert error.message == "AI problem"
