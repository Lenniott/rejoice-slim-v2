"""First-run setup for Rejoice [I-007].

This module provides guided setup for new users, including:
- Model selection and downloading
- Microphone testing
- Save location configuration
- Ollama connection testing
- Sample transcript creation
"""

from __future__ import annotations

import logging
import signal
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from rejoice.audio import get_audio_input_devices, record_audio
from rejoice.core.config import get_config_dir, get_default_config
from rejoice.transcript.manager import create_transcript

try:
    import whisperx
except ImportError:  # pragma: no cover
    whisperx = None

if TYPE_CHECKING:
    from ollama import Client as Ollama
else:
    try:
        from ollama import Client as Ollama
    except ImportError:  # pragma: no cover
        Ollama = None

logger = logging.getLogger(__name__)
console = Console()


def is_first_run() -> bool:
    """Check if this is the first run (no config file exists).

    Returns
    -------
    bool
        True if config file doesn't exist, False otherwise.
    """
    config_dir = get_config_dir()
    config_file = config_dir / "config.yaml"
    return not config_file.exists()


def select_whisper_model() -> str:
    """Prompt user to select a Whisper model.

    Returns
    -------
    str
        Selected model name (tiny, base, small, medium, large).
    """
    models = [
        ("tiny", "Fastest, least accurate (~39MB)"),
        ("base", "Good balance, recommended (~74MB)"),
        ("small", "Better accuracy (~244MB)"),
        ("medium", "High accuracy (~769MB)"),
        ("large", "Best accuracy, slowest (~1550MB)"),
    ]

    table = Table(title="Whisper Model Options")
    table.add_column("Option", style="cyan")
    table.add_column("Model", style="green")
    table.add_column("Description", style="dim")

    for i, (model, desc) in enumerate(models, 1):
        table.add_row(str(i), model, desc)

    console.print(table)
    console.print()

    choice = Prompt.ask(
        "Select a model (1-5)",
        default="2",  # Default to "base"
        choices=["1", "2", "3", "4", "5"],
    )

    # Handle empty string (user just pressed Enter)
    if not choice:
        choice = "2"

    selected_model = models[int(choice) - 1][0]
    console.print(f"[green]Selected: {selected_model}[/green]\n")
    return selected_model


def verify_whisperx_installation() -> bool:
    """Verify WhisperX is installed and available.

    Note: WhisperX automatically downloads models on first use when
    whisperx.load_model() is called. We don't need to pre-download them here.

    Returns
    -------
    bool
        True if WhisperX is available, False otherwise.
    """
    if whisperx is None:
        console.print(
            "[red]Error: WhisperX is not installed.[/red]\n"
            "Please install it with: pip install whisperx"
        )
        return False

    console.print("[green]✓ WhisperX is installed[/green]")
    console.print(
        "[dim]Note: Models will download automatically on first transcription.[/dim]\n"
    )
    return True


def choose_microphone() -> str | int:
    """Prompt user to select a microphone from available devices.

    Returns
    -------
    str | int
        Device identifier: "default" string or device index (int).
        Returns "default" if user selects default option or no devices available.
    """
    try:
        devices = get_audio_input_devices()
    except RuntimeError as exc:
        console.print(f"[red]Error getting audio devices: {exc}[/red]")
        console.print("[yellow]Using default device[/yellow]\n")
        return "default"

    if not devices:
        console.print("[yellow]No audio input devices found.[/yellow]")
        console.print("[yellow]Using default device[/yellow]\n")
        return "default"

    # Create table showing available devices
    table = Table(title="Available Microphones", show_header=True, header_style="bold")
    table.add_column("Option", style="cyan")
    table.add_column("Index", style="dim")
    table.add_column("Name", style="green")
    table.add_column("Default", style="magenta")

    # Add "default" as option 0
    default_device = next((d for d in devices if d.get("is_default", False)), None)
    default_label = "✓ (system default)" if default_device else ""
    table.add_row("0", "-", "Use system default", default_label)

    # Add all devices
    for i, dev in enumerate(devices, 1):
        index = dev.get("index")
        name = dev.get("name", f"Device {index}")
        is_default = dev.get("is_default", False)
        default_marker = "✓" if is_default else ""
        table.add_row(str(i), str(index), name, default_marker)

    console.print(table)
    console.print()

    # Get user selection
    max_option = len(devices)
    choice = Prompt.ask(
        f"Select microphone (0-{max_option})",
        default="0",
        choices=[str(i) for i in range(max_option + 1)],
    )

    if choice == "0":
        console.print("[green]Selected: System default[/green]\n")
        return "default"

    selected_index = int(choice) - 1
    selected_device = devices[selected_index]
    device_name = selected_device.get("name", f"Device {selected_device.get('index')}")
    # device_index is guaranteed to be int from the device dict
    device_index = selected_device.get("index", 0)

    console.print(f"[green]Selected: {device_name}[/green]\n")
    # Cast to satisfy mypy - device_index from dict is always int
    return int(device_index) if isinstance(device_index, (int, str)) else 0


def test_microphone(device: str | int | None = None, duration: float = 3.0) -> bool:
    """Test microphone by showing audio level meter briefly.

    This is a quick visual test - just check if the volume meter responds.
    Press Ctrl+C to cancel at any time.

    Parameters
    ----------
    device:
        Device identifier: "default" string, device index (int), or None for default.
    duration:
        Duration of test recording in seconds (default: 1.5 seconds).

    Returns
    -------
    bool
        True if microphone test succeeded, False otherwise.
    """
    try:
        import numpy as np
        import threading
        from rich.live import Live
        from rich.panel import Panel

        audio_data = []
        recording_done = False
        cancel_event = threading.Event()  # Use Event for thread-safe cancellation
        audio_level = 0.0
        audio_level_lock = threading.Lock()
        stream = None

        # Set up signal handler for Ctrl+C to ensure it works even with Rich
        # Live context
        def signal_handler(signum, frame):
            nonlocal recording_done
            recording_done = True
            cancel_event.set()  # Also set the event for thread-safe cancellation

        original_handler = signal.signal(signal.SIGINT, signal_handler)

        def audio_callback(indata, frames, timing, status):
            if not recording_done:
                audio_data.append(indata.copy())
                # Calculate audio level for display
                rms = float(np.sqrt(np.mean(indata**2)))
                level = min(1.0, rms / 0.5)  # Normalize like in recording
                with audio_level_lock:
                    nonlocal audio_level
                    audio_level = level

        # Convert device parameter for record_audio
        # record_audio accepts None for default, or int/string for specific device
        audio_device = None if (device is None or device == "default") else device

        stream = record_audio(
            audio_callback,
            device=audio_device,
            samplerate=16000,
            channels=1,
        )

        # Small delay to ensure stream is actually recording
        time.sleep(0.1)

        # Start time after stream is confirmed ready
        start_time = time.time()

        # Display live audio level meter
        def _display_audio_level():
            try:
                with Live(console=console, auto_refresh=False, screen=False) as live:
                    while not recording_done and not cancel_event.is_set():
                        elapsed = time.time() - start_time
                        remaining = max(0.0, duration - elapsed)

                        with audio_level_lock:
                            current_level = audio_level

                        # Create audio level bars (0-20 bars)
                        num_bars = int(current_level * 20)
                        level_bars = "█" * num_bars + "░" * (20 - num_bars)

                        status_text = (
                            "Complete!"
                            if remaining <= 0
                            else f"{remaining:.1f}s remaining"
                        )

                        panel_content = (
                            f"🎤 Testing microphone...\n"
                            f"⏱️  {status_text}\n"
                            f"📊 [{level_bars}]\n\n"
                            f"Please speak into your microphone.\n"
                            f"[dim]Press Ctrl+C to cancel[/dim]"
                        )

                        panel = Panel(
                            panel_content,
                            title="Microphone Test",
                            border_style="yellow",
                        )
                        live.update(panel)
                        live.refresh()
                        time.sleep(0.1)  # Update 10 times per second
            except Exception:
                pass  # Ignore errors in display thread

        display_thread = threading.Thread(target=_display_audio_level, daemon=True)
        display_thread.start()

        # Record for specified duration (can be interrupted with Ctrl+C)
        # Use interruptible sleep loop instead of single time.sleep() to ensure
        # Ctrl+C is properly handled even when Rich Live context is active
        try:
            # Sleep in small increments to allow Ctrl+C to interrupt
            # Use cancel_event.wait() which is interruptible and thread-safe
            elapsed = 0.0
            while (
                elapsed < duration and not recording_done and not cancel_event.is_set()
            ):
                sleep_interval = min(
                    0.1, duration - elapsed
                )  # Sleep in 0.1s increments
                if sleep_interval > 0:
                    # Use cancel_event.wait() which can be interrupted by the
                    # event being set
                    if cancel_event.wait(timeout=sleep_interval):
                        # Event was set (cancelled)
                        break
                elapsed = time.time() - start_time
                # Check recording_done and cancel_event again after sleep
                if recording_done or cancel_event.is_set():
                    break

            # Check if cancellation occurred (via signal handler)
            if recording_done or cancel_event.is_set():
                console.print("\n[yellow]⚠ Test cancelled by user[/yellow]")
                return True  # Don't fail setup if user cancels
        except KeyboardInterrupt:
            console.print("\n[yellow]⚠ Test cancelled by user[/yellow]")
            return True  # Don't fail setup if user cancels
        finally:
            # Restore original signal handler
            signal.signal(signal.SIGINT, original_handler)
            # Always stop recording and close stream, even if interrupted
            recording_done = True
            cancel_event.set()  # Ensure event is set to stop display thread
            if stream is not None:
                try:
                    stream.stop()
                    stream.close()
                except Exception:
                    pass  # Stream may already be closed

        # Wait for display thread to finish (with timeout to prevent hanging)
        display_thread.join(timeout=0.5)

        # Check if we got audio (simple check - just see if meter moved)
        if audio_data:
            # Calculate RMS level
            all_audio = np.concatenate(audio_data)
            rms = float(np.sqrt(np.mean(all_audio**2)))
            if rms > 0.001:  # Lower threshold - just check if any audio detected
                console.print(
                    "[green]✓ Microphone test passed - audio detected[/green]\n"
                )
                return True
            else:
                console.print(
                    "[yellow]⚠ Microphone detected but no audio input[/yellow]\n"
                )
                return True  # Still consider it working (mic exists, just quiet)
        else:
            console.print("[yellow]⚠ No audio data received[/yellow]\n")
            return True  # Don't fail setup - mic might just be quiet

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠ Test cancelled by user[/yellow]\n")
        return True  # Don't fail setup if user cancels
    except Exception as exc:
        console.print(f"[red]✗ Microphone test failed: {exc}[/red]\n")
        logger.error(f"Microphone test failed: {exc}", exc_info=True)
        return False


def setup_save_location() -> str:
    """Prompt user to set save location for transcripts.

    Returns
    -------
    str
        Expanded path to save directory.
    """
    default_path = str(Path.home() / "Documents" / "transcripts")

    console.print("Where should transcripts be saved?")
    save_path = Prompt.ask("Save location", default=default_path)

    # Expand user home directory
    expanded_path = str(Path(save_path).expanduser())

    # Create directory if it doesn't exist
    save_dir = Path(expanded_path)
    save_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"[green]✓ Transcripts will be saved to: {expanded_path}[/green]\n")
    return expanded_path


def test_ollama_connection(url: str = "http://localhost:11434") -> bool:
    """Test connection to Ollama server.

    Parameters
    ----------
    url:
        Ollama server URL.

    Returns
    -------
    bool
        True if connection successful, False otherwise.
    """
    if Ollama is None:
        console.print(
            "[yellow]⚠ Ollama client not available (optional feature)[/yellow]\n"
        )
        return False

    console.print(f"[yellow]Testing Ollama connection at {url}...[/yellow]")

    try:
        client = Ollama(host=url)
        # Try to list models (lightweight operation)
        client.list()
        console.print("[green]✓ Ollama connection successful[/green]\n")
        return True
    except Exception as exc:
        console.print(
            f"[yellow]⚠ Ollama not available: {exc}[/yellow]\n"
            "You can set it up later or skip AI features.\n"
        )
        return False


def create_sample_transcript(save_dir: Path) -> None:
    """Create a sample transcript file to demonstrate the format.

    Parameters
    ----------
    save_dir:
        Directory where transcripts are saved.
    """
    try:
        filepath, transcript_id = create_transcript(save_dir)

        # Add sample content
        sample_text = (
            "This is a sample transcript created during setup.\n\n"
            "You can edit this file or delete it. "
            "Future recordings will be saved in the same format."
        )

        from rejoice.transcript.manager import append_to_transcript

        append_to_transcript(filepath, sample_text)

        console.print(f"[green]✓ Sample transcript created: {filepath.name}[/green]\n")
    except Exception as exc:
        logger.warning(f"Failed to create sample transcript: {exc}")
        console.print(
            "[yellow]⚠ Could not create sample transcript (this is okay)[/yellow]\n"
        )


def run_first_setup() -> None:
    """Run the complete first-run setup wizard.

    This function guides the user through:
    1. Welcome message
    2. Microphone setup
    3. Save location selection
    4. Model selection
    5. WhisperX verification
    6. Ollama test (optional)
    7. Sample transcript creation
    8. Config file creation
    """
    console.print(
        Panel.fit(
            "👋 Welcome to Rejoice!\n\n"
            "Let's set up your transcription tool. "
            "This will only take a few minutes.",
            title="Rejoice Setup",
            border_style="green",
        )
    )
    console.print()

    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)

    # Initialize config dict for saving at the end
    config = get_default_config()
    selected_device: str | int = "default"  # Default if user skips

    # Step 1: Choose microphone
    console.print("\n[bold]1️⃣  Setting up microphone...[/bold]")
    if Confirm.ask("Configure microphone now?", default=True):
        # Choose microphone
        selected_device = choose_microphone()

        # Save device to config (will be saved at end)
        config["audio"]["device"] = (
            str(selected_device)
            if isinstance(selected_device, int)
            else selected_device
        )

        console.print(
            "[dim]You can test your microphone later using: "
            "[cyan]rec config mic[/cyan][/dim]\n"
        )
    else:
        console.print(
            "[dim]Skipping microphone setup. You can configure it later.[/dim]\n"
        )

    # Step 2: Save location
    console.print("\n[bold]2️⃣  Setting up save location...[/bold]")
    save_path = setup_save_location()

    # Step 3: Model selection
    console.print("\n[bold]3️⃣  Selecting transcription model...[/bold]")
    model = select_whisper_model()

    # Step 4: Verify WhisperX installation
    console.print("\n[bold]4️⃣  Verifying WhisperX installation...[/bold]")
    if not verify_whisperx_installation():
        console.print(
            "[red]✗ WhisperX is not installed. Please install it and try again.[/red]\n"
        )
        if not Confirm.ask(
            "Continue anyway? (transcription won't work until WhisperX is installed)"
        ):
            console.print("[yellow]Setup cancelled.[/yellow]")
            sys.exit(1)

    # Step 6: Test Ollama (optional)
    console.print("\n[bold]6️⃣  Testing AI features (optional)...[/bold]")
    ollama_ok = test_ollama_connection()
    if not ollama_ok:
        console.print(
            "[dim]You can set up Ollama later if you want AI features.[/dim]\n"
        )

    # Step 7: Create sample transcript
    console.print("\n[bold]7️⃣  Creating sample transcript...[/bold]")
    save_dir = Path(save_path)
    create_sample_transcript(save_dir)

    # Step 8: Save configuration
    console.print("\n[bold]8️⃣  Saving configuration...[/bold]")
    # Config was initialized at the start, now update with user selections
    config["transcription"]["model"] = model
    config["output"]["save_path"] = save_path
    # Audio device was already set in Step 1 if user configured it

    import yaml

    config_file = config_dir / "config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    console.print(f"[green]✓ Configuration saved to {config_file}[/green]\n")

    # Final message
    console.print(
        Panel.fit(
            "✅ Setup complete!\n\n"
            "You're ready to start transcribing. Try:\n"
            "  [cyan]rec[/cyan]  - Start recording\n"
            "  [cyan]rec list[/cyan]  - View your transcripts\n"
            "  [cyan]rec view latest[/cyan]  - View latest transcript",
            title="All Set!",
            border_style="green",
        )
    )
