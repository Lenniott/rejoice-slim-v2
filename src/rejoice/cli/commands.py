"""CLI commands for Rejoice."""
from __future__ import annotations

import tempfile
import time
import wave
from pathlib import Path
from typing import Optional

import click
import numpy as np
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Confirm
from rich.table import Table

from rejoice import __version__
from rejoice.audio import record_audio
from rejoice.cli.config_commands import config_group
from rejoice.core.config import load_config
from rejoice.core.logging import setup_logging
from rejoice.exceptions import TranscriptionError, TranscriptError
from rejoice.transcription import Transcriber
from rejoice.transcript.manager import (
    TRANSCRIPT_FILENAME_PATTERN,
    create_transcript,
    normalize_id,
    update_status,
)

console = Console()


def _default_wait_for_stop() -> None:
    """Block until the user indicates recording should stop.

    Currently implemented as a simple keypress prompt; later stories
    ([R-007], [R-008]) build on this for richer control.
    """
    console.print("[bold]Press Enter to stop recording.[/bold]")
    click.getchar()


def start_recording_session(
    *,
    wait_for_stop=_default_wait_for_stop,
    language_override: Optional[str] = None,
):
    """Start a recording session implementing [R-006] Recording Control - Start
    and [T-009] Connect Recording to Transcription.

    Steps:
    - Load configuration
    - Immediately create a transcript file (zero data loss)
    - Create temporary WAV file for audio capture
    - Start audio capture using the configured device and sample rate
    - Write audio data to temporary WAV file during recording
    - Block until ``wait_for_stop`` returns
    - Clean up the audio stream and display basic duration information
    - If not cancelled, transcribe the temporary audio file
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

    console.print(f"🎙️  Recording started [dim](ID {transcript_id})[/dim]")
    console.print(f"📄  Transcript: {filepath}")

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

    # 3. Start audio capture
    start_time = time.time()

    def _audio_callback(indata, frames, timing, status):  # pragma: no cover
        # Write audio buffer to WAV file
        # Convert float32 to int16 PCM
        audio_int16 = (indata * 32767).astype(np.int16)
        wav_file.writeframes(audio_int16.tobytes())

    stream = record_audio(
        _audio_callback,
        device=config.audio.device if config.audio.device != "default" else None,
        samplerate=config.audio.sample_rate,
        channels=1,
    )

    cancelled = False

    try:
        # 4. Wait for stop signal (keypress)
        try:
            wait_for_stop()
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
        # 5. Clean up audio stream and WAV file
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

        duration_seconds = int(time.time() - start_time)
        minutes, seconds = divmod(duration_seconds, 60)
        console.print(f"⏱️  Duration: {minutes:d}:{seconds:02d}")

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
        # 6. Finalise the transcript frontmatter to reflect a completed recording.
        update_status(filepath, "completed")
        console.print(
            "\n✅ Recording stopped. Transcript marked as [bold]completed[/bold].",
        )

        # 7. Transcribe the audio file [T-009]
        try:
            console.print("🔄 Transcribing audio...")
            transcriber = Transcriber(config.transcription)
            # Consume the generator to trigger transcription and file appends
            list(transcriber.stream_file_to_transcript(str(temp_audio_path), filepath))
            console.print("✅ Transcription complete.")
        except TranscriptionError as e:
            # Handle transcription errors gracefully without crashing
            console.print(f"[yellow]Transcription failed: {e}[/yellow]")
            if e.suggestion:
                console.print(f"[dim]{e.suggestion}[/dim]")
        except Exception as e:  # pragma: no cover - defensive error handling
            # Catch any other unexpected errors during transcription
            console.print(
                f"[yellow]Unexpected error during transcription: {e}[/yellow]"
            )
        finally:
            # Always clean up temp audio file
            try:
                temp_audio_path.unlink(missing_ok=True)
            except Exception:  # pragma: no cover - defensive cleanup
                pass

        console.print(f"📄 File saved at: {filepath}")

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
        date_str, id_str = match.groups()
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
        _date_str, id_str = match.groups()
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
@click.pass_context
def main(ctx, version, debug, language):
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
        date_str, id_str = match.groups()
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
