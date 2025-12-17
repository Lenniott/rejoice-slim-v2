"""CLI commands for Rejoice."""
import click
from rich.console import Console
from rejoice import __version__

console = Console()


@click.command()
@click.option("--version", is_flag=True, help="Show version and exit")
@click.option("--debug", is_flag=True, help="Enable debug mode")
def main(version, debug):
    """Rejoice - Local voice transcription tool.
    
    Run 'rec' to start recording.
    Press Enter to stop.
    """
    if version:
        console.print(f"Rejoice v{__version__}")
        return
    
    if debug:
        console.print("[yellow]Debug mode enabled[/yellow]")
    
    console.print("🎙️  Recording... (not implemented yet)")


if __name__ == "__main__":
    main()

