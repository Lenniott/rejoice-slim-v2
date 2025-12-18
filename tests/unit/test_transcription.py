"""Tests for transcription system ([T-001] faster-whisper Integration)."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import pytest

from rejoice.core.config import TranscriptionConfig
from rejoice.exceptions import TranscriptionError
import rejoice.transcription as transcription


class DummySegment:
    """Simple stand-in for faster-whisper segment objects."""

    def __init__(self, text: str, start: float, end: float) -> None:
        self.text = text
        self.start = start
        self.end = end


def test_transcriber_initialises_model_with_config(monkeypatch):
    """GIVEN a transcription config
    WHEN Transcriber is constructed
    THEN WhisperModel is initialised with the configured model name.
    """

    created: Dict[str, object] = {}

    class DummyModel:
        def __init__(
            self, model_size: str, device: str = "cpu", compute_type: str = "int8"
        ):
            created["model_size"] = model_size
            created["device"] = device
            created["compute_type"] = compute_type

        def transcribe(self, *args, **kwargs):  # pragma: no cover - not used here
            return [], {}

    monkeypatch.setattr(transcription, "WhisperModel", DummyModel)

    cfg = TranscriptionConfig(model="small", language="en", vad_filter=True)

    # Construct for side-effects; no need to keep a reference.
    transcription.Transcriber(cfg)

    assert created["model_size"] == "small"
    assert created["device"] == "cpu"
    assert created["compute_type"] == "int8"


def test_transcribe_file_yields_normalised_segments_and_uses_vad_and_language(
    monkeypatch, tmp_path: Path
):
    """GIVEN an audio file path and config
    WHEN transcribe_file is called
    THEN segments are yielded as dictionaries with text/start/end
    AND faster-whisper is called with VAD and language from config.
    """

    calls: Dict[str, object] = {}

    class DummyModel:
        def __init__(self, *args, **kwargs):
            pass

        def transcribe(self, audio_path: str, vad_filter: bool, language=None):
            calls["audio_path"] = audio_path
            calls["vad_filter"] = vad_filter
            calls["language"] = language
            segments = [DummySegment("hello world", 0.0, 1.23)]
            info = {"duration": 1.23}
            return segments, info

    monkeypatch.setattr(transcription, "WhisperModel", DummyModel)

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
    THEN language=None is passed through to faster-whisper."""

    observed = {}

    class DummyModel:
        def __init__(self, *args, **kwargs):
            pass

        def transcribe(self, audio_path: str, vad_filter: bool, language=None):
            observed["language"] = language
            return [DummySegment("hi", 0.0, 0.5)], {}

    monkeypatch.setattr(transcription, "WhisperModel", DummyModel)

    cfg = TranscriptionConfig(model="tiny", language="auto", vad_filter=True)
    transcriber = transcription.Transcriber(cfg)

    list(transcriber.transcribe_file(str(tmp_path / "audio.wav")))

    assert "language" in observed
    assert observed["language"] is None


def test_transcriber_raises_helpful_error_when_faster_whisper_missing(monkeypatch):
    """GIVEN faster-whisper cannot be imported
    WHEN Transcriber is constructed
    THEN a TranscriptionError with a helpful suggestion is raised.
    """

    monkeypatch.setattr(transcription, "WhisperModel", None)

    cfg = TranscriptionConfig(model="small", language="en", vad_filter=True)

    with pytest.raises(TranscriptionError) as excinfo:
        transcription.Transcriber(cfg)

    message = str(excinfo.value).lower()
    assert "faster-whisper" in message
    assert "install" in message or "dependency" in message


def test_transcribe_file_wraps_lower_level_errors(monkeypatch, tmp_path: Path):
    """GIVEN faster-whisper raises during transcription
    WHEN transcribe_file is called
    THEN a TranscriptionError is raised with the original error message included.
    """

    class Boom(Exception):
        pass

    class DummyModel:
        def __init__(self, *args, **kwargs):
            pass

        def transcribe(self, *args, **kwargs):
            raise Boom("boom")

    monkeypatch.setattr(transcription, "WhisperModel", DummyModel)

    cfg = TranscriptionConfig(model="tiny", language="en", vad_filter=True)
    transcriber = transcription.Transcriber(cfg)

    audio_path = str(tmp_path / "audio.wav")

    with pytest.raises(TranscriptionError) as excinfo:
        list(transcriber.transcribe_file(audio_path))

    message = str(excinfo.value).lower()
    assert "transcription failed" in message
    assert "boom" in message
