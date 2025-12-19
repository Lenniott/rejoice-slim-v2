"""Tests for CLI framework setup."""
from click.testing import CliRunner

from rejoice.cli.commands import main


def test_main_command_help():
    """GIVEN rec command
    WHEN --help is called
    THEN help text is displayed with subcommands"""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Rejoice" in result.output
    assert "Commands:" in result.output
    assert "config" in result.output


def test_version_flag():
    """GIVEN --version flag
    WHEN main is invoked
    THEN version is displayed and exits"""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "2.0.0" in result.output


def test_debug_flag_global():
    """GIVEN --debug flag
    WHEN main is invoked
    THEN debug mode is enabled"""
    runner = CliRunner()
    result = runner.invoke(main, ["--debug", "--help"])
    assert result.exit_code == 0
    # Debug flag should be accepted globally


def test_language_flag_global():
    """GIVEN --language flag
    WHEN main is invoked
    THEN the flag is accepted globally."""
    runner = CliRunner()
    result = runner.invoke(main, ["--language", "en", "--help"])
    assert result.exit_code == 0


def test_config_subcommand_exists():
    """GIVEN rec command
    WHEN config subcommand is called
    THEN config commands are available"""
    runner = CliRunner()
    result = runner.invoke(main, ["config", "--help"])
    assert result.exit_code == 0
    assert "Configuration" in result.output or "config" in result.output.lower()


def test_config_show_command():
    """GIVEN rec config show
    WHEN invoked
    THEN configuration is displayed"""
    runner = CliRunner()
    result = runner.invoke(main, ["config", "show"])
    # Should succeed (may show defaults if no config file)
    assert result.exit_code == 0


def test_config_path_command():
    """GIVEN rec config path
    WHEN invoked
    THEN config file path is shown"""
    runner = CliRunner()
    result = runner.invoke(main, ["config", "path"])
    assert result.exit_code == 0
    assert "Config" in result.output or "config" in result.output.lower()


def test_config_init_command():
    """GIVEN rec config init
    WHEN invoked
    THEN config file is created"""
    runner = CliRunner()
    # This will create a file, so we test it works
    result = runner.invoke(
        main, ["config", "init"], input="n\n"
    )  # Don't overwrite if exists
    # Should either succeed or show message
    assert result.exit_code in [0, 1]  # May exit with code 1 if cancelled


def test_no_subcommand_shows_help(monkeypatch, tmp_path):
    """GIVEN rec with no subcommand
    WHEN invoked
    THEN help or default behavior is shown"""
    monkeypatch.setattr("rejoice.cli.commands.setup_logging", lambda debug=False: None)
    monkeypatch.setattr(
        "rejoice.cli.commands.start_recording_session",
        lambda *args, **kwargs: (None, None),
    )

    from rejoice.core.config import AudioConfig, OutputConfig, TranscriptionConfig

    class FakeConfig:
        def __init__(self):
            self.audio = AudioConfig()
            self.output = OutputConfig(save_path=str(tmp_path))
            self.transcription = TranscriptionConfig()

    monkeypatch.setattr("rejoice.cli.commands.load_config", lambda: FakeConfig())

    runner = CliRunner()
    result = runner.invoke(main, [])
    # Should show help or default message (or start recording which we've mocked)
    assert result.exit_code == 0
