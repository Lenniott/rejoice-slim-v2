"""CLI commands for Rejoice."""

from __future__ import annotations

import sys
import tempfile
import threading
import time
import wave
from pathlib import Path
from typing import Optional

import click
import numpy as np
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table

from rejoice import __version__
from rejoice.audio import record_audio
from rejoice.cli.config_commands import config_group
from rejoice.core.config import load_config
from rejoice.core.logging import setup_logging
from rejoice.exceptions import TranscriptError
from rejoice.transcription import Transcriber
from rejoice.transcript.manager import (
    TRANSCRIPT_FILENAME_PATTERN,
    append_to_transcript,
    create_transcript,
    normalize_id,
    update_language,
    update_status,
)

console = Console()


def _default_wait_for_stop() -> None:
    """Block until the user indicates recording should stop.

    Currently implemented as a simple keypress prompt; later stories
    ([R-007], [R-008]) build on this for richer control.

    Note: This function is not used when Live display is active.
    Input is handled in a separate thread in start_recording_session().
    """
    # Simple input() - when Live uses alternate screen (screen=True),
    # input() works correctly because it reads from the original terminal
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        raise


def _calculate_audio_level(audio_chunk: np.ndarray) -> float:
    """Calculate RMS audio level for visual meter.

    Returns a normalized value between 0.0 and 1.0 representing audio level.
    """
    if len(audio_chunk) == 0:
        return 0.0
    # Calculate RMS (Root Mean Square) for audio level
    rms = float(np.sqrt(np.mean(audio_chunk**2)))
    # Normalize to 0-1 range (assuming input is typically -1.0 to 1.0)
    # Clamp to prevent values > 1.0 from causing display issues
    # Scale: 0.5 RMS = full bar (so rms/0.5 gives 0-2 range, min caps at 1.0)
    return min(1.0, rms / 0.25)


def start_recording_session(
    *,
    wait_for_stop=_default_wait_for_stop,
    language_override: Optional[str] = None,
):
    """Start a recording session implementing [R-012] Simplified Recording.

    Provides visual feedback during recording with Rich Live display.

    Steps:
    - Load configuration
    - Immediately create a transcript file (zero data loss)
    - Create temporary WAV file for audio capture
    - Start audio capture with visual feedback (Rich Live display)
    - Show recording indicator, elapsed time, and audio level meter
    - Block until ``wait_for_stop`` returns
    - Stop recording immediately
    - Run single transcription pass with progress bar
    - Write final transcript atomically
    - Clean up temporary audio file

    Args:
        wait_for_stop: Function to call to wait for recording stop signal.
        language_override: Optional language code to override config (e.g., "en", "es").

    Returns:
        tuple[Path, str]: The transcript filepath and ID.
    """
    config = load_config()

    # Override language if provided via CLI flag
    if language_override:
        config.transcription.language = language_override

    # 1. Create transcript file immediately (zero data loss principle)
    save_dir = Path(config.output.save_path).expanduser()
    filepath, transcript_id = create_transcript(save_dir)

    # 2. Create temporary audio file for recording
    temp_audio_file = tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False,
        dir=str(save_dir),
    )
    temp_audio_path = Path(temp_audio_file.name)
    temp_audio_file.close()

    # Open WAV file for writing
    wav_file = wave.open(str(temp_audio_path), "wb")
    wav_file.setnchannels(1)  # mono
    wav_file.setsampwidth(2)  # 16-bit
    wav_file.setframerate(config.audio.sample_rate)  # 16kHz

    # Shared state for display thread
    recording_active = threading.Event()
    recording_active.set()
    start_time = time.time()
    audio_level_state = {"value": 0.0}
    audio_level_lock = threading.Lock()

    def _audio_callback(indata, frames, timing, status):  # pragma: no cover
        # Write audio buffer to WAV file
        # Convert float32 to int16 PCM
        audio_int16 = (indata * 32767).astype(np.int16)
        wav_file.writeframes(audio_int16.tobytes())

        # Calculate audio level for meter
        level = _calculate_audio_level(indata.flatten())
        with audio_level_lock:
            audio_level_state["value"] = level

    stream = record_audio(
        _audio_callback,
        device=config.audio.device if config.audio.device != "default" else None,
        samplerate=config.audio.sample_rate,
        channels=1,
    )

    cancelled = False

    # Display with Live - use screen=True for alternate screen
    # (prevents duplicate panels)
    # Input handling in separate thread that reads from original terminal
    enter_pressed = threading.Event()

    def _wait_for_enter_input():
        """Wait for Enter in separate thread - reads from original terminal."""
        try:
            # When Live uses screen=True, it uses alternate screen buffer
            # input() reads from the original terminal, so it works correctly
            input()
            enter_pressed.set()
        except (EOFError, KeyboardInterrupt):
            enter_pressed.set()
            raise

    # Start input thread
    input_thread = threading.Thread(target=_wait_for_enter_input, daemon=True)
    input_thread.start()

    # Suppress console logging handler before starting display thread
    # This prevents debug logs from interfering with Rich Live's alternate screen
    import logging

    root_logger = logging.getLogger()
    console_handler = None
    for handler in root_logger.handlers:
        # Find the RichHandler (console handler)
        if hasattr(handler, "rich_tracebacks"):
            console_handler = handler
            # Temporarily remove the handler to prevent debug logs from interfering
            root_logger.removeHandler(handler)
            break

    # Display thread for Rich Live panel
    def _display_recording_status():
        """Display live recording status with elapsed time and audio level."""
        try:
            sys.stdout.write("\033[2J\033[H")
            with Live(
                console=console, auto_refresh=True, screen=False, transient=False
            ) as live:
                while recording_active.is_set() and not enter_pressed.is_set():
                    elapsed = time.time() - start_time
                    minutes, seconds = divmod(int(elapsed), 60)

                    with audio_level_lock:
                        current_level = audio_level_state["value"]

                    # Create audio level bars (0-20 bars)
                    num_bars = int(current_level * 20)
                    level_bars = "█" * num_bars + "░" * (20 - num_bars)

                    panel_content = (
                        f"🔴 Recording...\n"
                        f"⏱️  {minutes:02d}:{seconds:02d}\n"
                        f"🎤 [{level_bars}]\n\n"
                        f"Press Enter to stop recording."
                    )

                    panel = Panel(
                        panel_content,
                        title="Rejoice",
                        border_style="red",
                    )
                    live.update(panel)
                    time.sleep(0.05)  # Update 10 times per second for smooth display
        finally:
            # Restore console handler after Live display exits
            if console_handler:
                root_logger.addHandler(console_handler)

    display_thread = threading.Thread(target=_display_recording_status, daemon=True)
    display_thread.start()

    try:
        # 3. Wait for stop signal (Enter key detected in input thread)
        try:
            # Wait for enter_pressed event (set by input thread)
            while not enter_pressed.is_set() and recording_active.is_set():
                time.sleep(0.1)
        except KeyboardInterrupt:
            # Handle Ctrl+C as a cancel signal for [R-008].
            cancelled = True
            console.print(
                "\n[bold red]Recording interrupt received (Ctrl+C).[/bold red]"
            )

            # First confirm whether the user really wants to cancel.
            if not Confirm.ask(
                "Cancel recording? This will stop without finalising as completed.",
                default=True,
            ):
                cancelled = False
    finally:
        # 4. Stop recording immediately
        recording_active.clear()
        enter_pressed.set()  # Signal display thread to stop

        # Restore console handler if it was suppressed
        if console_handler:
            root_logger.addHandler(console_handler)

        # CRITICAL: Close audio stream and WAV file FIRST
        # This ensures the file is properly flushed and closed before transcription
        try:
            stream.stop()
            stream.close()
        except Exception:  # pragma: no cover - defensive cleanup
            # Errors here are logged in the audio module; the CLI should not
            # crash during shutdown.
            pass

        try:
            wav_file.close()
        except Exception:  # pragma: no cover - defensive cleanup
            pass

        # Wait for display thread to finish (with timeout)
        # Only call join once - removed duplicate
        display_thread.join(timeout=0.5)

        # If display thread is still alive, it's a daemon so it will be killed
        # Don't block forever waiting for it
        sys.stdout.write("\033[2J\033[H")
        console.print("\n⏹️  Stopping recording...")

    if cancelled:
        # Offer optional deletion, but default to keeping the file marked
        # as cancelled to preserve data integrity.
        delete_file = Confirm.ask(
            "Delete the partial transcript file?",
            default=False,
        )
        if delete_file:
            try:
                filepath.unlink()
                console.print(
                    "\n🗑️  Recording cancelled and transcript file deleted.",
                )
            except FileNotFoundError:  # pragma: no cover - defensive
                console.print(
                    "\n⚠️  Transcript file was already removed.",
                )
        else:
            update_status(filepath, "cancelled")
            console.print(
                "\n⚠️  Recording cancelled. Transcript marked as "
                "[bold]cancelled[/bold] and kept on disk.",
            )
        # Clean up temp audio file for cancelled recordings
        try:
            temp_audio_path.unlink(missing_ok=True)
        except Exception:  # pragma: no cover - defensive cleanup
            pass
    else:
        # 5. Run single transcription pass with progress display
        sys.stdout.write("\033[2J\033[H")

        # Get audio duration for progress calculation
        import wave as wave_module

        try:
            with wave_module.open(str(temp_audio_path), "rb") as wf:
                audio_duration = wf.getnframes() / wf.getframerate()
        except Exception:
            audio_duration = None

        transcription_start_time = time.time()
        segments = []
        segment_count = 0

        try:
            # Suppress verbose INFO logs from faster-whisper, huggingface, httpx
            # These libraries log model downloads/checks which are noisy
            # Note: Models are cached locally - HTTP request is just a version
            # check, not a download
            import logging

            # Get root logger and its console handler
            root_logger = logging.getLogger()
            console_handler = None
            original_console_level = None
            for handler in root_logger.handlers:
                # Find the RichHandler (console handler)
                if hasattr(handler, "rich_tracebacks"):
                    console_handler = handler
                    original_console_level = handler.level
                    # Temporarily suppress INFO logs on console
                    handler.setLevel(logging.WARNING)
                    break

            # Also suppress at logger level for noisy libraries
            noisy_loggers = [
                "faster_whisper",
                "huggingface_hub",
                "httpx",
                "httpcore",
            ]
            for logger_name in noisy_loggers:
                logger = logging.getLogger(logger_name)
                logger.setLevel(logging.WARNING)

            try:
                transcriber = Transcriber(config.transcription)

                # Flag to control display thread
                transcription_active = threading.Event()
                transcription_active.set()

                # Transcription progress display with Live panel
                def _display_transcription_progress():
                    """Display live transcription progress."""
                    with Live(console=console, auto_refresh=True, screen=False) as live:
                        while transcription_active.is_set():
                            elapsed = time.time() - transcription_start_time
                            minutes, seconds = divmod(int(elapsed), 60)
                            tenths = int((elapsed % 1) * 10)
                            elapsed_formatted = f"{minutes:02d}:{seconds:02d}.{tenths}"

                            # Calculate progress percentage
                            # (estimate based on elapsed time)
                            if audio_duration:
                                # Estimate: assume transcription takes ~0.5x realtime
                                # (twice as fast as audio duration)
                                # This factor should be tuned based on your hardware
                                # and model size (e.g., 0.1 on GPU, 0.5 on fast CPU)
                                estimated_total_duration = audio_duration * 0.1
                                progress_pct = min(
                                    100, int((elapsed / estimated_total_duration) * 100)
                                )
                            else:
                                progress_pct = 0

                            # Create progress bar (50 chars)
                            filled = int(progress_pct / 2)
                            progress_bar = "█" * filled + "░" * (50 - filled)

                            panel_content = (
                                f"STATUS        TRANSCRIBING\n"
                                f"SESSION ID    {transcript_id}\n"
                                f"FILE          {filepath.name}\n"
                                f"\n"
                                f"PROGRESS      {progress_bar} {progress_pct}%\n"
                                f"ELAPSED       {elapsed_formatted}\n"
                                f"\n"
                                f"OUTPUT\n"
                                f"Processing audio…"
                            )

                            panel = Panel(
                                panel_content,
                                title="Rejoice",
                                border_style="yellow",
                            )
                            live.update(panel)
                            time.sleep(0.01)

                # Start display thread
                display_thread = threading.Thread(
                    target=_display_transcription_progress, daemon=True
                )
                display_thread.start()

                # Transcribe
                for segment in transcriber.transcribe_file(str(temp_audio_path)):
                    text = str(segment.get("text", "")).strip()
                    if text:
                        segments.append(text)
                        segment_count += 1

                # Stop display thread
                transcription_active.clear()
                display_thread.join(timeout=0.5)

                # Write final transcript atomically
                if segments:
                    final_text = " ".join(segments)
                    append_to_transcript(filepath, final_text)

                # Update language in frontmatter if detected
                if transcriber.last_language:
                    update_language(filepath, transcriber.last_language)
            finally:
                # Restore console handler level
                if console_handler and original_console_level is not None:
                    console_handler.setLevel(original_console_level)
                # Restore loggers to use parent logger's level
                # (NOTSET = inherit from root)
                for logger_name in noisy_loggers:
                    logging.getLogger(logger_name).setLevel(logging.NOTSET)

        except Exception as e:  # pragma: no cover - defensive error handling
            console.print(f"[yellow]Warning: Transcription failed: {e}[/yellow]")

        # 6. Finalise the transcript frontmatter to reflect a completed recording.
        update_status(filepath, "completed")

        # Calculate duration and word count for final output
        duration_seconds = time.time() - start_time
        minutes, seconds = divmod(int(duration_seconds), 60)
        duration_formatted = f"{minutes:02d}:{seconds:02d}"

        # Count words in transcript
        if segments:
            final_text = " ".join(segments)
            word_count = len(final_text.split())
        else:
            word_count = 0

        # Prompt to delete audio file (default yes)
        should_delete = True
        if temp_audio_path.exists():
            should_delete = Confirm.ask("Delete temporary audio file?", default=True)
            if should_delete:
                try:
                    temp_audio_path.unlink(missing_ok=True)
                except Exception:  # pragma: no cover - defensive cleanup
                    pass

        # Final completion output
        sys.stdout.write("\033[2J\033[H")
        final_panel = Panel(
            f"✅ COMPLETE\n"
            f"SESSION ID    {transcript_id}\n"
            f"FILE          {filepath.name}\n"
            f"DURATION      {duration_formatted}\n"
            f"WORDS         {word_count}\n\n"
            f"OUTPUT\n"
            f"Saved to {filepath.parent}",
            title="Rejoice",
            border_style="green",
        )
        console.print(final_panel)

    return filepath, transcript_id


def _iter_transcripts(save_dir: Path) -> list[Path]:
    """Yield transcript files in the given directory matching the standard pattern."""
    if not save_dir.exists():
        return []

    files: list[Path] = []
    for entry in save_dir.iterdir():
        if not entry.is_file():
            continue
        if TRANSCRIPT_FILENAME_PATTERN.match(entry.name):
            files.append(entry)

    # Sort by date (derived from filename) and ID, newest first.
    def sort_key(path: Path) -> tuple[str, str]:
        match = TRANSCRIPT_FILENAME_PATTERN.match(path.name)
        assert match is not None  # Covered by construction above
        id_str, date_str = match.groups()
        return (date_str, id_str)

    files.sort(key=sort_key, reverse=True)
    return files


def _get_transcript_dir() -> Path:
    """Return the transcripts directory from the loaded configuration."""
    config = load_config()
    return Path(config.output.save_path).expanduser()


def _get_latest_transcript_path(save_dir: Path) -> Path | None:
    """Return the most recent transcript path, or ``None`` if none exist."""
    transcripts = _iter_transcripts(save_dir)
    if not transcripts:
        return None
    return transcripts[0]


def _get_transcript_path_by_id(save_dir: Path, user_supplied_id: str) -> Path | None:
    """Resolve a user-supplied transcript ID to an existing file path.

    The ID is normalised via :func:`normalize_id` to allow flexible input
    (for example ``"1"`` or ``"000001"``) while still relying on the
    standard filename pattern.
    """
    normalised_id = normalize_id(user_supplied_id)

    for entry in save_dir.iterdir():
        if not entry.is_file():
            continue
        match = TRANSCRIPT_FILENAME_PATTERN.match(entry.name)
        if not match:
            continue
        id_str, _date_str = match.groups()
        if id_str == normalised_id:
            return entry

    return None


def _split_frontmatter(content: str) -> tuple[str, str]:
    """Split transcript content into YAML frontmatter and body.

    Returns a tuple of ``(frontmatter, body)`` where ``frontmatter`` is an
    empty string if no valid frontmatter block is present.
    """
    if not content.startswith("---"):
        return "", content

    try:
        first_sep_end = content.index("\n", 3)
        second_sep_start = content.index("\n---", first_sep_end)
    except ValueError as exc:
        raise TranscriptError(
            "Transcript frontmatter is malformed.",
            suggestion=(
                "Check the transcript file for manual edits to the '---' markers."
            ),
        ) from exc

    frontmatter_block = content[0 : second_sep_start + len("\n---\n")]
    body = content[second_sep_start + len("\n---\n") :]
    return frontmatter_block.strip("\n"), body.lstrip("\n")


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show version and exit")
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.option(
    "--language",
    "-l",
    metavar="CODE",
    help="Force transcription language (e.g. en, es, fr).",
)
@click.option(
    "--skip-setup",
    is_flag=True,
    help="Skip first-run setup check (for advanced users)",
)
@click.pass_context
def main(ctx, version, debug, language, skip_setup):
    """Rejoice - Local voice transcription tool.

    Run 'rec' to start recording.
    Press Enter to stop.
    """
    # Set up logging first
    setup_logging(debug=debug)

    if version:
        console.print(f"Rejoice v{__version__}")
        ctx.exit(0)

    if debug:
        console.print("[yellow]Debug mode enabled[/yellow]")

    # Note: Setup is now run during installation, not on first run
    # Users can run 'rec config mic' or other config commands to change settings

    # Store debug flag and language override in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug
    ctx.obj["language"] = language

    # If no subcommand, start a recording session
    if ctx.invoked_subcommand is None:
        language_override = ctx.obj.get("language") if ctx.obj else None
        start_recording_session(language_override=language_override)


@main.command("list")
def list_recordings(limit: int = 50):
    """List recorded transcripts implementing [C-001] List Recordings Command."""
    config = load_config()
    save_dir = Path(config.output.save_path).expanduser()

    transcripts = _iter_transcripts(save_dir)
    if not transcripts:
        console.print("No recordings found in your transcripts directory.")
        return

    # Apply simple limit/pagination
    transcripts = transcripts[:limit]

    table = Table(title="Your Recordings")
    table.add_column("ID")
    table.add_column("Date")
    table.add_column("Filename")

    for path in transcripts:
        match = TRANSCRIPT_FILENAME_PATTERN.match(path.name)
        if not match:
            continue
        id_str, date_str = match.groups()
        formatted_date = f"{date_str[0:4]}-{date_str[4:6]}-{date_str[6:8]}"
        table.add_row(id_str, formatted_date, path.name)

    console.print(table)


@main.command("view")
@click.argument("transcript_id", default="latest")
@click.option(
    "--show-frontmatter/--hide-frontmatter",
    default=False,
    help="Show or hide YAML frontmatter metadata.",
)
def view_transcript(transcript_id: str, show_frontmatter: bool) -> None:
    """View a transcript in the terminal implementing [C-003].

    Supports ``rec view <id>`` and ``rec view latest``. Markdown is rendered
    using Rich and long transcripts are paginated.
    """
    save_dir = _get_transcript_dir()

    try:
        if transcript_id == "latest":
            path = _get_latest_transcript_path(save_dir)
        else:
            path = _get_transcript_path_by_id(save_dir, transcript_id)
    except TranscriptError as exc:
        console.print(f"[red]{exc}[/red]")
        raise click.Abort() from exc

    if path is None:
        if transcript_id == "latest":
            console.print("No transcripts found to display.")
        else:
            # Normalise for user-friendly error without raising again.
            normalised = normalize_id(transcript_id)
            console.print(
                f"Transcript with ID {normalised} was not found in your transcripts "
                "directory.",
            )
        raise click.Abort()

    raw = path.read_text(encoding="utf-8")
    frontmatter_block, body = _split_frontmatter(raw)

    if show_frontmatter and frontmatter_block:
        console.print("[bold]Metadata[/bold]")
        console.print(frontmatter_block)
        console.print()

    markdown = Markdown(body or "")
    console.print(markdown)


# Add config subcommand group
main.add_command(config_group, name="config")


if __name__ == "__main__":
    main()
