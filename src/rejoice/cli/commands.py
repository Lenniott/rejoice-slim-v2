"""CLI commands for Rejoice."""

from __future__ import annotations

import contextlib
import io
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
from rich.progress import BarColumn, Progress, TimeElapsedColumn
from rich.prompt import Confirm
from rich.table import Table

from rejoice import __version__
from rejoice.audio import record_audio
from rejoice.cli.config_commands import config_group
from rejoice.core.config import load_config
from rejoice.core.logging import setup_logging
from rejoice.exceptions import TranscriptError
from rejoice.transcription import Transcriber
from rejoice.audio.archive import archive_audio_file
from rejoice.transcript.manager import (
    append_to_transcript,
    create_transcript,
    migrate_filenames,
    normalize_id,
    parse_transcript_filename,
    update_audio_file,
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
    # Simple input() - reads from terminal
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        raise


def _calculate_audio_level(audio_chunk: np.ndarray) -> float:
    """Calculate RMS audio level for visual meter.

    Returns a normalized value between 0.0 and 1.0 representing audio level.
    Uses a more sensitive scaling to show movement even with quiet speech.
    """
    if len(audio_chunk) == 0:
        return 0.0
    # Calculate RMS (Root Mean Square) for audio level
    rms = float(np.sqrt(np.mean(audio_chunk**2)))
    # Normalize to 0-1 range (assuming input is typically -1.0 to 1.0)
    # Use a smaller divisor (0.1 instead of 0.5) to make the meter 5x more sensitive
    # This means normal speech will show movement without needing to shout
    # Clamp to prevent values > 1.0 from causing display issues
    return min(1.0, rms / 0.05)


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
    # Suppress warnings for the entire recording session to keep output clean
    import warnings

    warnings.filterwarnings("ignore")

    config = load_config()

    # Override language if provided via CLI flag
    if language_override:
        config.transcription.language = language_override

    # 1. Create transcript file immediately (zero data loss principle)
    save_dir = Path(config.output.save_path).expanduser()
    filepath, transcript_id = create_transcript(save_dir)

    console.print("⏳ Loading Rejoice...")
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

    # 3. Start recording - stream must be active before showing "Recording started"
    stream = record_audio(
        _audio_callback,
        device=config.audio.device if config.audio.device != "default" else None,
        samplerate=config.audio.sample_rate,
        channels=1,
    )

    # 4. NOW show "Recording started" message - recording is actually happening
    # console.print(f"🎙️  Recording started [dim](ID {transcript_id})[/dim]")
    # console.print(f"📄  Transcript: {filepath}")
    # No delay needed - inline updates don't require screen switching
    # Messages appear above the Live frame

    # 5. Initialize timer NOW - recording is actually happening
    start_time = time.time()

    cancelled = False

    # Input handling in separate thread to avoid blocking display updates
    # This prevents race conditions between display refresh and user input
    enter_pressed = threading.Event()

    def _wait_for_enter_input():
        """Wait for Enter in separate thread."""
        try:
            input()
            enter_pressed.set()
        except (EOFError, KeyboardInterrupt):
            enter_pressed.set()
            raise

    # Start input thread
    input_thread = threading.Thread(target=_wait_for_enter_input, daemon=True)
    input_thread.start()

    # During Live rendering, console output is reserved exclusively for the frame.
    # While Live is active, the frame owns stdout.
    # Suppress console logging to prevent logs from corrupting frame borders,
    # pushing content upward, or interleaving mid-refresh.
    import logging

    root_logger = logging.getLogger()
    console_handler = None
    original_console_level = None

    for handler in root_logger.handlers:
        if hasattr(handler, "rich_tracebacks"):
            console_handler = handler
            original_console_level = handler.level
            # Raise handler level to ERROR to prevent any logs during Live rendering
            # This enforces the rule: "While Live is active, the frame owns stdout"
            handler.setLevel(logging.ERROR)
            break

    # Display thread for Rich Live panel
    def _display_recording_status():
        """Display live recording status with elapsed time and audio level."""
        try:
            # During Live rendering, console output is reserved exclusively for the
            # frame. While Live is active, the frame owns stdout.
            # Logs are suppressed to avoid corrupting the display.
            sys.stdout.write("\033[2J\033[H")
            with Live(
                console=console, auto_refresh=True, screen=False, transient=False
            ) as live:
                # Throttle updates by state to avoid unnecessary redraws
                # RECORDING: ~10-15 fps (66-100ms) for audio level meter
                RECORDING_REFRESH_INTERVAL = 0.1  # 10 fps for recording
                last_update_time = 0.0

                while recording_active.is_set() and not enter_pressed.is_set():
                    current_time = time.time()

                    # Throttle updates for recording state
                    if current_time - last_update_time >= RECORDING_REFRESH_INTERVAL:
                        elapsed = current_time - start_time
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
                        last_update_time = current_time

                    # Check exit condition more frequently than refresh rate
                    time.sleep(0.05)
        finally:
            # Live context exits automatically when the with block exits
            # Restore console handler level so logs can appear again
            if console_handler and original_console_level is not None:
                console_handler.setLevel(original_console_level)

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
        # The display thread will restore the console handler in its finally block
        display_thread.join(
            timeout=1.0
        )  # Increased timeout to allow Live context to exit

        # Brief pause to ensure Live context has fully exited
        # Inline updates don't require screen restoration, but we want clean state
        if not display_thread.is_alive():
            try:
                time.sleep(0.1)  # Brief pause to ensure clean state
            except KeyboardInterrupt:
                # Ignore KeyboardInterrupt during cleanup to ensure cancelled status
                # is properly set
                pass

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
        # 5. Archive audio file before transcription (R-013)
        # Only archive if temp file exists (it may not exist in test scenarios
        # or if recording was very short)
        archived_audio_path = None
        if temp_audio_path.exists():
            # Move temp audio file to permanent archive location
            archived_audio_path = archive_audio_file(temp_audio_path, filepath)

            # Update frontmatter with relative path to archived audio file
            relative_audio_path = archived_audio_path.relative_to(filepath.parent)
            update_audio_file(filepath, str(relative_audio_path))

            console.print(f"💾 Audio archived: {relative_audio_path}")
        else:
            import logging

            logging.getLogger(__name__).warning(
                f"Temp audio file {temp_audio_path} doesn't exist, skipping archiving"
            )

        # 6. Run single transcription pass with progress bar
        sys.stdout.write("\033[2J\033[H")
        console.print("🔄 Transcribing...")
        transcription_successful = False
        try:
            # Suppress all verbose output from WhisperX and its dependencies
            import logging

            # Warnings are already suppressed at the start of the function

            # Get root logger and its console handler
            root_logger = logging.getLogger()
            console_handler = None
            original_console_level = None
            for handler in root_logger.handlers:
                # Find the RichHandler (console handler)
                if hasattr(handler, "rich_tracebacks"):
                    console_handler = handler
                    original_console_level = handler.level
                    # Temporarily suppress all logs below ERROR on console
                    handler.setLevel(logging.ERROR)
                    break

            # Suppress at logger level for all noisy libraries
            noisy_loggers = [
                "faster_whisper",
                "whisperx",
                "whisperx.asr",
                "whisperx.vads",
                "whisperx.vads.silero",
                "huggingface_hub",
                "httpx",
                "httpcore",
                "urllib3",
                "torchaudio",
                "speechbrain",
                "pyannote",
            ]
            for logger_name in noisy_loggers:
                logger = logging.getLogger(logger_name)
                logger.setLevel(logging.ERROR)

            # Capture stdout/stderr during transcription to suppress WhisperX
            # progress bars, print statements, and warnings
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
                io.StringIO()
            ):
                transcriber = Transcriber(config.transcription)
                segments = []

                with Progress(
                    BarColumn(),
                    TimeElapsedColumn(),
                    console=console,
                ) as progress:
                    progress.add_task("Transcribing", total=None)
                    # Use archived audio path if available, otherwise fall back
                    # to temp (for test scenarios)
                    audio_file_path = (
                        str(archived_audio_path)
                        if archived_audio_path
                        else str(temp_audio_path)
                    )
                    for segment in transcriber.transcribe_file(audio_file_path):
                        text = str(segment.get("text", "")).strip()
                        if text:
                            segments.append(text)

                # Write final transcript atomically
                if segments:
                    final_text = " ".join(segments)
                    append_to_transcript(filepath, final_text)

                # Update language in frontmatter if detected
                if transcriber.last_language:
                    update_language(filepath, transcriber.last_language)

                transcription_successful = True

            # Restore console handler level
            if console_handler and original_console_level is not None:
                console_handler.setLevel(original_console_level)
            # Restore loggers to use parent logger's level
            # (NOTSET = inherit from root)
            for logger_name in noisy_loggers:
                logging.getLogger(logger_name).setLevel(logging.NOTSET)
            # Warnings remain suppressed for the entire session to keep output clean

        except Exception as e:  # pragma: no cover - defensive error handling
            console.print(f"[yellow]Warning: Transcription failed: {e}[/yellow]")
            # Audio file is preserved on transcription failure (R-013 requirement)
            if archived_audio_path:
                console.print(
                    f"⚠️  Transcription failed. Audio file kept for recovery: "
                    f"{archived_audio_path.name}"
                )
            else:
                console.print("⚠️  Transcription failed. No audio file was recorded.")
        finally:
            # Note: Temp audio file has been archived, so no cleanup needed here
            # The archived audio file will be handled by deletion prompt logic
            pass

        # 7. Finalise the transcript frontmatter to reflect a completed recording.
        update_status(filepath, "completed")

        # After transcription completes, render final COMPLETE state
        # This ensures the last state is clean and prevents half-frames if the thread
        # exits early. Makes COMPLETE state deterministic.
        if transcription_successful:
            # Calculate duration from audio file (not session time)
            # Use archived audio file if available, otherwise fall back to temp file
            audio_file_for_duration = (
                archived_audio_path if archived_audio_path else temp_audio_path
            )
            try:
                with wave.open(str(audio_file_for_duration), "rb") as wav_reader:
                    frames = wav_reader.getnframes()
                    sample_rate = wav_reader.getframerate()
                    recording_duration = frames / sample_rate
            except Exception:
                # Fallback to session time if we can't read the audio file
                recording_duration = time.time() - start_time

            duration_minutes = int(recording_duration // 60)
            duration_seconds = int(recording_duration % 60)
            duration_formatted = f"{duration_minutes:02d}:{duration_seconds:02d}"

            # Count words in transcript
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Extract body (after frontmatter)
                    if "---\n" in content:
                        parts = content.split("---\n", 2)
                        body = parts[2] if len(parts) > 2 else content
                    else:
                        body = content
                    word_count = len(body.split())
            except Exception:
                word_count = 0

            sys.stdout.write("\033[2J\033[H")
            # Render COMPLETE state
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
        else:
            console.print(f"✅ Transcript saved: {filepath}")

        # 8. Handle audio file deletion prompt (R-013)
        # Only prompt if transcription succeeded and audio file was archived
        if transcription_successful and archived_audio_path:
            # Check if we should skip prompt
            skip_prompt = (
                config.audio.auto_delete or not config.audio.keep_after_transcription
            )

            relative_audio_path = archived_audio_path.relative_to(filepath.parent)

            if skip_prompt:
                # Keep file silently (no prompt)
                console.print(f"💾 Audio file kept: {relative_audio_path}")
            else:
                # Prompt user for deletion (default: n = keep)
                should_delete = Confirm.ask(
                    "Delete audio file to save space?",
                    default=False,
                )

                if should_delete:
                    try:
                        archived_audio_path.unlink(missing_ok=True)
                        console.print("🗑️  Audio file deleted")
                    except (
                        Exception
                    ) as e:  # pragma: no cover - defensive error handling
                        console.print(
                            f"[yellow]Warning: Could not delete audio file: "
                            f"{e}[/yellow]"
                        )
                else:
                    console.print(f"💾 Audio file kept: {relative_audio_path}")
        # If transcription failed, audio is already preserved (message shown above)

    return filepath, transcript_id


def _iter_transcripts(save_dir: Path) -> list[Path]:
    """Yield transcript files in the given directory matching the standard pattern.

    Supports both old format (transcript_YYYYMMDD_ID.md) and
    new format (ID_transcript_YYYYMMDD.md).
    """
    if not save_dir.exists():
        return []

    files: list[Path] = []
    for entry in save_dir.iterdir():
        if not entry.is_file():
            continue
        # Use parse_transcript_filename to check if it's a valid transcript file
        try:
            parse_transcript_filename(entry.name)
            files.append(entry)
        except TranscriptError:
            # Not a transcript file, skip it
            continue

    # Sort by date (derived from filename) and ID, newest first.
    def sort_key(path: Path) -> tuple[str, str]:
        date_str, id_str = parse_transcript_filename(path.name)
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
    standard filename pattern. Supports both old and new filename formats.
    """
    normalised_id = normalize_id(user_supplied_id)

    for entry in save_dir.iterdir():
        if not entry.is_file():
            continue
        try:
            _date_str, id_str = parse_transcript_filename(entry.name)
            if id_str == normalised_id:
                return entry
        except TranscriptError:
            # Not a transcript file, skip it
            continue

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
                "Check the transcript file for manual edits to the " "'---' markers."
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
        try:
            date_str, id_str = parse_transcript_filename(path.name)
            formatted_date = f"{date_str[0:4]}-{date_str[4:6]}-{date_str[6:8]}"
            table.add_row(id_str, formatted_date, path.name)
        except TranscriptError:
            # Skip invalid filenames (shouldn't happen due to filtering)
            continue

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


@main.command("migrate")
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Preview changes without modifying files",
)
@click.option(
    "--execute",
    is_flag=True,
    default=False,
    help="Perform the migration (requires confirmation)",
)
def migrate_command(dry_run: bool, execute: bool):
    """Migrate transcript filenames from old format to new format.

    Old format: transcript_YYYYMMDD_ID.md
    New format: ID_transcript_YYYYMMDD.md

    Use --dry-run to preview changes without modifying files.
    Use --execute to perform the migration.
    """
    if not dry_run and not execute:
        console.print("[yellow]Please specify either --dry-run or --execute[/yellow]")
        console.print("Use --help for more information")
        return

    if dry_run and execute:
        console.print("[yellow]Cannot use both --dry-run and --execute[/yellow]")
        return

    config = load_config()
    save_dir = Path(config.output.save_path).expanduser()

    if not save_dir.exists():
        console.print(
            f"[yellow]Transcript directory does not exist: {save_dir}[/yellow]"
        )
        return

        if dry_run:
            console.print("[bold]Dry-run mode: No files will be modified[/bold]\n")
            result = migrate_filenames(save_dir, dry_run=True)

            if not result["operations"]:
                console.print("No files found matching old format.")
                return

            console.print(f"Found {len(result['operations'])} file(s) to migrate:\n")
            for old_path, new_path in result["operations"]:
                console.print(f"  {old_path.name} → {new_path.name}")

            console.print(f"\n[green]Would rename {result['renamed']} file(s)[/green]")
            if result["failed"] > 0:
                console.print(f"[red]Would fail {result['failed']} file(s)[/red]")
                for error in result["errors"]:
                    console.print(f"  [red]{error}[/red]")

    if execute:
        console.print("[bold]Migration mode: Files will be renamed[/bold]\n")

        # Confirm before proceeding
        if not Confirm.ask("Do you want to proceed with the migration?"):
            console.print("[yellow]Migration cancelled[/yellow]")
            return

        result = migrate_filenames(save_dir, dry_run=False)

        if not result["operations"]:
            console.print("No files found matching old format.")
            return

        console.print(
            f"\n[green]Successfully renamed {result['renamed']} file(s)[/green]"
        )
        if result["failed"] > 0:
            console.print(f"[red]Failed to rename {result['failed']} file(s)[/red]")
            for error in result["errors"]:
                console.print(f"  [red]{error}[/red]")


# Add config subcommand group
main.add_command(config_group, name="config")


if __name__ == "__main__":
    main()
