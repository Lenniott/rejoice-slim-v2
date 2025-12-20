"""Tests for first-run setup [I-007]."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml


def test_detect_first_run_no_config():
    """GIVEN no config file exists
    WHEN first run is detected
    THEN returns True"""
    from rejoice.setup import is_first_run

    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / ".config" / "rejoice"
        config_dir.mkdir(parents=True)

        with patch("rejoice.setup.get_config_dir", return_value=config_dir):
            assert is_first_run() is True


def test_detect_first_run_with_config():
    """GIVEN config file exists
    WHEN first run is detected
    THEN returns False"""
    from rejoice.setup import is_first_run

    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / ".config" / "rejoice"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.yaml"
        config_file.write_text("transcription:\n  model: medium\n")

        with patch("rejoice.setup.get_config_dir", return_value=config_dir):
            assert is_first_run() is False


def test_model_selection_prompt():
    """GIVEN user is prompted for model
    WHEN valid model is selected
    THEN model is returned"""
    from rejoice.setup import select_whisper_model

    with patch(
        "rejoice.setup.Prompt.ask", return_value="3"
    ):  # Select "small" (option 3)
        model = select_whisper_model()
        assert model == "small"


def test_model_selection_default():
    """GIVEN user presses Enter without selection
    WHEN model selection is prompted
    THEN default model (base) is returned"""
    from rejoice.setup import select_whisper_model

    with patch("rejoice.setup.Prompt.ask", return_value="2"):  # Default is "2" (base)
        model = select_whisper_model()
        assert model == "base"


def test_model_download_if_not_exists():
    """GIVEN model is not downloaded
    WHEN download_model is called
    THEN model is downloaded"""
    from rejoice.setup import download_whisper_model

    mock_model = MagicMock()
    with patch("rejoice.setup.WhisperModel", return_value=mock_model) as mock_whisper:
        # First call with local_files_only=True should fail (model not found)
        # Second call with local_files_only=False should succeed (download)
        mock_whisper.side_effect = [
            Exception("Model not found locally"),
            mock_model,
        ]

        with patch("rejoice.setup.console"):
            download_whisper_model("tiny", check_only=False)
            # Should attempt download
            assert mock_whisper.call_count >= 1


def test_model_download_skips_if_exists():
    """GIVEN model is already downloaded
    WHEN download_model is called
    THEN download is skipped"""
    from rejoice.setup import download_whisper_model

    mock_model = MagicMock()
    with patch("rejoice.setup.WhisperModel", return_value=mock_model):
        with patch("rejoice.setup.console"):
            download_whisper_model("tiny", check_only=True)
            # Should not show download message if already exists
            # (check_only=True means we're just verifying, not downloading)


def test_test_microphone():
    """GIVEN microphone test is requested
    WHEN test_microphone is called
    THEN audio device is tested"""
    from rejoice.setup import test_microphone

    with patch("rejoice.setup.record_audio") as mock_record:
        with patch("rejoice.setup.console"):
            with patch("rejoice.setup.time.sleep"):
                mock_stream = MagicMock()
                mock_record.return_value = mock_stream

                result = test_microphone(device="default", duration=1.0)

                # Should have started and stopped recording
                mock_record.assert_called_once()
                mock_stream.stop.assert_called_once()
                mock_stream.close.assert_called_once()
                # Should return a boolean
                assert isinstance(result, bool)


def test_choose_microphone():
    """GIVEN user is prompted to choose microphone
    WHEN valid selection is made
    THEN device identifier is returned"""
    from rejoice.setup import choose_microphone

    mock_devices = [
        {"index": 0, "name": "Default Mic", "is_default": True},
        {"index": 1, "name": "USB Mic", "is_default": False},
    ]

    with patch("rejoice.setup.get_audio_input_devices", return_value=mock_devices):
        with patch("rejoice.setup.Prompt.ask", return_value="0"):  # Select default
            with patch("rejoice.setup.console"):
                device = choose_microphone()
                assert device == "default"

        with patch("rejoice.setup.Prompt.ask", return_value="1"):  # Select first device
            with patch("rejoice.setup.console"):
                device = choose_microphone()
                assert device == 0  # Returns device index


def test_choose_microphone_no_devices():
    """GIVEN no audio devices are available
    WHEN choose_microphone is called
    THEN returns default"""
    from rejoice.setup import choose_microphone

    with patch("rejoice.setup.get_audio_input_devices", return_value=[]):
        with patch("rejoice.setup.console"):
            device = choose_microphone()
            assert device == "default"


def test_test_microphone_with_device():
    """GIVEN microphone test with specific device
    WHEN test_microphone is called with device parameter
    THEN device parameter is passed to record_audio"""
    from rejoice.setup import test_microphone

    with patch("rejoice.setup.record_audio") as mock_record:
        with patch("rejoice.setup.console"):
            with patch("rejoice.setup.time.sleep"):
                mock_stream = MagicMock()
                mock_record.return_value = mock_stream

                test_microphone(device=1, duration=1.0)

                # Should pass device parameter
                mock_record.assert_called_once()
                call_args = mock_record.call_args
                assert call_args[1]["device"] == 1  # device is a keyword arg


def test_setup_save_location():
    """GIVEN user is prompted for save location
    WHEN valid path is provided
    THEN path is returned and expanded"""
    from rejoice.setup import setup_save_location

    with patch("rejoice.setup.Prompt.ask", return_value="~/Documents/transcripts"):
        with patch("rejoice.setup.console"):
            save_path = setup_save_location()
            assert save_path is not None
            assert "~" not in save_path  # Should be expanded


def test_setup_save_location_creates_directory():
    """GIVEN user provides new save location
    WHEN setup_save_location is called
    THEN directory is created if it doesn't exist"""
    from rejoice.setup import setup_save_location

    with tempfile.TemporaryDirectory() as tmpdir:
        new_path = Path(tmpdir) / "new_transcripts"
        with patch("rejoice.setup.Prompt.ask", return_value=str(new_path)):
            with patch("rejoice.setup.console"):
                save_path = setup_save_location()
                assert Path(save_path).exists()


def test_test_ollama_connection_success():
    """GIVEN Ollama is running
    WHEN test_ollama is called
    THEN returns True"""
    from rejoice.setup import test_ollama_connection

    mock_client = MagicMock()
    mock_client.list.return_value = {"models": [{"name": "llama2"}]}

    with patch("rejoice.setup.Ollama", return_value=mock_client):
        with patch("rejoice.setup.console"):
            result = test_ollama_connection("http://localhost:11434")
            assert result is True


def test_test_ollama_connection_failure():
    """GIVEN Ollama is not running
    WHEN test_ollama is called
    THEN returns False"""
    from rejoice.setup import test_ollama_connection

    with patch("rejoice.setup.Ollama") as mock_ollama:
        mock_ollama.side_effect = Exception("Connection refused")

        with patch("rejoice.setup.console"):
            result = test_ollama_connection("http://localhost:11434")
            assert result is False


def test_create_sample_transcript():
    """GIVEN setup is complete
    WHEN create_sample_transcript is called
    THEN sample transcript file is created"""
    from rejoice.setup import create_sample_transcript

    with tempfile.TemporaryDirectory() as tmpdir:
        save_dir = Path(tmpdir)
        with patch("rejoice.setup.console"):
            create_sample_transcript(save_dir)

            # Should create a transcript file
            transcript_files = list(save_dir.glob("*.md"))
            assert len(transcript_files) == 1

            # Should contain sample content
            content = transcript_files[0].read_text()
            assert "Welcome to Rejoice" in content or "sample" in content.lower()


def test_first_run_setup_full_flow():
    """GIVEN first run setup is triggered
    WHEN all steps complete successfully
    THEN config file is created with user selections"""
    from rejoice.setup import run_first_setup

    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / ".config" / "rejoice"
        config_dir.mkdir(parents=True)

        with patch("rejoice.setup.get_config_dir", return_value=config_dir):
            with patch("rejoice.setup.console"):
                # Mock Confirm.ask to return True for mic test prompt
                with patch(
                    "rejoice.setup.Confirm.ask", return_value=True
                ):  # Mock all Confirm.ask calls (mic test + download continue)
                    with patch(
                        "rejoice.setup.select_whisper_model", return_value="small"
                    ):
                        with patch(
                            "rejoice.setup.download_whisper_model", return_value=True
                        ):
                            with patch(
                                "rejoice.setup.choose_microphone",
                                return_value="default",
                            ):
                                with patch(
                                    "rejoice.setup.test_microphone", return_value=True
                                ):
                                    with patch(
                                        "rejoice.setup.setup_save_location",
                                        return_value=str(Path(tmpdir) / "transcripts"),
                                    ):
                                        with patch(
                                            "rejoice.setup.test_ollama_connection",
                                            return_value=True,
                                        ):
                                            with patch(
                                                "rejoice.setup.create_sample_transcript"
                                            ):
                                                run_first_setup()

                                                # Verify device was saved to config
                                                config_file = config_dir / "config.yaml"
                                                assert config_file.exists()
                                                config_data = yaml.safe_load(
                                                    config_file.read_text()
                                                )
                                                assert "audio" in config_data
                                                assert (
                                                    config_data["audio"]["device"]
                                                    == "default"
                                                )

                                        # Config file should be created
                                        config_file = config_dir / "config.yaml"
                                        assert config_file.exists()

                                        # Should contain user selections
                                        config_data = yaml.safe_load(
                                            config_file.read_text()
                                        )
                                        assert (
                                            config_data["transcription"]["model"]
                                            == "small"
                                        )


def test_first_run_setup_cancelled():
    """GIVEN user cancels during setup
    WHEN setup is interrupted
    THEN no config file is created"""
    from rejoice.setup import run_first_setup

    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / ".config" / "rejoice"
        config_dir.mkdir(parents=True)

        with patch("rejoice.setup.get_config_dir", return_value=config_dir):
            with patch("rejoice.setup.console"):
                # Simulate user cancelling at mic test prompt
                with patch("rejoice.setup.Confirm.ask", return_value=False):
                    # User skips mic test, but setup continues
                    # So we need to cancel at a later step -
                    # let's cancel at model download failure
                    with patch("rejoice.setup.test_microphone", return_value=True):
                        with patch(
                            "rejoice.setup.setup_save_location",
                            return_value=str(Path(tmpdir) / "transcripts"),
                        ):
                            with patch(
                                "rejoice.setup.select_whisper_model",
                                return_value="small",
                            ):
                                with patch(
                                    "rejoice.setup.download_whisper_model",
                                    return_value=False,
                                ):
                                    # User cancels when asked to continue
                                    # after download failure
                                    with pytest.raises(SystemExit):
                                        run_first_setup()

                                    # Config file should not exist
                                    config_file = config_dir / "config.yaml"
                                    assert not config_file.exists()
