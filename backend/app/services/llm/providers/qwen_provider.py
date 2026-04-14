"""
Qwen provider — Alibaba Qwen via OpenAI-compatible endpoint.
Default base URL: https://dashscope.aliyuncs.com/compatible-mode/v1
"""

import os

from .openai_provider import OpenAIProvider


class QwenProvider(OpenAIProvider):
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        default_model: str = "qwen-plus",
        max_tokens: int = 4096,
        **kwargs,
    ):
        super().__init__(
            api_key=api_key or os.environ.get("LLM_API_KEY", ""),
            base_url=base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1",
            default_model=default_model,
            max_tokens=max_tokens,
        )
