"""Configuration system for Rejoice."""
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv

from rejoice.exceptions import ConfigError


@dataclass
class TranscriptionConfig:
    """Transcription settings."""

    model: str = "medium"
    language: str = "auto"
    vad_filter: bool = True


@dataclass
class OutputConfig:
    """Output settings."""

    save_path: str = "~/Documents/transcripts"
    template: str = "default"
    auto_analyze: bool = True
    auto_copy: bool = True


@dataclass
class AudioConfig:
    """Audio settings."""

    device: str = "default"
    sample_rate: int = 16000


@dataclass
class AIConfig:
    """AI settings."""

    ollama_url: str = "http://localhost:11434"
    model: str = "qwen3:4b"
    prompts_path: str = "~/.config/rejoice/prompts/"


@dataclass
class Config:
    """Main configuration object."""

    transcription: TranscriptionConfig = field(default_factory=TranscriptionConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    ai: AIConfig = field(default_factory=AIConfig)

    def validate(self) -> None:
        """Validate configuration values."""
        # Validate model
        valid_models = ["tiny", "base", "small", "medium", "large"]
        if self.transcription.model not in valid_models:
            raise ConfigError(
                f"Invalid model: {self.transcription.model}. "
                f"Must be one of: {', '.join(valid_models)}"
            )

        # Validate sample rate (Whisper requires 16kHz)
        if self.audio.sample_rate != 16000:
            raise ConfigError(
                f"Invalid sample_rate: {self.audio.sample_rate}. "
                "Must be 16000 for Whisper compatibility."
            )

        # Expand paths
        self.output.save_path = str(Path(self.output.save_path).expanduser())
        self.ai.prompts_path = str(Path(self.ai.prompts_path).expanduser())


def get_config_dir() -> Path:
    """Get the configuration directory."""
    config_home = os.getenv("XDG_CONFIG_HOME")
    if config_home:
        return Path(config_home) / "rejoice"
    return Path.home() / ".config" / "rejoice"


def get_default_config() -> Dict[str, Any]:
    """Get default configuration as dictionary."""
    return {
        "transcription": {
            "model": "medium",
            "language": "auto",
            "vad_filter": True,
        },
        "output": {
            "save_path": "~/Documents/transcripts",
            "template": "default",
            "auto_analyze": True,
            "auto_copy": True,
        },
        "audio": {
            "device": "default",
            "sample_rate": 16000,
        },
        "ai": {
            "ollama_url": "http://localhost:11434",
            "model": "qwen3:4b",
            "prompts_path": "~/.config/rejoice/prompts/",
        },
    }


def load_config_file(config_dir: Path) -> Optional[Dict[str, Any]]:
    """Load user configuration file if it exists."""
    config_file = config_dir / "config.yaml"
    if not config_file.exists():
        return None

    try:
        with open(config_file, "r") as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise ConfigError(f"Invalid YAML in config file: {e}")


def load_env_overrides() -> Dict[str, Any]:
    """Load configuration from environment variables."""
    # Load .env file if it exists
    config_dir = get_config_dir()
    env_file = config_dir / ".env"
    if env_file.exists():
        load_dotenv(env_file)

    overrides: Dict[str, Any] = {}

    # Map environment variables to config structure
    env_mappings = {
        "REJOICE_TRANSCRIPTION_MODEL": ("transcription", "model"),
        "REJOICE_TRANSCRIPTION_LANGUAGE": ("transcription", "language"),
        "REJOICE_TRANSCRIPTION_VAD_FILTER": ("transcription", "vad_filter"),
        "REJOICE_OUTPUT_SAVE_PATH": ("output", "save_path"),
        "REJOICE_OUTPUT_TEMPLATE": ("output", "template"),
        "REJOICE_OUTPUT_AUTO_ANALYZE": ("output", "auto_analyze"),
        "REJOICE_OUTPUT_AUTO_COPY": ("output", "auto_copy"),
        "REJOICE_AUDIO_DEVICE": ("audio", "device"),
        "REJOICE_AUDIO_SAMPLE_RATE": ("audio", "sample_rate"),
        "REJOICE_AI_OLLAMA_URL": ("ai", "ollama_url"),
        "REJOICE_AI_MODEL": ("ai", "model"),
        "REJOICE_AI_PROMPTS_PATH": ("ai", "prompts_path"),
    }

    for env_var, (section, key) in env_mappings.items():
        value = os.getenv(env_var)
        if value is not None:
            if section not in overrides:
                overrides[section] = {}

            # Convert string booleans and integers
            converted_value: Any
            if value.lower() in ("true", "false"):
                converted_value = value.lower() == "true"
            elif value.isdigit():
                converted_value = int(value)
            else:
                converted_value = value

            overrides[section][key] = converted_value

    return overrides


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries."""
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def dict_to_config(data: Dict[str, Any]) -> Config:
    """Convert dictionary to Config object."""
    transcription = TranscriptionConfig(**data.get("transcription", {}))
    output = OutputConfig(**data.get("output", {}))
    audio = AudioConfig(**data.get("audio", {}))
    ai = AIConfig(**data.get("ai", {}))

    return Config(
        transcription=transcription,
        output=output,
        audio=audio,
        ai=ai,
    )


def load_config() -> Config:
    """Load configuration with hierarchy: defaults -> user config -> env vars."""
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)

    # Start with defaults
    config_dict = get_default_config()

    # Merge user config file
    user_config = load_config_file(config_dir)
    if user_config:
        config_dict = deep_merge(config_dict, user_config)

    # Merge environment variable overrides
    env_overrides = load_env_overrides()
    if env_overrides:
        config_dict = deep_merge(config_dict, env_overrides)

    # Convert to Config object
    config = dict_to_config(config_dict)

    # Validate
    config.validate()

    return config
