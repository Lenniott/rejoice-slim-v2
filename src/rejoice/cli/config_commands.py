"""Configuration CLI commands."""

import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

import yaml

from rejoice.audio import get_audio_input_devices
from rejoice.core.config import get_config_dir, get_default_config, load_config
from rejoice.setup import choose_microphone, test_microphone

console = Console()


def _safe_clear():
    """Safely clear console, handling non-TTY environments (like tests)."""
    try:
        if console.is_terminal:
            console.clear()
    except Exception:
        # Ignore errors when clearing console in non-interactive environments
        pass


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


def _save_config(config_data: dict) -> None:
    """Save configuration data to config.yaml file."""
    config_dir = get_config_dir()
    config_file = config_dir / "config.yaml"
    config_dir.mkdir(parents=True, exist_ok=True)

    with open(config_file, "w") as f:
        yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)

    console.print(f"[green]✓ Configuration saved to {config_file}[/green]")


def _load_config_data() -> dict:
    """Load configuration data from file or return defaults."""
    config_dir = get_config_dir()
    config_file = config_dir / "config.yaml"

    if config_file.exists():
        with open(config_file, "r") as f:
            return yaml.safe_load(f) or {}
    return get_default_config()


def _show_main_menu() -> str:
    """Display main settings menu and return user choice."""
    _safe_clear()
    console.print(Panel.fit("[bold cyan]Rejoice Settings Menu[/bold cyan]"))
    console.print("\n[bold]Select a category:[/bold]")
    console.print("  1. Transcription Settings")
    console.print("  2. Output Settings")
    console.print("  3. Audio Settings")
    console.print("  4. AI Settings")
    console.print("  q. Quit")
    console.print()

    choice = Prompt.ask("Choice", default="q").strip().lower()
    return str(choice)


def _show_transcription_settings(config_data: dict) -> dict:
    """Interactive transcription settings editor."""
    while True:
        config = load_config()
        _safe_clear()
        console.print(Panel.fit("[bold cyan]Transcription Settings[/bold cyan]"))
        console.print("\n[bold]Current values:[/bold]")
        console.print(f"  Model: [green]{config.transcription.model}[/green]")
        console.print(f"  Language: [green]{config.transcription.language}[/green]")
        console.print(f"  VAD Filter: [green]{config.transcription.vad_filter}[/green]")
        console.print("\n[bold]What would you like to change?[/bold]")
        console.print("  1. Model")
        console.print("  2. Language")
        console.print("  3. VAD Filter")
        console.print("  q. Back to main menu")
        console.print()

        choice = Prompt.ask("Choice", default="q").strip().lower()

        if choice == "1":
            valid_models = ["tiny", "base", "small", "medium", "large"]
            console.print(f"\n[dim]Valid models: {', '.join(valid_models)}[/dim]")
            new_model = (
                Prompt.ask("Transcription model", default=config.transcription.model)
                .strip()
                .lower()
            )

            if new_model not in valid_models:
                console.print(
                    f"[red]Invalid model: {new_model}. "
                    f"Must be one of: {', '.join(valid_models)}[/red]"
                )
                if not Confirm.ask("Try again?", default=True):
                    continue
            else:
                if "transcription" not in config_data:
                    config_data["transcription"] = {}
                config_data["transcription"]["model"] = new_model
                _save_config(config_data)
                console.print(f"[green]✓ Model updated to {new_model}[/green]")
                if not Confirm.ask("Change another setting?", default=False):
                    break

        elif choice == "2":
            new_language = (
                Prompt.ask(
                    "Language (auto or language code like 'en', 'es', 'fr')",
                    default=config.transcription.language,
                )
                .strip()
                .lower()
            )

            if "transcription" not in config_data:
                config_data["transcription"] = {}
            config_data["transcription"]["language"] = new_language
            _save_config(config_data)
            console.print(f"[green]✓ Language updated to {new_language}[/green]")
            if not Confirm.ask("Change another setting?", default=False):
                break

        elif choice == "3":
            current_vad = config.transcription.vad_filter
            new_vad = Confirm.ask("Enable VAD Filter?", default=current_vad)

            if "transcription" not in config_data:
                config_data["transcription"] = {}
            config_data["transcription"]["vad_filter"] = new_vad
            _save_config(config_data)
            console.print(
                f"[green]✓ VAD Filter {'enabled' if new_vad else 'disabled'}[/green]"
            )
            if not Confirm.ask("Change another setting?", default=False):
                break

        elif choice == "q":
            break
        else:
            console.print("[yellow]Invalid choice[/yellow]")

    return config_data


def _show_output_settings(config_data: dict) -> dict:
    """Interactive output settings editor."""
    while True:
        config = load_config()
        _safe_clear()
        console.print(Panel.fit("[bold cyan]Output Settings[/bold cyan]"))
        console.print("\n[bold]Current values:[/bold]")
        console.print(f"  Save Path: [green]{config.output.save_path}[/green]")
        console.print(f"  Auto Analyze: [green]{config.output.auto_analyze}[/green]")
        console.print(f"  Auto Copy: [green]{config.output.auto_copy}[/green]")
        console.print("\n[bold]What would you like to change?[/bold]")
        console.print("  1. Save Path")
        console.print("  2. Auto Analyze")
        console.print("  3. Auto Copy")
        console.print("  q. Back to main menu")
        console.print()

        choice = Prompt.ask("Choice", default="q").strip().lower()

        if choice == "1":
            new_path = Prompt.ask("Save path", default=config.output.save_path).strip()

            # Expand user home directory
            expanded_path = str(Path(new_path).expanduser())

            if "output" not in config_data:
                config_data["output"] = {}
            config_data["output"]["save_path"] = expanded_path
            _save_config(config_data)
            console.print(f"[green]✓ Save path updated to {expanded_path}[/green]")
            if not Confirm.ask("Change another setting?", default=False):
                break

        elif choice == "2":
            current_auto_analyze = config.output.auto_analyze
            new_auto_analyze = Confirm.ask(
                "Enable Auto Analyze?", default=current_auto_analyze
            )

            if "output" not in config_data:
                config_data["output"] = {}
            config_data["output"]["auto_analyze"] = new_auto_analyze
            _save_config(config_data)
            status = "enabled" if new_auto_analyze else "disabled"
            console.print(f"[green]✓ Auto Analyze {status}[/green]")
            if not Confirm.ask("Change another setting?", default=False):
                break

        elif choice == "3":
            current_auto_copy = config.output.auto_copy
            new_auto_copy = Confirm.ask("Enable Auto Copy?", default=current_auto_copy)

            if "output" not in config_data:
                config_data["output"] = {}
            config_data["output"]["auto_copy"] = new_auto_copy
            _save_config(config_data)
            status = "enabled" if new_auto_copy else "disabled"
            console.print(f"[green]✓ Auto Copy {status}[/green]")
            if not Confirm.ask("Change another setting?", default=False):
                break

        elif choice == "q":
            break
        else:
            console.print("[yellow]Invalid choice[/yellow]")

    return config_data


def _show_audio_settings(config_data: dict) -> dict:
    """Interactive audio settings editor."""
    while True:
        config = load_config()
        _safe_clear()
        console.print(Panel.fit("[bold cyan]Audio Settings[/bold cyan]"))
        console.print("\n[bold]Current values:[/bold]")
        console.print(f"  Device: [green]{config.audio.device}[/green]")
        console.print(f"  Sample Rate: [green]{config.audio.sample_rate}[/green]")
        console.print("\n[bold]What would you like to change?[/bold]")
        console.print("  1. Device (use 'rec config mic' for interactive selection)")
        console.print("  2. Sample Rate")
        console.print("  q. Back to main menu")
        console.print()

        choice = Prompt.ask("Choice", default="q").strip().lower()

        if choice == "1":
            console.print(
                "[yellow]For interactive microphone selection, "
                "use 'rec config mic' command[/yellow]"
            )
            new_device = Prompt.ask(
                "Audio device (device index or 'default')",
                default=str(config.audio.device),
            ).strip()

            if "audio" not in config_data:
                config_data["audio"] = {}
            # Try to convert to int if it's a number, otherwise keep as string
            try:
                config_data["audio"]["device"] = int(new_device)
            except ValueError:
                config_data["audio"]["device"] = new_device
            _save_config(config_data)
            console.print(
                f"[green]✓ Device updated to {config_data['audio']['device']}[/green]"
            )
            if not Confirm.ask("Change another setting?", default=False):
                break

        elif choice == "2":
            console.print(
                "[yellow]Sample rate must be 16000 for Whisper compatibility[/yellow]"
            )
            new_rate = Prompt.ask(
                "Sample rate", default=str(config.audio.sample_rate)
            ).strip()

            try:
                rate_int = int(new_rate)
                if rate_int != 16000:
                    console.print(
                        "[yellow]Warning: Whisper requires 16000 Hz. "
                        "Other values may cause issues.[/yellow]"
                    )
                    if not Confirm.ask("Continue anyway?", default=False):
                        continue
                if "audio" not in config_data:
                    config_data["audio"] = {}
                config_data["audio"]["sample_rate"] = rate_int
                _save_config(config_data)
                console.print(f"[green]✓ Sample rate updated to {rate_int}[/green]")
                if not Confirm.ask("Change another setting?", default=False):
                    break
            except ValueError:
                console.print("[red]Invalid sample rate. Must be a number.[/red]")
                if not Confirm.ask("Try again?", default=True):
                    break

        elif choice == "q":
            break
        else:
            console.print("[yellow]Invalid choice[/yellow]")

    return config_data


def _show_ai_settings(config_data: dict) -> dict:
    """Interactive AI settings editor."""
    while True:
        config = load_config()
        _safe_clear()
        console.print(Panel.fit("[bold cyan]AI Settings[/bold cyan]"))
        console.print("\n[bold]Current values:[/bold]")
        console.print(f"  Ollama URL: [green]{config.ai.ollama_url}[/green]")
        console.print(f"  Model: [green]{config.ai.model}[/green]")
        console.print(f"  Prompts Path: [green]{config.ai.prompts_path}[/green]")
        console.print("\n[bold]What would you like to change?[/bold]")
        console.print("  1. Ollama URL")
        console.print("  2. Model")
        console.print("  3. Prompts Path")
        console.print("  q. Back to main menu")
        console.print()

        choice = Prompt.ask("Choice", default="q").strip().lower()

        if choice == "1":
            new_url = Prompt.ask("Ollama URL", default=config.ai.ollama_url).strip()

            if "ai" not in config_data:
                config_data["ai"] = {}
            config_data["ai"]["ollama_url"] = new_url
            _save_config(config_data)
            console.print(f"[green]✓ Ollama URL updated to {new_url}[/green]")
            if not Confirm.ask("Change another setting?", default=False):
                break

        elif choice == "2":
            new_model = Prompt.ask("AI Model", default=config.ai.model).strip()

            if "ai" not in config_data:
                config_data["ai"] = {}
            config_data["ai"]["model"] = new_model
            _save_config(config_data)
            console.print(f"[green]✓ AI Model updated to {new_model}[/green]")
            if not Confirm.ask("Change another setting?", default=False):
                break

        elif choice == "3":
            new_path = Prompt.ask(
                "Prompts Path", default=config.ai.prompts_path
            ).strip()

            # Expand user home directory
            expanded_path = str(Path(new_path).expanduser())

            if "ai" not in config_data:
                config_data["ai"] = {}
            config_data["ai"]["prompts_path"] = expanded_path
            _save_config(config_data)
            console.print(f"[green]✓ Prompts Path updated to {expanded_path}[/green]")
            if not Confirm.ask("Change another setting?", default=False):
                break

        elif choice == "q":
            break
        else:
            console.print("[yellow]Invalid choice[/yellow]")

    return config_data


@config_group.command()
def settings():
    """Open interactive settings menu.

    This command provides a friendly interface for editing configuration
    without manually editing config files.
    It implements [S-001] Interactive Settings Menu.
    """
    try:
        config_data = _load_config_data()

        while True:
            choice = _show_main_menu()

            if choice == "1":
                config_data = _show_transcription_settings(config_data)
            elif choice == "2":
                config_data = _show_output_settings(config_data)
            elif choice == "3":
                config_data = _show_audio_settings(config_data)
            elif choice == "4":
                config_data = _show_ai_settings(config_data)
            elif choice == "q":
                console.print("\n[green]Settings menu closed.[/green]")
                break
            else:
                console.print(
                    "[yellow]Invalid choice. Please select 1-4 or 'q' to quit.[/yellow]"
                )
                if not Confirm.ask("Continue?", default=True):
                    break

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Settings menu cancelled.[/yellow]")
    except Exception as e:  # pragma: no cover - defensive error handling
        console.print(f"[red]Error in settings menu: {e}[/red]")
        raise click.Abort()
