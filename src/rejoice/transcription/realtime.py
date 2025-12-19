"""Real-time incremental transcription during recording [T-010].

This module provides functionality to transcribe audio incrementally during
recording, updating the transcript file in real-time as speech segments are
confirmed.
"""

from __future__ import annotations

import logging
import tempfile
import threading
import wave
from pathlib import Path
from queue import Empty, Queue
from typing import Optional

import numpy as np

from rejoice.exceptions import TranscriptionError
from rejoice.transcript.manager import append_to_transcript
from rejoice.transcription import Transcriber

logger = logging.getLogger(__name__)


class RealtimeTranscriptionWorker:
    """Background worker that processes audio chunks for real-time transcription.

    This worker runs in a separate thread, consuming audio chunks from a queue
    and transcribing them incrementally. Transcribed segments are appended to
    the transcript file as they are confirmed.

    Parameters
    ----------
    transcriber:
        The Transcriber instance to use for transcription.
    transcript_path:
        Path to the transcript file to append segments to.
    sample_rate:
        Audio sample rate (default: 16000 Hz).
    min_chunk_size_seconds:
        Minimum chunk size in seconds before processing (default: 1.0).
    """

    def __init__(
        self,
        transcriber: Transcriber,
        transcript_path: Path,
        sample_rate: int = 16000,
        min_chunk_size_seconds: float = 1.0,
    ):
        self.transcriber = transcriber
        self.transcript_path = transcript_path
        self.sample_rate = sample_rate
        self.min_chunk_size_seconds = min_chunk_size_seconds
        self.min_chunk_samples = int(min_chunk_size_seconds * sample_rate)

        # Thread-safe queue for audio chunks
        self.audio_queue: Queue[np.ndarray] = Queue()
        self.is_running = threading.Event()
        self.worker_thread: Optional[threading.Thread] = None

        # Accumulated audio buffer
        self.accumulated_audio: list[np.ndarray] = []

        # Lock for thread-safe file operations
        self.file_lock = threading.Lock()

        # Track processed chunks for testing/debugging
        self.processed_chunks_count = 0

    def start(self) -> None:
        """Start the background transcription worker thread."""
        if self.worker_thread is not None and self.worker_thread.is_alive():
            logger.warning("Realtime transcription worker already running")
            return

        self.is_running.set()
        self.worker_thread = threading.Thread(
            target=self._worker_loop, daemon=True, name="RealtimeTranscriptionWorker"
        )
        self.worker_thread.start()
        logger.info("Started real-time transcription worker thread")

    def stop(self, timeout: float = 5.0) -> None:
        """Stop the background transcription worker.

        Parameters
        ----------
        timeout:
            Maximum time to wait for the worker thread to finish (seconds).
        """
        if self.worker_thread is None:
            return

        self.is_running.clear()
        if self.worker_thread.is_alive():
            self.worker_thread.join(timeout=timeout)
            if self.worker_thread.is_alive():
                logger.warning(
                    "Realtime transcription worker thread did not stop within timeout"
                )
            else:
                logger.info("Stopped real-time transcription worker thread")

    def add_audio_chunk(self, audio_chunk: np.ndarray) -> None:
        """Add an audio chunk to the processing queue.

        Parameters
        ----------
        audio_chunk:
            Audio data as a numpy array (float32, mono).
        """
        if self.is_running.is_set():
            self.audio_queue.put(audio_chunk.copy())

    def _worker_loop(self) -> None:
        """Main worker loop that processes audio chunks from the queue."""
        logger.debug("Realtime transcription worker loop started")

        while self.is_running.is_set() or not self.audio_queue.empty():
            try:
                # Get audio chunk from queue (with timeout to allow checking is_running)
                try:
                    chunk = self.audio_queue.get(timeout=0.1)
                except Empty:
                    continue

                # Accumulate chunks until we have enough for processing
                self.accumulated_audio.append(chunk)

                # Check if we have enough accumulated audio
                total_samples = sum(len(c) for c in self.accumulated_audio)
                if total_samples >= self.min_chunk_samples:
                    self._process_accumulated_audio()
            except Exception as exc:
                # Log error but continue processing (don't stop recording)
                logger.error(
                    f"Error in real-time transcription worker: {exc}",
                    exc_info=True,
                )

        # Process any remaining accumulated audio
        if self.accumulated_audio:
            self._process_accumulated_audio()

        logger.debug("Realtime transcription worker loop finished")

    def _process_accumulated_audio(self) -> None:
        """Process accumulated audio chunks by transcribing them."""
        if not self.accumulated_audio:
            return

        try:
            # Concatenate accumulated audio
            audio_array = np.concatenate(self.accumulated_audio)

            # Save to temporary WAV file for faster-whisper
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_path = Path(tmp_file.name)

            # Write audio to WAV file
            with wave.open(str(tmp_path), "wb") as wav_file:
                wav_file.setnchannels(1)  # mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(self.sample_rate)

                # Convert float32 to int16 PCM
                audio_int16 = (audio_array * 32767).astype(np.int16)
                wav_file.writeframes(audio_int16.tobytes())

            # Transcribe the chunk
            try:
                for segment in self.transcriber.transcribe_file(str(tmp_path)):
                    text = str(segment.get("text", "") or "").strip()
                    if text:
                        # Thread-safe append to transcript
                        with self.file_lock:
                            append_to_transcript(self.transcript_path, text)
                        self.processed_chunks_count += 1
                        logger.debug(
                            f"Appended real-time transcription segment: {text[:50]}"
                        )

            finally:
                # Clean up temp file
                try:
                    tmp_path.unlink(missing_ok=True)
                except Exception:  # pragma: no cover
                    pass

            # Clear accumulated audio after processing
            self.accumulated_audio.clear()

        except TranscriptionError as exc:
            # Log transcription errors but don't stop recording
            logger.warning(f"Transcription error in real-time worker: {exc}")
        except Exception as exc:
            # Log other errors but continue
            logger.error(
                f"Unexpected error processing accumulated audio: {exc}", exc_info=True
            )

    def finalize(self, remaining_audio_path: Optional[Path] = None) -> None:
        """Finalize transcription by processing any remaining audio.

        This should be called after recording stops to ensure all audio
        is transcribed, including any partial chunks.

        Parameters
        ----------
        remaining_audio_path:
            Optional path to audio file containing remaining audio to transcribe.
        """
        # Process any accumulated audio that didn't reach min_chunk_size
        if self.accumulated_audio:
            self._process_accumulated_audio()

        # Process remaining audio file if provided
        if remaining_audio_path and remaining_audio_path.exists():
            try:
                for segment in self.transcriber.transcribe_file(
                    str(remaining_audio_path)
                ):
                    text = str(segment.get("text", "") or "").strip()
                    if text:
                        with self.file_lock:
                            append_to_transcript(self.transcript_path, text)
                logger.info("Final transcription pass completed")
            except TranscriptionError as exc:
                logger.warning(f"Error in final transcription pass: {exc}")
            except Exception as exc:
                logger.error(f"Unexpected error in final pass: {exc}", exc_info=True)
