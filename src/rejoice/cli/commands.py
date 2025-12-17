"""CLI commands for Rejoice."""
import click
from rich.console import Console
from rejoice import __version__
from rejoice.cli.config_commands import config_group
from rejoice.core.logging import setup_logging

console = Console()


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

    # If no subcommand, show help or start recording (to be implemented)
    if ctx.invoked_subcommand is None:
        console.print("🎙️  Recording... (not implemented yet)")


# Add config subcommand group
main.add_command(config_group, name="config")


if __name__ == "__main__":
    main()
