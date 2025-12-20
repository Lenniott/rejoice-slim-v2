"""Tests for configuration CLI commands."""

from click.testing import CliRunner

from rejoice.cli.commands import main


def test_config_show_displays_configuration(tmp_path, monkeypatch):
    """GIVEN rec config show
    WHEN invoked with valid config
    THEN configuration table is displayed"""
    # Mock config directory
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    runner = CliRunner()
    result = runner.invoke(main, ["config", "show"])

    assert result.exit_code == 0
    assert "Rejoice Configuration" in result.output
    assert "Transcription Model" in result.output
    assert "Save Path" in result.output


def test_config_show_handles_error_gracefully(monkeypatch):
    """GIVEN rec config show
    WHEN config loading fails
    THEN error is displayed and command aborts"""

    def mock_load_config():
        raise Exception("Config error")

    monkeypatch.setattr("rejoice.cli.config_commands.load_config", mock_load_config)

    runner = CliRunner()
    result = runner.invoke(main, ["config", "show"])

    assert result.exit_code != 0
    assert "Error loading config" in result.output


def test_config_path_shows_path_when_file_exists(tmp_path, monkeypatch):
    """GIVEN rec config path
    WHEN config file exists
    THEN path is shown with success indicator"""
    config_dir = tmp_path / ".config" / "rejoice"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "config.yaml"
    config_file.write_text("test: value")

    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))

    runner = CliRunner()
    result = runner.invoke(main, ["config", "path"])

    assert result.exit_code == 0
    assert "Config directory" in result.output
    assert "Config file" in result.output
    assert "✓ Config file exists" in result.output


def test_config_path_shows_warning_when_file_missing(tmp_path, monkeypatch):
    """GIVEN rec config path
    WHEN config file does not exist
    THEN path is shown with warning"""
    config_dir = tmp_path / ".config" / "rejoice"
    config_dir.mkdir(parents=True)

    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))

    runner = CliRunner()
    result = runner.invoke(main, ["config", "path"])

    assert result.exit_code == 0
    assert "Config directory" in result.output
    assert "Config file" in result.output
    assert "⚠ Config file does not exist" in result.output


def test_config_init_creates_file_when_not_exists(tmp_path, monkeypatch):
    """GIVEN rec config init
    WHEN config file does not exist
    THEN config file is created"""
    config_dir = tmp_path / ".config" / "rejoice"

    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))

    runner = CliRunner()
    result = runner.invoke(main, ["config", "init"])

    assert result.exit_code == 0
    config_file = config_dir / "config.yaml"
    assert config_file.exists()
    assert "Configuration file created" in result.output
    assert "transcription:" in config_file.read_text()


def test_config_init_prompts_when_file_exists(tmp_path, monkeypatch):
    """GIVEN rec config init
    WHEN config file exists
    THEN user is prompted to overwrite"""
    config_dir = tmp_path / ".config" / "rejoice"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "config.yaml"
    config_file.write_text("existing: config")

    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))

    runner = CliRunner()
    # Answer 'n' to not overwrite
    result = runner.invoke(main, ["config", "init"], input="n\n")

    assert result.exit_code == 0
    assert "Cancelled" in result.output
    # Original content should still be there
    assert "existing: config" in config_file.read_text()


def test_config_init_overwrites_when_confirmed(tmp_path, monkeypatch):
    """GIVEN rec config init
    WHEN config file exists and user confirms
    THEN config file is overwritten"""
    config_dir = tmp_path / ".config" / "rejoice"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "config.yaml"
    config_file.write_text("existing: config")

    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))

    runner = CliRunner()
    # Answer 'y' to overwrite
    result = runner.invoke(main, ["config", "init"], input="y\n")

    assert result.exit_code == 0
    assert "Configuration file created" in result.output
    # Should have new default content
    content = config_file.read_text()
    assert "transcription:" in content
    assert "existing: config" not in content


def test_config_list_mics_shows_devices(monkeypatch):
    """GIVEN rec config list-mics
    WHEN devices are available
    THEN device table is displayed"""
    fake_devices = [
        {"index": 0, "name": "Built-in Microphone", "is_default": True},
        {"index": 1, "name": "USB Mic", "is_default": False},
    ]

    monkeypatch.setattr(
        "rejoice.cli.config_commands.get_audio_input_devices", lambda: fake_devices
    )

    runner = CliRunner()
    result = runner.invoke(main, ["config", "list-mics"])

    assert result.exit_code == 0
    assert "Audio Input Devices" in result.output
    assert "Built-in Microphone" in result.output
    assert "USB Mic" in result.output
    assert "✓" in result.output  # Default indicator


def test_config_list_mics_shows_warning_when_no_devices(monkeypatch):
    """GIVEN rec config list-mics
    WHEN no devices are available
    THEN warning message is shown"""
    monkeypatch.setattr(
        "rejoice.cli.config_commands.get_audio_input_devices", lambda: []
    )

    runner = CliRunner()
    result = runner.invoke(main, ["config", "list-mics"])

    assert result.exit_code == 0
    assert "No audio input devices found" in result.output


def test_config_list_mics_handles_runtime_error(monkeypatch):
    """GIVEN rec config list-mics
    WHEN get_audio_input_devices raises RuntimeError
    THEN error is displayed and command aborts"""

    def mock_get_devices():
        raise RuntimeError("Audio system error")

    monkeypatch.setattr(
        "rejoice.cli.config_commands.get_audio_input_devices", mock_get_devices
    )

    runner = CliRunner()
    result = runner.invoke(main, ["config", "list-mics"])

    assert result.exit_code != 0
    assert "Audio system error" in result.output


def test_config_list_mics_handles_missing_device_fields(monkeypatch):
    """GIVEN rec config list-mics
    WHEN device dicts have missing fields
    THEN command handles gracefully with defaults"""
    fake_devices = [
        {"index": 0},  # Missing name and is_default
        {"index": 1, "name": "USB Mic"},  # Missing is_default
    ]

    monkeypatch.setattr(
        "rejoice.cli.config_commands.get_audio_input_devices", lambda: fake_devices
    )

    runner = CliRunner()
    result = runner.invoke(main, ["config", "list-mics"])

    assert result.exit_code == 0
    assert "Audio Input Devices" in result.output
    assert "Device 0" in result.output  # Default name when missing
    assert "USB Mic" in result.output


def test_config_mic_chooses_and_saves_device(tmp_path, monkeypatch):
    """GIVEN rec config mic
    WHEN user selects a device
    THEN device is saved to config"""
    from unittest.mock import patch

    config_dir = tmp_path / ".config" / "rejoice"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "config.yaml"
    config_file.write_text("transcription:\n  model: medium\n")

    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))

    with patch(
        "rejoice.cli.config_commands.choose_microphone", return_value=1
    ) as mock_choose:
        with patch("rejoice.cli.config_commands.test_microphone", return_value=True):
            with patch("rich.prompt.Confirm.ask", return_value=True):
                runner = CliRunner()
                result = runner.invoke(main, ["config", "mic"], input="y\n")

                assert result.exit_code == 0
                mock_choose.assert_called_once()
                # Verify device was saved
                import yaml

                config_data = yaml.safe_load(config_file.read_text())
                assert config_data["audio"]["device"] == "1"


def test_config_mic_skips_test_when_user_declines(tmp_path, monkeypatch):
    """GIVEN rec config mic
    WHEN user declines to test
    THEN device is still saved"""
    from unittest.mock import patch

    config_dir = tmp_path / ".config" / "rejoice"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "config.yaml"
    config_file.write_text("transcription:\n  model: medium\n")

    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))

    with patch("rejoice.cli.config_commands.choose_microphone", return_value="default"):
        with patch("rich.prompt.Confirm.ask", return_value=False):
            runner = CliRunner()
            result = runner.invoke(main, ["config", "mic"])

            assert result.exit_code == 0
            # Verify device was saved even without test
            import yaml

            config_data = yaml.safe_load(config_file.read_text())
            assert config_data["audio"]["device"] == "default"


def test_settings_command_opens_menu(tmp_path, monkeypatch):
    """GIVEN rec settings
    WHEN invoked
    THEN interactive menu is displayed"""
    config_dir = tmp_path / ".config" / "rejoice"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "config.yaml"
    config_file.write_text("transcription:\n  model: medium\n")

    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))

    runner = CliRunner()
    # Simulate user selecting "Exit" immediately
    result = runner.invoke(main, ["config", "settings"], input="q\n")

    assert result.exit_code == 0
    assert "Settings" in result.output or "settings" in result.output.lower()


def test_settings_shows_current_values(tmp_path, monkeypatch):
    """GIVEN rec settings
    WHEN viewing a setting category
    THEN current values are displayed"""
    config_dir = tmp_path / ".config" / "rejoice"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "config.yaml"
    config_file.write_text(
        "transcription:\n  model: small\n  language: en\noutput:\n  save_path: ~/test\n"
    )

    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))

    runner = CliRunner()
    # Navigate to transcription settings, then exit
    result = runner.invoke(main, ["config", "settings"], input="1\nq\nq\n")

    assert result.exit_code == 0
    # Should show current model value
    assert "small" in result.output or "Model" in result.output


def test_settings_updates_transcription_model(tmp_path, monkeypatch):
    """GIVEN rec settings
    WHEN updating transcription model
    THEN config file is updated"""
    config_dir = tmp_path / ".config" / "rejoice"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "config.yaml"
    config_file.write_text("transcription:\n  model: medium\n")

    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))

    runner = CliRunner()
    # Navigate: Main menu -> Transcription -> Model -> Enter new value
    # -> No to "change another" -> Back -> Exit
    result = runner.invoke(
        main,
        ["config", "settings"],
        input="1\n1\nlarge\nn\nq\nq\n",
    )

    assert result.exit_code == 0
    # Verify config was updated
    import yaml

    config_data = yaml.safe_load(config_file.read_text())
    assert config_data["transcription"]["model"] == "large"


def test_settings_validates_model_input(tmp_path, monkeypatch):
    """GIVEN rec settings
    WHEN entering invalid model name
    THEN validation error is shown and value is not saved"""
    config_dir = tmp_path / ".config" / "rejoice"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "config.yaml"
    config_file.write_text("transcription:\n  model: medium\n")

    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))

    runner = CliRunner()
    # Try to set invalid model, then exit
    result = runner.invoke(
        main,
        ["config", "settings"],
        input="1\n1\ninvalid_model\nn\n1\nmedium\nn\nq\n",
    )

    assert result.exit_code == 0
    # Should show validation error
    assert "invalid" in result.output.lower() or "valid" in result.output.lower()
    # Original value should remain
    import yaml

    config_data = yaml.safe_load(config_file.read_text())
    assert config_data["transcription"]["model"] == "medium"


def test_settings_updates_save_path(tmp_path, monkeypatch):
    """GIVEN rec settings
    WHEN updating save path
    THEN config file is updated with expanded path"""
    config_dir = tmp_path / ".config" / "rejoice"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "config.yaml"
    config_file.write_text("output:\n  save_path: ~/Documents/transcripts\n")

    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))

    runner = CliRunner()
    new_path = str(tmp_path / "new_transcripts")
    # Navigate: Main menu -> Output -> Save Path -> Enter new path
    # -> No to "change another" -> Back -> Exit
    result = runner.invoke(
        main,
        ["config", "settings"],
        input=f"2\n1\n{new_path}\nn\nq\nq\n",
    )

    assert result.exit_code == 0
    # Verify config was updated
    import yaml

    config_data = yaml.safe_load(config_file.read_text())
    # Path should be saved (may be expanded or as-is depending on implementation)
    assert "new_transcripts" in config_data["output"]["save_path"]


def test_settings_validates_boolean_input(tmp_path, monkeypatch):
    """GIVEN rec settings
    WHEN updating boolean setting
    THEN accepts yes/no or true/false and saves correctly"""
    config_dir = tmp_path / ".config" / "rejoice"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "config.yaml"
    config_file.write_text("output:\n  auto_copy: true\n")

    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))

    runner = CliRunner()
    # Navigate: Main menu -> Output -> Auto Copy -> Toggle -> Exit
    result = runner.invoke(
        main,
        ["config", "settings"],
        input="2\n3\nn\nn\nq\nq\n",
    )

    assert result.exit_code == 0
    # Verify config was updated
    import yaml

    config_data = yaml.safe_load(config_file.read_text())
    assert config_data["output"]["auto_copy"] is False


def test_settings_preserves_other_config_values(tmp_path, monkeypatch):
    """GIVEN rec settings
    WHEN updating one setting
    THEN other config values are preserved"""
    config_dir = tmp_path / ".config" / "rejoice"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "config.yaml"
    original_config = """transcription:
  model: medium
  language: en
output:
  save_path: ~/test
  auto_copy: true
audio:
  device: default
"""
    config_file.write_text(original_config)

    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))

    runner = CliRunner()
    # Only update transcription model
    result = runner.invoke(
        main,
        ["config", "settings"],
        input="1\n1\nsmall\nn\nq\nq\n",
    )

    assert result.exit_code == 0
    # Verify only model changed, other values preserved
    import yaml

    config_data = yaml.safe_load(config_file.read_text())
    assert config_data["transcription"]["model"] == "small"
    assert config_data["transcription"]["language"] == "en"
    assert config_data["output"]["auto_copy"] is True
    assert config_data["audio"]["device"] == "default"
