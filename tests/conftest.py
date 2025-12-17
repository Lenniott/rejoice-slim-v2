"""Pytest configuration and shared fixtures."""
import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def tmp_dir():
    """Create a temporary directory for tests."""
    tmp = tempfile.mkdtemp()
    yield Path(tmp)
    shutil.rmtree(tmp)


@pytest.fixture
def sample_audio_dir(tmp_dir):
    """Create a directory with sample audio files for testing."""
    audio_dir = tmp_dir / "audio"
    audio_dir.mkdir()
    return audio_dir


@pytest.fixture
def config_dir(tmp_dir):
    """Create a temporary config directory."""
    config_dir = tmp_dir / ".rejoice" / "config"
    config_dir.mkdir(parents=True)
    return config_dir

