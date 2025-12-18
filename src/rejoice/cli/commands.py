"""CLI commands for Rejoice."""
from __future__ import annotations

import time
from pathlib import Path

import click
from rich.console import Console

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
    try:
        click.getchar()
    except (KeyboardInterrupt, EOFError):
        # Treat interrupts as a normal stop signal for now.
        pass


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

    try:
        # 3. Wait for stop signal (keypress)
        wait_for_stop()
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

    # 5. Finalise the transcript frontmatter to reflect a completed recording.
    update_status(filepath, "completed")
    console.print("\n✅ Recording stopped. Transcript marked as [bold]completed[/bold].")
    console.print(f"📄 File saved at: {filepath}")

    return filepath, transcript_id


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show version and exit")
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.pass_context
def main(ctx, version, debug):
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

    # Store debug flag in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug

    # If no subcommand, start a recording session
    if ctx.invoked_subcommand is None:
        start_recording_session()


# Add config subcommand group
main.add_command(config_group, name="config")


if __name__ == "__main__":
    main()
