"""
Base LLM provider interface.
All providers must implement this contract so callers are provider-agnostic.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseLLMProvider(ABC):
    """Abstract base for all LLM provider implementations."""

    @abstractmethod
    def chat(
        self,
        messages: list[dict],
        model: str | None = None,
        temperature: float = 0.3,
        max_tokens: int | None = None,
        response_format: dict | None = None,
        **kwargs: Any,
    ) -> str:
        """
        Send a chat completion request.

        Args:
            messages: List of {"role": ..., "content": ...} dicts.
            model: Override the provider's default model.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens in the response.
            response_format: e.g. {"type": "json_object"} for structured output.

        Returns:
            The assistant message content as a string.
        """

    @abstractmethod
    def analyze_image(
        self,
        image_path: str,
        prompt: str,
        model: str | None = None,
    ) -> str:
        """
        Analyze an image file and return a text description/analysis.

        Args:
            image_path: Absolute path to the image file.
            prompt: Instruction for the model (e.g. "Describe the CTA in this ad").
            model: Override the provider's vision model.

        Returns:
            Model response as a string.
        """

    @abstractmethod
    def test_connection(self) -> dict:
        """
        Test the provider connection.

        Returns:
            {"ok": True/False, "message": "..."}
        """

    def transcribe(self, audio_path: str, model: str | None = None) -> str:
        """
        Transcribe audio/video to text.
        Providers that don't support this raise NotImplementedError.
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support transcription")
