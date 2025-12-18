"""Tests for CLI commands."""
from click.testing import CliRunner
from rejoice.cli.commands import main


def test_cli_help():
    """GIVEN rec command
    WHEN --help is called
    THEN help text is displayed"""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Rejoice" in result.output
    assert "rec" in result.output.lower() or "recording" in result.output.lower()


def test_cli_version():
    """GIVEN --version flag
    WHEN main is invoked
    THEN version is displayed"""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "2.0.0" in result.output


def test_cli_debug_flag():
    """GIVEN --debug flag
    WHEN main is invoked
    THEN debug mode is enabled"""
    runner = CliRunner()
    result = runner.invoke(main, ["--debug"])
    assert result.exit_code == 0
    assert "Debug mode enabled" in result.output or "debug" in result.output.lower()
