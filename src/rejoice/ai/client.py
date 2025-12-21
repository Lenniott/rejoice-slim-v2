"""Ollama REST API client for AI enhancement."""
import json
from typing import Iterator, List

import requests

from rejoice.exceptions import AIError


class OllamaClient:
    """Client for interacting with Ollama REST API."""

    def __init__(self, base_url: str = "http://localhost:11434", timeout: int = 30):
        """Initialize Ollama client.

        Args:
            base_url: Base URL for Ollama API (default: http://localhost:11434)
            timeout: Request timeout in seconds (default: 30)
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def generate(
        self, prompt: str, model: str = "qwen3:4b", stream: bool = False
    ) -> str:
        """Generate text using Ollama.

        Args:
            prompt: The prompt to send to the model
            model: Model name to use (default: qwen3:4b)
            stream: Whether to stream the response (default: False)

        Returns:
            Generated text response

        Raises:
            AIError: If connection fails, timeout occurs, or API returns error
        """
        if stream:
            # For streaming, collect all chunks and return concatenated result
            chunks = list(self.generate_streaming(prompt, model))
            return "".join(chunks)

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": model, "prompt": prompt},
                stream=False,
                timeout=self.timeout,
            )
            response.raise_for_status()
            result = response.json()
            response_text = result.get("response", "")
            return str(response_text) if response_text else ""
        except requests.exceptions.ConnectionError as e:
            raise AIError(
                "Cannot connect to Ollama. Is Ollama running?",
                suggestion="Start Ollama with: ollama serve",
            ) from e
        except requests.exceptions.Timeout as e:
            raise AIError(
                f"Request to Ollama timed out after {self.timeout} seconds.",
                suggestion="Try increasing the timeout or using a smaller model.",
            ) from e
        except requests.exceptions.HTTPError as e:
            status_code = (
                e.response.status_code
                if hasattr(e, "response") and e.response
                else "unknown"
            )
            raise AIError(
                f"Ollama API returned error: {status_code}",
                suggestion=(
                    "Check that the model exists and Ollama is running correctly."
                ),
            ) from e
        except Exception as e:
            raise AIError(f"Unexpected error calling Ollama: {str(e)}") from e

    def generate_streaming(self, prompt: str, model: str = "qwen3:4b") -> Iterator[str]:
        """Generate text with streaming response.

        Yields text chunks as they are generated.

        Args:
            prompt: The prompt to send to the model
            model: Model name to use (default: qwen3:4b)

        Yields:
            Text chunks as strings

        Raises:
            AIError: If connection fails, timeout occurs, or API returns error
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": model, "prompt": prompt, "stream": True},
                stream=True,
                timeout=self.timeout,
            )
            response.raise_for_status()

            for line in response.iter_lines():
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]
                    if data.get("done", False):
                        break
                except json.JSONDecodeError:
                    # Skip malformed JSON lines
                    continue

        except requests.exceptions.ConnectionError as e:
            raise AIError(
                "Cannot connect to Ollama. Is Ollama running?",
                suggestion="Start Ollama with: ollama serve",
            ) from e
        except requests.exceptions.Timeout as e:
            raise AIError(
                f"Request to Ollama timed out after {self.timeout} seconds.",
                suggestion="Try increasing the timeout or using a smaller model.",
            ) from e
        except requests.exceptions.HTTPError as e:
            status_code = (
                e.response.status_code
                if hasattr(e, "response") and e.response
                else "unknown"
            )
            raise AIError(
                f"Ollama API returned error: {status_code}",
                suggestion=(
                    "Check that the model exists and Ollama is running correctly."
                ),
            ) from e
        except Exception as e:
            raise AIError(f"Unexpected error calling Ollama: {str(e)}") from e

    def test_connection(self) -> bool:
        """Test connection to Ollama server.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Use a lightweight endpoint to test connection
            # The /api/tags endpoint is lightweight and doesn't require model
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            return True
        except Exception:
            return False

    def list_models(self) -> List[str]:
        """List available Ollama models.

        Returns:
            List of model names (empty list if connection fails)
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            data = response.json()
            models = data.get("models", [])
            # Extract model names from list of dicts
            return [model.get("name", "") for model in models if "name" in model]
        except Exception:
            # Return empty list if connection fails (graceful degradation)
            return []
