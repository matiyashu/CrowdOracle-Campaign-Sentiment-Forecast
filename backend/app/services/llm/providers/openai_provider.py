"""
OpenAI provider — wraps the openai SDK.
Also used as the base for any OpenAI-compatible endpoint (Qwen, Gemini via compat, etc.).
"""

import base64
import os

from openai import OpenAI

from ..base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        default_model: str = "gpt-4o-mini",
        max_tokens: int = 4096,
        **kwargs,
    ):
        self.api_key = api_key or os.environ.get("LLM_API_KEY", "")
        self.base_url = base_url or os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")
        self.default_model = default_model or os.environ.get("LLM_MODEL_NAME", "gpt-4o-mini")
        self.max_tokens = max_tokens
        self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def chat(self, messages, model=None, temperature=0.3, max_tokens=None, response_format=None, **kwargs):
        kwargs_extra = {}
        if response_format:
            kwargs_extra["response_format"] = response_format

        resp = self._client.chat.completions.create(
            model=model or self.default_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens or self.max_tokens,
            **kwargs_extra,
        )
        return resp.choices[0].message.content

    def analyze_image(self, image_path, prompt, model=None):
        with open(image_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        ext = os.path.splitext(image_path)[1].lstrip(".").lower()
        mime = f"image/{ext}" if ext != "jpg" else "image/jpeg"

        resp = self._client.chat.completions.create(
            model=model or self.default_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{data}"}},
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
            max_tokens=self.max_tokens,
        )
        return resp.choices[0].message.content

    def test_connection(self):
        try:
            models = self._client.models.list()
            return {"ok": True, "message": f"Connected. Found {len(list(models))} models."}
        except Exception as e:
            return {"ok": False, "message": str(e)}
