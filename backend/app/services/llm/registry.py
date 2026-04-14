"""
LLM Provider Registry.

Routes LLM calls to the correct provider based on:
  1. Per-task routing saved in the active ProviderConfig record (DB).
  2. The active ProviderConfig's default model.
  3. Fallback: env-var provider (backward compatible with existing MiroFish services).

Usage:
    from app.services.llm import get_provider

    provider = get_provider("sentiment")
    result = provider.chat([{"role": "user", "content": "..."}])
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from .base import BaseLLMProvider

if TYPE_CHECKING:
    pass

# Known task names used throughout the platform
TASK_NAMES = [
    "creative_vision",   # image/video analysis
    "sentiment",         # sentiment & aspect extraction
    "report_writer",     # long-form report narrative
    "simulation",        # MiroFish simulation LLM calls
    "transcript",        # audio/video transcription
    "chat",              # interactive Q&A / interaction view
    "keyword",           # keyword/phrase extraction
    "impact",            # impact scoring & recommendations
]


def _build_provider(provider_type: str, api_key: str, base_url: str | None, default_model: str) -> BaseLLMProvider:
    """Instantiate the correct provider class from config values."""
    from .providers.openai_provider import OpenAIProvider
    from .providers.anthropic_provider import AnthropicProvider
    from .providers.qwen_provider import QwenProvider
    from .providers.gemini_provider import GeminiProvider
    from .providers.custom_provider import CustomProvider

    mapping = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "qwen": QwenProvider,
        "gemini": GeminiProvider,
        "custom": CustomProvider,
    }
    cls = mapping.get(provider_type, OpenAIProvider)

    kwargs: dict = {"default_model": default_model, "api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url

    return cls(**kwargs)


def _env_fallback_provider() -> BaseLLMProvider:
    """Return a provider built purely from environment variables (MiroFish backward compat)."""
    from .providers.openai_provider import OpenAIProvider
    return OpenAIProvider(
        api_key=os.environ.get("LLM_API_KEY", ""),
        base_url=os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1"),
        default_model=os.environ.get("LLM_MODEL_NAME", "gpt-4o-mini"),
    )


def get_provider(task: str = "chat") -> BaseLLMProvider:
    """
    Return the best provider for the given task.

    Tries the DB-saved active ProviderConfig first, then falls back to env vars.
    Safe to call outside app context (returns env fallback in that case).
    """
    try:
        from flask import current_app  # noqa: F401 — just to trigger ImportError outside context
        from app.models.provider_config import ProviderConfig

        active = ProviderConfig.query.filter_by(is_active=True).first()
        if not active:
            return _env_fallback_provider()

        # Check if there's a task-specific model override
        routing = active.task_routing or {}
        model_override = routing.get(task)
        default_model = model_override or active.default_model or os.environ.get("LLM_MODEL_NAME", "gpt-4o-mini")

        return _build_provider(
            provider_type=active.provider_type,
            api_key=active.api_key_ref or "",
            base_url=active.base_url,
            default_model=default_model,
        )

    except Exception:
        # Outside app context or no active config — use env vars
        return _env_fallback_provider()


class _Registry:
    """Convenience object: registry.get("sentiment") → BaseLLMProvider."""
    def get(self, task: str = "chat") -> BaseLLMProvider:
        return get_provider(task)


registry = _Registry()
