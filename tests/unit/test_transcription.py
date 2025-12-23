"""Tests for transcription system ([T-011] WhisperX Integration)."""

from __future__ import annotations

from pathlib import Path
from types import ModuleType
from typing import Dict, List

import pytest

from rejoice.core.config import TranscriptionConfig
from rejoice.exceptions import TranscriptionError
import rejoice.transcription as transcription
from rejoice.transcript import manager as transcript_manager


# WhisperX returns segments as dicts, not objects


def create_mock_whisperx_module(monkeypatch):
    """Create a mock whisperx module for testing."""
    mock_whisperx = ModuleType("whisperx")
    monkeypatch.setattr(transcription, "whisperx", mock_whisperx)
    return mock_whisperx


def test_transcriber_initialises_model_with_config(monkeypatch):
    """GIVEN a transcription config
    WHEN Transcriber is constructed
    THEN WhisperX model is loaded with the configured model name.
    """

    created: Dict[str, object] = {}
    mock_whisperx = create_mock_whisperx_module(monkeypatch)

    def mock_load_model(
        model: str,
        device: str = "cpu",
        compute_type: str = "int8",
        vad_method: str = "silero",
    ):
        created["model"] = model
        created["device"] = device
        created["compute_type"] = compute_type
        created["vad_method"] = vad_method

        class DummyModel:
            def transcribe(self, *args, **kwargs):  # pragma: no cover - not used here
                return {"segments": [], "language": None}

        return DummyModel()

    mock_whisperx.load_model = mock_load_model
    mock_whisperx.load_audio = lambda path: b"dummy_audio"

    cfg = TranscriptionConfig(model="small", language="en", vad_filter=True)

    # Construct for side-effects; no need to keep a reference.
    transcription.Transcriber(cfg)

    assert created["model"] == "small"
    assert created["device"] == "cpu"
    assert created["compute_type"] == "int8"
    assert created["vad_method"] == "silero"


def test_transcribe_file_yields_normalised_segments_and_uses_vad_and_language(
    monkeypatch, tmp_path: Path
):
    """GIVEN an audio file path and config
    WHEN transcribe_file is called
    THEN segments are yielded as dictionaries with text/start/end
    AND WhisperX is called with VAD and language from config.
    """

    calls: Dict[str, object] = {}

    class DummyModel:
        def transcribe(self, audio, language=None, vad_filter=True):
            calls["vad_filter"] = vad_filter
            calls["language"] = language
            return {
                "segments": [{"text": "hello world", "start": 0.0, "end": 1.23}],
                "language": "en",
            }

    def mock_load_model(*args, **kwargs):
        return DummyModel()

    def mock_load_audio(audio_path: str):
        calls["audio_path"] = audio_path
        return b"dummy_audio"

    mock_whisperx = create_mock_whisperx_module(monkeypatch)
    mock_whisperx.load_model = mock_load_model
    mock_whisperx.load_audio = mock_load_audio

    cfg = TranscriptionConfig(model="tiny", language="en", vad_filter=True)
    transcriber = transcription.Transcriber(cfg)

    audio_path = str(tmp_path / "audio.wav")
    results = list(transcriber.transcribe_file(audio_path))

    assert calls["audio_path"] == audio_path
    assert calls["vad_filter"] is True
    assert calls["language"] == "en"

    assert len(results) == 1
    segment = results[0]
    assert segment["text"] == "hello world"
    assert pytest.approx(segment["start"], rel=1e-6) == 0.0
    assert pytest.approx(segment["end"], rel=1e-6) == 1.23


def test_transcribe_file_passes_none_language_when_auto(monkeypatch, tmp_path: Path):
    """GIVEN language='auto' in config
    WHEN transcribe_file is called
    THEN language=None is passed through to WhisperX."""

    observed = {}

    class DummyModel:
        def transcribe(self, audio, language=None, vad_filter=True):
            observed["language"] = language
            return {
                "segments": [{"text": "hi", "start": 0.0, "end": 0.5}],
                "language": None,
            }

    def mock_load_model(*args, **kwargs):
        return DummyModel()

    mock_whisperx = create_mock_whisperx_module(monkeypatch)
    mock_whisperx.load_model = mock_load_model
    mock_whisperx.load_audio = lambda path: b"dummy_audio"

    cfg = TranscriptionConfig(model="tiny", language="auto", vad_filter=True)
    transcriber = transcription.Transcriber(cfg)

    list(transcriber.transcribe_file(str(tmp_path / "audio.wav")))

    assert "language" in observed
    assert observed["language"] is None


def test_transcriber_tracks_detected_language_when_auto(monkeypatch, tmp_path: Path):
    """GIVEN language='auto' in config and model reports a detected language
    WHEN transcribe_file is called
    THEN the transcriber exposes the detected language via a property.
    """

    class DummyModel:
        def transcribe(self, audio, language=None, vad_filter=True):
            # WhisperX returns language in the result dict
            return {
                "segments": [{"text": "hola mundo", "start": 0.0, "end": 1.0}],
                "language": "es",
            }

    def mock_load_model(*args, **kwargs):
        return DummyModel()

    mock_whisperx = create_mock_whisperx_module(monkeypatch)
    mock_whisperx.load_model = mock_load_model
    mock_whisperx.load_audio = lambda path: b"dummy_audio"

    cfg = TranscriptionConfig(model="tiny", language="auto", vad_filter=True)
    transcriber = transcription.Transcriber(cfg)

    list(transcriber.transcribe_file(str(tmp_path / "audio.wav")))

    assert transcriber.last_language == "es"


def test_transcriber_last_language_matches_forced_language(monkeypatch, tmp_path: Path):
    """GIVEN a fixed language in config
    WHEN transcribe_file is called
    THEN last_language matches the configured language regardless of model info.
    """

    class DummyModel:
        def transcribe(self, audio, language=None, vad_filter=True):
            # Even if model detects different language, we use configured one
            return {
                "segments": [{"text": "bonjour", "start": 0.0, "end": 1.0}],
                "language": "fr",  # Model detects French, but config says English
            }

    def mock_load_model(*args, **kwargs):
        return DummyModel()

    mock_whisperx = create_mock_whisperx_module(monkeypatch)
    mock_whisperx.load_model = mock_load_model
    mock_whisperx.load_audio = lambda path: b"dummy_audio"

    cfg = TranscriptionConfig(model="tiny", language="en", vad_filter=True)
    transcriber = transcription.Transcriber(cfg)

    list(transcriber.transcribe_file(str(tmp_path / "audio.wav")))

    assert transcriber.last_language == "en"


def test_transcriber_raises_helpful_error_when_whisperx_missing(monkeypatch):
    """GIVEN WhisperX cannot be imported
    WHEN Transcriber is constructed
    THEN a TranscriptionError with a helpful suggestion is raised.
    """

    # Set whisperx to None to test error handling
    monkeypatch.setattr(transcription, "whisperx", None)

    cfg = TranscriptionConfig(model="small", language="en", vad_filter=True)

    with pytest.raises(TranscriptionError) as excinfo:
        transcription.Transcriber(cfg)

    message = str(excinfo.value).lower()
    assert "whisperx" in message
    assert "install" in message or "dependency" in message


def test_transcribe_file_wraps_lower_level_errors(monkeypatch, tmp_path: Path):
    """GIVEN WhisperX raises during transcription
    WHEN transcribe_file is called
    THEN a TranscriptionError is raised with the original error message included.
    """

    class Boom(Exception):
        pass

    class DummyModel:
        def transcribe(self, *args, **kwargs):
            raise Boom("boom")

    def mock_load_model(*args, **kwargs):
        return DummyModel()

    mock_whisperx = create_mock_whisperx_module(monkeypatch)
    mock_whisperx.load_model = mock_load_model
    mock_whisperx.load_audio = lambda path: b"dummy_audio"

    cfg = TranscriptionConfig(model="tiny", language="en", vad_filter=True)
    transcriber = transcription.Transcriber(cfg)

    audio_path = str(tmp_path / "audio.wav")

    with pytest.raises(TranscriptionError) as excinfo:
        list(transcriber.transcribe_file(audio_path))

    message = str(excinfo.value).lower()
    assert "transcription failed" in message
    assert "boom" in message


def test_stream_file_to_transcript_appends_each_segment_in_order(
    monkeypatch, tmp_path: Path
):
    """GIVEN an audio file and transcript path
    WHEN stream_file_to_transcript is called
    THEN each non-empty segment is appended to the transcript in order.
    """

    calls: List[Dict[str, object]] = []

    class DummyModel:
        def transcribe(self, audio, language=None, vad_filter=True):
            # Two real segments and one empty/whitespace-only segment that
            # should be ignored for appends.
            return {
                "segments": [
                    {"text": "first segment", "start": 0.0, "end": 1.0},
                    {"text": "   ", "start": 1.0, "end": 2.0},
                    {"text": "second segment", "start": 2.0, "end": 3.0},
                ],
                "language": "en",
            }

    def mock_load_model(*args, **kwargs):
        return DummyModel()

    mock_whisperx = create_mock_whisperx_module(monkeypatch)
    mock_whisperx.load_model = mock_load_model
    mock_whisperx.load_audio = lambda path: b"dummy_audio"

    def fake_append(transcript_path: Path, text: str) -> None:
        calls.append({"path": transcript_path, "text": text})

    monkeypatch.setattr(transcription, "append_to_transcript", fake_append)

    cfg = TranscriptionConfig(model="tiny", language="en", vad_filter=True)
    transcriber = transcription.Transcriber(cfg)

    audio_path = str(tmp_path / "audio.wav")
    transcript_path, _tid = transcript_manager.create_transcript(tmp_path)

    # Consume the streaming generator to trigger appends.
    segments = list(transcriber.stream_file_to_transcript(audio_path, transcript_path))

    # We should have yielded all three segments, including the blank one.
    assert len(segments) == 3
    assert segments[0]["text"] == "first segment"
    assert segments[1]["text"] == ""
    assert segments[2]["text"] == "second segment"

    # Only the non-empty segments should have resulted in append operations.
    assert len(calls) == 2
    assert calls[0]["path"] is transcript_path
    assert calls[0]["text"] == "first segment"
    assert calls[1]["path"] is transcript_path
    assert calls[1]["text"] == "second segment"


def test_stream_file_to_transcript_updates_language_in_frontmatter(
    monkeypatch, tmp_path: Path
):
    """GIVEN language='auto' and a model that reports a detected language
    WHEN stream_file_to_transcript completes
    THEN the transcript frontmatter language field is updated accordingly.
    """

    class DummyModel:
        def transcribe(self, audio, language=None, vad_filter=True):
            return {
                "segments": [{"text": "hola mundo", "start": 0.0, "end": 1.0}],
                "language": "es",
            }

    def mock_load_model(*args, **kwargs):
        return DummyModel()

    mock_whisperx = create_mock_whisperx_module(monkeypatch)
    mock_whisperx.load_model = mock_load_model
    mock_whisperx.load_audio = lambda path: b"dummy_audio"

    cfg = TranscriptionConfig(model="tiny", language="auto", vad_filter=True)
    transcriber = transcription.Transcriber(cfg)

    # Create a real transcript file so that frontmatter helpers operate normally.
    save_dir = tmp_path
    transcript_path, _tid = transcript_manager.create_transcript(save_dir)

    audio_path = str(tmp_path / "audio.wav")

    # Consume the generator to completion to trigger the post-processing hook.
    list(transcriber.stream_file_to_transcript(audio_path, transcript_path))

    content = transcript_path.read_text(encoding="utf-8")
    assert "language: es" in content


def test_transcriber_handles_dict_style_info(monkeypatch, tmp_path):
    """GIVEN transcribe_file
    WHEN WhisperX returns a result dict with language key
    THEN language is extracted correctly."""

    class DummyModel:
        def transcribe(self, audio, language=None, vad_filter=True):
            # WhisperX returns language in result dict
            return {
                "segments": [{"text": "Bonjour", "start": 0.0, "end": 1.0}],
                "language": "fr",
            }

    def mock_load_model(*args, **kwargs):
        return DummyModel()

    mock_whisperx = create_mock_whisperx_module(monkeypatch)
    mock_whisperx.load_model = mock_load_model
    mock_whisperx.load_audio = lambda path: b"dummy_audio"

    cfg = TranscriptionConfig(model="tiny", language="auto", vad_filter=True)
    transcriber = transcription.Transcriber(cfg)

    # Test that dict-style result access works
    audio_path = str(tmp_path / "test.wav")
    # Create a dummy audio file
    (tmp_path / "test.wav").write_bytes(b"dummy")

    segments = list(transcriber.transcribe_file(audio_path))
    assert len(segments) > 0
    # Language should be detected from result dict
    assert transcriber.last_language == "fr"


def test_whisperx_segment_format_compatibility(monkeypatch, tmp_path: Path):
    """GIVEN WhisperX transcription
    WHEN segments are returned
    THEN all segments have required keys (text, start, end) in correct format."""

    class DummyModel:
        def transcribe(self, audio, language=None, vad_filter=True):
            return {
                "segments": [
                    {"text": "first", "start": 0.0, "end": 1.0},
                    {"text": "second", "start": 1.5, "end": 2.5},
                    {"text": "third", "start": 3.0, "end": 4.0},
                ],
                "language": "en",
            }

    def mock_load_model(*args, **kwargs):
        return DummyModel()

    mock_whisperx = create_mock_whisperx_module(monkeypatch)
    mock_whisperx.load_model = mock_load_model
    mock_whisperx.load_audio = lambda path: b"dummy_audio"

    cfg = TranscriptionConfig(model="tiny", language="en", vad_filter=True)
    transcriber = transcription.Transcriber(cfg)

    audio_path = str(tmp_path / "audio.wav")
    segments = list(transcriber.transcribe_file(audio_path))

    assert len(segments) == 3
    for segment in segments:
        assert "text" in segment
        assert "start" in segment
        assert "end" in segment
        assert isinstance(segment["text"], str)
        assert isinstance(segment["start"], float)
        assert isinstance(segment["end"], float)
        assert segment["start"] < segment["end"]


def test_whisperx_model_caching(monkeypatch):
    """GIVEN multiple Transcriber instances
    WHEN created with same config
    THEN WhisperX load_model is called for each (model caching handled by WhisperX)."""

    call_count = 0

    def mock_load_model(
        model: str,
        device: str = "cpu",
        compute_type: str = "int8",
        vad_method: str = "silero",
    ):
        nonlocal call_count
        call_count += 1

        class DummyModel:
            def transcribe(self, *args, **kwargs):
                return {"segments": [], "language": None}

        return DummyModel()

    mock_whisperx = create_mock_whisperx_module(monkeypatch)
    mock_whisperx.load_model = mock_load_model
    mock_whisperx.load_audio = lambda path: b"dummy_audio"

    cfg = TranscriptionConfig(model="small", language="en", vad_filter=True)

    # Create multiple instances
    _ = transcription.Transcriber(cfg)
    _ = transcription.Transcriber(cfg)
    _ = transcription.Transcriber(cfg)

    # Each instance should trigger load_model
    # (caching is handled by WhisperX internally)
    assert call_count == 3
