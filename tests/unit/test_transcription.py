"""Tests for transcription system ([T-001] faster-whisper Integration)."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import pytest

from rejoice.core.config import TranscriptionConfig
from rejoice.exceptions import TranscriptionError
import rejoice.transcription as transcription
from rejoice.transcript import manager as transcript_manager


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
            self,
            model_size: str,
            device: str = "cpu",
            compute_type: str = "int8",
            local_files_only: bool = False,
        ):
            created["model_size"] = model_size
            created["device"] = device
            created["compute_type"] = compute_type
            created["local_files_only"] = local_files_only

        def transcribe(self, *args, **kwargs):  # pragma: no cover - not used here
            return [], {}

    monkeypatch.setattr(transcription, "WhisperModel", DummyModel)

    cfg = TranscriptionConfig(model="small", language="en", vad_filter=True)

    # Construct for side-effects; no need to keep a reference.
    transcription.Transcriber(cfg)

    assert created["model_size"] == "small"
    assert created["device"] == "cpu"
    assert created["compute_type"] == "int8"
    assert created["local_files_only"] is True  # Enforced for local-only operation


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


def test_transcriber_tracks_detected_language_when_auto(monkeypatch, tmp_path: Path):
    """GIVEN language='auto' in config and model reports a detected language
    WHEN transcribe_file is called
    THEN the transcriber exposes the detected language via a property.
    """

    class DummyModel:
        def __init__(self, *args, **kwargs):
            pass

        def transcribe(self, audio_path: str, vad_filter: bool, language=None):
            # Simulate faster-whisper returning an info object with language
            class Info:
                language = "es"

            segments = [DummySegment("hola mundo", 0.0, 1.0)]
            return segments, Info()

    monkeypatch.setattr(transcription, "WhisperModel", DummyModel)

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
        def __init__(self, *args, **kwargs):
            pass

        def transcribe(self, audio_path: str, vad_filter: bool, language=None):
            class Info:
                language = "fr"

            segments = [DummySegment("bonjour", 0.0, 1.0)]
            return segments, Info()

    monkeypatch.setattr(transcription, "WhisperModel", DummyModel)

    cfg = TranscriptionConfig(model="tiny", language="en", vad_filter=True)
    transcriber = transcription.Transcriber(cfg)

    list(transcriber.transcribe_file(str(tmp_path / "audio.wav")))

    assert transcriber.last_language == "en"


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


def test_stream_file_to_transcript_appends_each_segment_in_order(
    monkeypatch, tmp_path: Path
):
    """GIVEN an audio file and transcript path
    WHEN stream_file_to_transcript is called
    THEN each non-empty segment is appended to the transcript in order.
    """

    calls: List[Dict[str, object]] = []

    class DummyModel:
        def __init__(self, *args, **kwargs):
            pass

        def transcribe(self, audio_path: str, vad_filter: bool, language=None):
            # Two real segments and one empty/whitespace-only segment that
            # should be ignored for appends.
            segments = [
                DummySegment("first segment", 0.0, 1.0),
                DummySegment("   ", 1.0, 2.0),
                DummySegment("second segment", 2.0, 3.0),
            ]
            info = {"duration": 3.0}
            return segments, info

    monkeypatch.setattr(transcription, "WhisperModel", DummyModel)

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
        def __init__(self, *args, **kwargs):
            pass

        def transcribe(self, audio_path: str, vad_filter: bool, language=None):
            class Info:
                language = "es"

            segments = [DummySegment("hola mundo", 0.0, 1.0)]
            return segments, Info()

    monkeypatch.setattr(transcription, "WhisperModel", DummyModel)

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
    WHEN info is a dict with language key
    THEN language is extracted correctly (line 158)"""

    class DummySegment:
        def __init__(self, text: str, start: float, end: float):
            self.text = text
            self.start = start
            self.end = end

    class Info:
        def __init__(self):
            # Use dict-style access
            self._data = {"language": "fr"}

        def get(self, key, default=None):
            return self._data.get(key, default)

        def __contains__(self, key):
            return key in self._data

    class DummyModel:
        def __init__(self, *args, **kwargs):
            pass

        def transcribe(self, *args, **kwargs):
            segments = [DummySegment("Bonjour", 0.0, 1.0)]
            info = Info()
            return segments, info

    monkeypatch.setattr(transcription, "WhisperModel", DummyModel)

    cfg = TranscriptionConfig(model="tiny", language="auto", vad_filter=True)
    transcriber = transcription.Transcriber(cfg)

    # Test that dict-style info access works
    audio_path = str(tmp_path / "test.wav")
    # Create a dummy audio file
    (tmp_path / "test.wav").write_bytes(b"dummy")

    segments = list(transcriber.transcribe_file(audio_path))
    assert len(segments) > 0
    # Language should be detected from dict-style info
    assert transcriber.last_language == "fr"
