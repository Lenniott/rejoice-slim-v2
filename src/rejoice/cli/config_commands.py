"""Configuration CLI commands."""

import click
from rich.console import Console
from rich.table import Table

import yaml

from rejoice.audio import get_audio_input_devices
from rejoice.core.config import get_config_dir, get_default_config, load_config
from rejoice.setup import choose_microphone, test_microphone

console = Console()


@click.group()
def config_group():
    """Manage configuration settings."""
    pass


@config_group.command()
def show():
    """Show current configuration."""
    try:
        config = load_config()
        config_dir = get_config_dir()

        table = Table(
            title="Rejoice Configuration", show_header=True, header_style="bold"
        )
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")

        # Transcription
        table.add_row("Transcription Model", config.transcription.model)
        table.add_row("Language", config.transcription.language)
        table.add_row("VAD Filter", str(config.transcription.vad_filter))

        # Output
        table.add_row("Save Path", config.output.save_path)
        table.add_row("Auto Analyze", str(config.output.auto_analyze))
        table.add_row("Auto Copy", str(config.output.auto_copy))

        # Audio
        table.add_row("Audio Device", config.audio.device)
        table.add_row("Sample Rate", str(config.audio.sample_rate))

        # AI
        table.add_row("Ollama URL", config.ai.ollama_url)
        table.add_row("AI Model", config.ai.model)

        console.print(table)
        console.print(f"\n📁 Config directory: {config_dir}")
        console.print(f"📄 Config file: {config_dir / 'config.yaml'}")

    except Exception as e:  # pragma: no cover - defensive, surfaced via click
        console.print(f"[red]Error loading config: {e}[/red]")
        raise click.Abort()


@config_group.command()
def path():
    """Show configuration file path."""
    config_dir = get_config_dir()
    config_file = config_dir / "config.yaml"

    console.print(f"📁 Config directory: {config_dir}")
    console.print(f"📄 Config file: {config_file}")

    if config_file.exists():
        console.print("[green]✓ Config file exists[/green]")
    else:
        console.print("[yellow]⚠ Config file does not exist (using defaults)[/yellow]")


@config_group.command()
def init():
    """Initialize configuration file with defaults."""
    config_dir = get_config_dir()
    config_file = config_dir / "config.yaml"

    if config_file.exists():
        if not click.confirm("Config file already exists. Overwrite?"):
            console.print("[yellow]Cancelled[/yellow]")
            return

    config_dir.mkdir(parents=True, exist_ok=True)

    # Write default config
    default_config = """# Rejoice Configuration
# Edit this file to customize Rejoice settings

transcription:
  model: medium  # tiny, base, small, medium, large
  language: auto  # auto-detect or language code (en, es, fr, etc.)
  vad_filter: true  # Voice Activity Detection

output:
  save_path: ~/Documents/transcripts  # Where to save transcripts
  template: default
  auto_analyze: true  # Automatically analyze after recording
  auto_copy: true  # Automatically copy transcript to clipboard

audio:
  device: default  # Audio input device
  sample_rate: 16000  # Must be 16000 for Whisper

ai:
  ollama_url: http://localhost:11434
  model: llama2
  prompts_path: ~/.config/rejoice/prompts/
"""

    config_file.write_text(default_config)
    console.print(f"[green]✓ Configuration file created: {config_file}[/green]")
    console.print("[dim]Edit this file to customize your settings[/dim]")


@config_group.command("list-mics")
def list_mics() -> None:
    """List available audio input devices.

    This command helps users discover which microphones Rejoice can use.
    It corresponds to the backlog story [R-001] Audio Device Detection.
    """

    try:
        devices = get_audio_input_devices()
    except RuntimeError as exc:
        console.print(f"[red]{exc}[/red]")
        raise click.Abort()

    if not devices:
        console.print("[yellow]No audio input devices found.[/yellow]")
        console.print(
            "[dim]Check your system audio settings and ensure a microphone is "
            "connected.[/dim]"
        )
        return

    table = Table(title="Audio Input Devices", show_header=True, header_style="bold")
    table.add_column("Index", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Default", style="magenta")

    for dev in devices:
        index = dev.get("index")
        name = dev.get("name", f"Device {index}")
        is_default = dev.get("is_default", False)
        default_label = "✓" if is_default else ""
        table.add_row(str(index), name, default_label)

    console.print(table)
    console.print(
        "\nUse the device index or name in your config.yaml under the "
        "'audio.device' setting."
    )


@config_group.command("mic")
def mic():
    """Configure microphone selection and test it."""
    from rich.prompt import Confirm

    try:
        # Choose microphone
        selected_device = choose_microphone()

        # Test microphone
        if Confirm.ask("Test this microphone?", default=True):
            mic_ok = test_microphone(device=selected_device)
            if not mic_ok:
                console.print(
                    "[yellow]⚠ Microphone test had issues, "
                    "but configuration was saved.[/yellow]"
                )

        # Save to config
        config_dir = get_config_dir()
        config_file = config_dir / "config.yaml"
        config_dir.mkdir(parents=True, exist_ok=True)

        # Load existing config or use defaults
        if config_file.exists():
            with open(config_file, "r") as f:
                config_data = yaml.safe_load(f) or {}
        else:
            config_data = get_default_config()

        # Update audio device
        if "audio" not in config_data:
            config_data["audio"] = {}
        config_data["audio"]["device"] = (
            str(selected_device)
            if isinstance(selected_device, int)
            else selected_device
        )

        # Save config
        with open(config_file, "w") as f:
            yaml.dump(config_data, f, default_flow_style=False)

        device_display = (
            f"Device {selected_device}"
            if isinstance(selected_device, int)
            else "System default"
        )
        console.print(f"[green]✓ Microphone configured: {device_display}[/green]")
        console.print(f"[dim]Configuration saved to {config_file}[/dim]")

    except Exception as e:
        console.print(f"[red]Error configuring microphone: {e}[/red]")
        raise click.Abort()
