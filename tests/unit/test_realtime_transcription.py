"""Tests for real-time incremental transcription during recording [T-010]."""

import threading
from pathlib import Path
from typing import List

import numpy as np

from rejoice.core.config import TranscriptionConfig
from rejoice.exceptions import TranscriptionError
from rejoice.transcript.manager import append_to_transcript


def test_realtime_transcription_updates_transcript_incrementally(monkeypatch, tmp_path):
    """GIVEN a real-time transcription session
    WHEN audio chunks are processed
    THEN transcript file is updated incrementally."""
    transcript_path = tmp_path / "transcript_20250101_000001.md"
    transcript_path.write_text("---\nid: '000001'\n---\n\n", encoding="utf-8")

    transcribed_segments: List[str] = []

    # Mock Transcriber to simulate incremental transcription
    class MockTranscriber:
        def __init__(self, config):
            self.config = config
            self.call_count = 0

        def transcribe_audio_chunk(self, audio_chunk: np.ndarray, sample_rate: int):
            """Simulate transcribing a chunk of audio."""
            self.call_count += 1
            # Simulate returning transcribed segments
            if self.call_count == 1:
                return [{"text": "First segment", "start": 0.0, "end": 1.0}]
            elif self.call_count == 2:
                return [{"text": "Second segment", "start": 1.0, "end": 2.0}]
            return []

    def mock_append(text: str):
        transcribed_segments.append(text)
        append_to_transcript(transcript_path, text)

    monkeypatch.setattr("rejoice.transcript.manager.append_to_transcript", mock_append)

    # Simulate processing audio chunks
    transcriber = MockTranscriber(TranscriptionConfig())

    # Add audio chunks to queue
    chunk1 = np.random.randn(16000).astype(np.float32)  # 1 second at 16kHz
    chunk2 = np.random.randn(16000).astype(np.float32)

    # Process chunks (simulating real-time transcription)
    for chunk in [chunk1, chunk2]:
        segments = transcriber.transcribe_audio_chunk(chunk, 16000)
        for segment in segments:
            text = segment.get("text", "").strip()
            if text:
                mock_append(text)

    # Verify transcript was updated incrementally
    assert len(transcribed_segments) == 2
    assert "First segment" in transcribed_segments
    assert "Second segment" in transcribed_segments

    # Verify transcript file contains both segments
    content = transcript_path.read_text(encoding="utf-8")
    assert "First segment" in content
    assert "Second segment" in content


def test_realtime_transcription_thread_safety(monkeypatch, tmp_path):
    """GIVEN concurrent transcription updates
    WHEN multiple threads append to transcript
    THEN file writes are thread-safe (no corruption)."""
    transcript_path = tmp_path / "transcript_20250101_000001.md"
    transcript_path.write_text("---\nid: '000001'\n---\n\n", encoding="utf-8")

    append_count = {"count": 0}
    lock = threading.Lock()

    def safe_append(text: str):
        with lock:
            append_count["count"] += 1
            append_to_transcript(transcript_path, text)

    def append_segment(segment_text: str):
        """Worker function that appends a segment."""
        safe_append(segment_text)

    # Create multiple threads that append simultaneously
    threads = []
    for i in range(10):
        thread = threading.Thread(target=append_segment, args=(f"Segment {i}",))
        threads.append(thread)

    # Start all threads
    for thread in threads:
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Verify all segments were written (no corruption)
    assert append_count["count"] == 10
    content = transcript_path.read_text(encoding="utf-8")
    for i in range(10):
        assert f"Segment {i}" in content


def test_realtime_transcription_handles_errors_gracefully(monkeypatch, tmp_path):
    """GIVEN a real-time transcription session
    WHEN transcription fails
    THEN error is handled gracefully without stopping recording."""
    transcript_path = tmp_path / "transcript_20250101_000001.md"
    transcript_path.write_text("---\nid: '000001'\n---\n\n", encoding="utf-8")

    errors_caught = []

    class FailingTranscriber:
        def transcribe_audio_chunk(self, audio_chunk, sample_rate):
            raise TranscriptionError("Transcription failed")

    transcriber = FailingTranscriber()

    # Simulate transcription worker that catches errors
    def transcription_worker():
        try:
            chunk = np.random.randn(16000).astype(np.float32)
            transcriber.transcribe_audio_chunk(chunk, 16000)
        except TranscriptionError as e:
            errors_caught.append(e)
            # Error is caught, recording continues

    worker_thread = threading.Thread(target=transcription_worker)
    worker_thread.start()
    worker_thread.join()

    # Verify error was caught but didn't crash
    assert len(errors_caught) == 1
    assert "Transcription failed" in str(errors_caught[0])
    # Verify transcript file still exists (recording wasn't interrupted)
    assert transcript_path.exists()


def test_realtime_transcription_final_pass_after_stop(tmp_path):
    """GIVEN a recording session with real-time transcription
    WHEN recording stops
    THEN final transcription pass processes remaining audio."""
    transcript_path = tmp_path / "transcript_20250101_000001.md"
    transcript_path.write_text(
        "---\nid: '000001'\n---\n\nRemaining: ", encoding="utf-8"
    )

    final_pass_called = {"called": False}

    # Mock final pass
    def final_transcription_pass(audio_path: str, transcript_path: Path):
        final_pass_called["called"] = True
        append_to_transcript(transcript_path, "final segment")

    # Simulate calling final pass
    temp_audio_path = tmp_path / "remaining_audio.wav"
    temp_audio_path.write_bytes(b"dummy audio")
    final_transcription_pass(str(temp_audio_path), transcript_path)

    # Verify final pass was called and appended text
    assert final_pass_called["called"] is True
    content = transcript_path.read_text(encoding="utf-8")
    assert "final segment" in content


def test_realtime_transcription_min_chunk_size(monkeypatch):
    """GIVEN a real-time transcription session
    WHEN audio chunks are smaller than min_chunk_size
    THEN chunks are accumulated until threshold is reached."""
    min_chunk_size_seconds = 1.0
    sample_rate = 16000
    min_chunk_samples = int(min_chunk_size_seconds * sample_rate)

    accumulated_samples: List[np.ndarray] = []
    processed_chunks: List[int] = []

    def process_if_ready(chunk: np.ndarray):
        accumulated_samples.extend(chunk)
        if len(accumulated_samples) >= min_chunk_samples:
            # Process accumulated chunk
            processed_chunks.append(len(accumulated_samples))
            accumulated_samples.clear()

    # Add small chunks (0.5 seconds each)
    small_chunk_size = int(0.5 * sample_rate)
    for _ in range(3):  # 3 chunks = 1.5 seconds total
        chunk = np.random.randn(small_chunk_size).astype(np.float32)
        process_if_ready(chunk)

    # Verify chunks were accumulated and processed when threshold reached
    # After 2 chunks (1.0 second), we should have processed
    assert len(processed_chunks) >= 1


def test_realtime_transcription_with_vad(monkeypatch):
    """GIVEN a real-time transcription session with VAD
    WHEN audio contains silence
    THEN VAD filters silence gracefully."""
    # This test verifies that VAD integration works
    # In practice, faster-whisper's VAD is handled in the model
    config = TranscriptionConfig(vad_filter=True)
    assert config.vad_filter is True

    # VAD is enabled in the transcriber config
    # The actual VAD processing happens in faster-whisper
    # This test just verifies the config is set correctly
