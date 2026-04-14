"""
Custom OpenAI-compatible provider — any base URL the user configures.
"""

from .openai_provider import OpenAIProvider


class CustomProvider(OpenAIProvider):
    """Generic wrapper for any OpenAI-compatible endpoint."""

    def __init__(self, api_key: str, base_url: str, default_model: str, max_tokens: int = 4096, **kwargs):
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            default_model=default_model,
            max_tokens=max_tokens,
        )
