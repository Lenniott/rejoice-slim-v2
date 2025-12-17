"""Tests for configuration system."""
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from rejoice.core.config import load_config
from rejoice.exceptions import ConfigError


def test_default_config_exists():
    """GIVEN no user config
    WHEN config is loaded
    THEN default config is returned"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / ".config" / "rejoice"
        config_dir.mkdir(parents=True)

        with patch("rejoice.core.config.get_config_dir", return_value=config_dir):
            config = load_config()

            assert config is not None
            assert config.transcription.model == "medium"
            assert config.transcription.language == "auto"
            assert config.transcription.vad_filter is True
            assert config.output.save_path is not None
            assert config.audio.sample_rate == 16000


def test_user_config_overrides_defaults():
    """GIVEN user config file exists
    WHEN config is loaded
    THEN user values override defaults"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / ".config" / "rejoice"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.yaml"

        user_config = {
            "transcription": {"model": "large", "language": "en"},
            "output": {"save_path": "/custom/path"},
        }

        config_file.write_text(yaml.dump(user_config))

        with patch("rejoice.core.config.get_config_dir", return_value=config_dir):
            config = load_config()

            assert config.transcription.model == "large"
            assert config.transcription.language == "en"
            assert config.output.save_path == "/custom/path"
            # Defaults still apply for other fields
            assert config.transcription.vad_filter is True


def test_config_validation_invalid_model():
    """GIVEN config with invalid model
    WHEN config is loaded
    THEN validation error is raised"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / ".config" / "rejoice"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.yaml"

        invalid_config = {"transcription": {"model": "invalid_model"}}

        config_file.write_text(yaml.dump(invalid_config))

        with patch("rejoice.core.config.get_config_dir", return_value=config_dir):
            with pytest.raises(ConfigError, match="Invalid model"):
                load_config()


def test_config_validation_invalid_sample_rate():
    """GIVEN config with invalid sample rate
    WHEN config is loaded
    THEN validation error is raised"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / ".config" / "rejoice"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.yaml"

        invalid_config = {"audio": {"sample_rate": 8000}}  # Must be 16000 for Whisper

        config_file.write_text(yaml.dump(invalid_config))

        with patch("rejoice.core.config.get_config_dir", return_value=config_dir):
            with pytest.raises(ConfigError, match="sample_rate"):
                load_config()


def test_env_variables_override_config():
    """GIVEN environment variables set
    WHEN config is loaded
    THEN env vars override config file"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / ".config" / "rejoice"
        config_dir.mkdir(parents=True)

        with patch("rejoice.core.config.get_config_dir", return_value=config_dir):
            with patch.dict(
                os.environ,
                {
                    "REJOICE_TRANSCRIPTION_MODEL": "small",
                    "REJOICE_OUTPUT_SAVE_PATH": "/env/path",
                },
            ):
                config = load_config()

                assert config.transcription.model == "small"
                assert config.output.save_path == "/env/path"


def test_config_path_expansion():
    """GIVEN config with ~ in path
    WHEN config is loaded
    THEN ~ is expanded to home directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / ".config" / "rejoice"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.yaml"

        user_config = {"output": {"save_path": "~/Documents/transcripts"}}

        config_file.write_text(yaml.dump(user_config))

        with patch("rejoice.core.config.get_config_dir", return_value=config_dir):
            config = load_config()

            assert config.output.save_path.startswith("/")
            assert config.output.save_path.endswith("Documents/transcripts")
            assert "~" not in config.output.save_path


def test_config_creates_directory_if_missing():
    """GIVEN config directory doesn't exist
    WHEN config is loaded
    THEN directory is created"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / ".config" / "rejoice"

        with patch("rejoice.core.config.get_config_dir", return_value=config_dir):
            config = load_config()

            assert config_dir.exists()
            assert config is not None


def test_config_merges_partial_overrides():
    """GIVEN user config with partial transcription settings
    WHEN config is loaded
    THEN only specified fields are overridden"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / ".config" / "rejoice"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.yaml"

        # Only override model, not language or vad_filter
        user_config = {"transcription": {"model": "small"}}

        config_file.write_text(yaml.dump(user_config))

        with patch("rejoice.core.config.get_config_dir", return_value=config_dir):
            config = load_config()

            assert config.transcription.model == "small"
            # Defaults still apply
            assert config.transcription.language == "auto"
            assert config.transcription.vad_filter is True
