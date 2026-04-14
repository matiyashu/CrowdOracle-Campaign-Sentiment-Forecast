"""
Gemini provider — Google Gemini via OpenAI-compatible endpoint.
Base URL: https://generativelanguage.googleapis.com/v1beta/openai/
"""

import os

from .openai_provider import OpenAIProvider


class GeminiProvider(OpenAIProvider):
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        default_model: str = "gemini-2.0-flash",
        max_tokens: int = 4096,
        **kwargs,
    ):
        super().__init__(
            api_key=api_key or os.environ.get("GEMINI_API_KEY", ""),
            base_url=base_url or "https://generativelanguage.googleapis.com/v1beta/openai/",
            default_model=default_model,
            max_tokens=max_tokens,
        )
