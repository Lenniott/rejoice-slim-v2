"""Tests for Ollama client integration."""
from unittest.mock import Mock, patch

import pytest
import requests

from rejoice.ai.client import OllamaClient
from rejoice.exceptions import AIError


class TestOllamaClient:
    """Test Ollama REST API client."""

    def test_init_with_default_url(self):
        """GIVEN no base_url provided
        WHEN OllamaClient is initialized
        THEN default URL is used"""
        client = OllamaClient()
        assert client.base_url == "http://localhost:11434"

    def test_init_with_custom_url(self):
        """GIVEN custom base_url provided
        WHEN OllamaClient is initialized
        THEN custom URL is used"""
        client = OllamaClient(base_url="http://custom:11434")
        assert client.base_url == "http://custom:11434"

    @patch("rejoice.ai.client.requests.post")
    def test_generate_success(self, mock_post):
        """GIVEN Ollama is running
        WHEN generate is called with prompt
        THEN response text is returned"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Generated text here"}
        mock_post.return_value = mock_response

        client = OllamaClient()
        result = client.generate("Test prompt", model="qwen3:4b")

        assert result == "Generated text here"
        mock_post.assert_called_once_with(
            "http://localhost:11434/api/generate",
            json={"model": "qwen3:4b", "prompt": "Test prompt"},
            stream=False,
            timeout=30,
        )

    @patch("rejoice.ai.client.requests.post")
    def test_generate_with_different_model(self, mock_post):
        """GIVEN Ollama client
        WHEN generate is called with different model
        THEN correct model is used in request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Response"}
        mock_post.return_value = mock_response

        client = OllamaClient()
        client.generate("Prompt", model="mistral")

        call_args = mock_post.call_args
        assert call_args[1]["json"]["model"] == "mistral"

    @patch("rejoice.ai.client.requests.post")
    def test_generate_connection_error(self, mock_post):
        """GIVEN Ollama is not running
        WHEN generate is called
        THEN AIError is raised with helpful message"""
        mock_post.side_effect = requests.exceptions.ConnectionError(
            "Connection refused"
        )

        client = OllamaClient()
        with pytest.raises(AIError) as exc_info:
            client.generate("Test prompt")

        error_msg_lower = str(exc_info.value).lower()
        assert "ollama" in error_msg_lower
        assert "connection" in error_msg_lower or "running" in error_msg_lower

    @patch("rejoice.ai.client.requests.post")
    def test_generate_timeout_error(self, mock_post):
        """GIVEN request times out
        WHEN generate is called
        THEN AIError is raised"""
        mock_post.side_effect = requests.exceptions.Timeout("Request timeout")

        client = OllamaClient()
        with pytest.raises(AIError) as exc_info:
            client.generate("Test prompt")

        assert (
            "timeout" in str(exc_info.value).lower()
            or "timed out" in str(exc_info.value).lower()
        )

    @patch("rejoice.ai.client.requests.post")
    def test_generate_http_error(self, mock_post):
        """GIVEN Ollama returns error status
        WHEN generate is called
        THEN AIError is raised"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "500 Server Error", response=mock_response
        )
        mock_post.return_value = mock_response

        client = OllamaClient()
        with pytest.raises(AIError):
            client.generate("Test prompt")

    @patch("rejoice.ai.client.requests.post")
    def test_generate_streaming_success(self, mock_post):
        """GIVEN Ollama client with streaming enabled
        WHEN generate_streaming is called
        THEN text chunks are yielded"""
        # Mock streaming response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = [
            b'{"response": "Hello", "done": false}',
            b'{"response": " world", "done": false}',
            b'{"response": "!", "done": true}',
        ]
        mock_post.return_value = mock_response

        client = OllamaClient()
        chunks = list(client.generate_streaming("Test prompt", model="qwen3:4b"))

        assert chunks == ["Hello", " world", "!"]
        call_args = mock_post.call_args
        assert call_args[1]["stream"] is True

    @patch("rejoice.ai.client.requests.post")
    def test_generate_streaming_connection_error(self, mock_post):
        """GIVEN Ollama is not running
        WHEN generate_streaming is called
        THEN AIError is raised"""
        mock_post.side_effect = requests.exceptions.ConnectionError()

        client = OllamaClient()
        with pytest.raises(AIError):
            list(client.generate_streaming("Test prompt"))

    @patch("rejoice.ai.client.requests.get")
    def test_test_connection_success(self, mock_get):
        """GIVEN Ollama is running
        WHEN test_connection is called
        THEN True is returned"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        client = OllamaClient()
        result = client.test_connection()

        assert result is True
        # Should use a lightweight endpoint for testing
        mock_get.assert_called_once_with("http://localhost:11434/api/tags", timeout=5)

    @patch("rejoice.ai.client.requests.get")
    def test_test_connection_failure(self, mock_get):
        """GIVEN Ollama is not running
        WHEN test_connection is called
        THEN False is returned"""
        mock_get.side_effect = requests.exceptions.ConnectionError()

        client = OllamaClient()
        result = client.test_connection()

        assert result is False

    @patch("rejoice.ai.client.requests.get")
    def test_test_connection_http_error(self, mock_get):
        """GIVEN Ollama returns error
        WHEN test_connection is called
        THEN False is returned"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "500 Server Error", response=mock_response
        )
        mock_get.return_value = mock_response

        client = OllamaClient()
        result = client.test_connection()

        assert result is False

    @patch("rejoice.ai.client.requests.get")
    def test_list_models_success(self, mock_get):
        """GIVEN Ollama is running
        WHEN list_models is called
        THEN list of model names is returned"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "qwen3:4b:latest"},
                {"name": "mistral:latest"},
            ]
        }
        mock_get.return_value = mock_response

        client = OllamaClient()
        models = client.list_models()

        assert "qwen3:4b:latest" in models
        assert "mistral:latest" in models
        mock_get.assert_called_once_with("http://localhost:11434/api/tags", timeout=5)

    @patch("rejoice.ai.client.requests.get")
    def test_list_models_connection_error(self, mock_get):
        """GIVEN Ollama is not running
        WHEN list_models is called
        THEN empty list is returned"""
        mock_get.side_effect = requests.exceptions.ConnectionError()

        client = OllamaClient()
        models = client.list_models()

        assert models == []
