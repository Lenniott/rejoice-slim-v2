"""CLI commands for Rejoice."""
from __future__ import annotations

import time
from pathlib import Path

import click
from rich.console import Console
from rich.prompt import Confirm

from rejoice import __version__
from rejoice.audio import record_audio
from rejoice.cli.config_commands import config_group
from rejoice.core.config import load_config
from rejoice.core.logging import setup_logging
from rejoice.transcript.manager import create_transcript, update_status

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
):
    """Start a recording session implementing [R-006] Recording Control - Start.

    Steps:
    - Load configuration
    - Immediately create a transcript file (zero data loss)
    - Start audio capture using the configured device and sample rate
    - Block until ``wait_for_stop`` returns
    - Clean up the audio stream and print a simple duration summary

    Returns:
        tuple[Path, str]: The transcript filepath and ID.
    """
    config = load_config()

    # 1. Create transcript file immediately (zero data loss principle)
    save_dir = Path(config.output.save_path).expanduser()
    filepath, transcript_id = create_transcript(save_dir)

    console.print(f"🎙️  Recording started [dim](ID {transcript_id})[/dim]")
    console.print(f"📄  Transcript: {filepath}")

    # 2. Start audio capture
    start_time = time.time()

    def _audio_callback(indata, frames, timing, status):  # pragma: no cover
        # Placeholder for streaming/transcription pipeline in later stories.
        # For now we simply discard audio blocks; the focus of [R-006] is the
        # control flow and zero-data-loss transcript creation.
        return

    stream = record_audio(
        _audio_callback,
        device=config.audio.device if config.audio.device != "default" else None,
        samplerate=config.audio.sample_rate,
        channels=1,
    )

    cancelled = False

    try:
        # 3. Wait for stop signal (keypress)
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
        # 4. Clean up audio stream and display basic duration information
        try:
            stream.stop()
            stream.close()
        except Exception:  # pragma: no cover - defensive cleanup
            # Errors here are logged in the audio module; the CLI should not
            # crash during shutdown.
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
    else:
        # 5. Finalise the transcript frontmatter to reflect a completed recording.
        update_status(filepath, "completed")
        console.print(
            "\n✅ Recording stopped. Transcript marked as [bold]completed[/bold].",
        )
        console.print(f"📄 File saved at: {filepath}")

    return filepath, transcript_id


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
        start_recording_session()


# Add config subcommand group
main.add_command(config_group, name="config")


if __name__ == "__main__":
    main()
