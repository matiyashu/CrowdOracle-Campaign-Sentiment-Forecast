"""
Anthropic (Claude) provider.
"""

import base64
import os

from ..base import BaseLLMProvider


class AnthropicProvider(BaseLLMProvider):
    def __init__(
        self,
        api_key: str | None = None,
        default_model: str = "claude-sonnet-4-6",
        max_tokens: int = 4096,
        **kwargs,
    ):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.default_model = default_model
        self.max_tokens = max_tokens

    def _get_client(self):
        try:
            import anthropic
            return anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise RuntimeError("anthropic package is not installed. Run: pip install anthropic")

    def chat(self, messages, model=None, temperature=0.3, max_tokens=None, response_format=None, **kwargs):
        client = self._get_client()
        # Anthropic separates system from user messages
        system_msgs = [m["content"] for m in messages if m["role"] == "system"]
        user_msgs = [m for m in messages if m["role"] != "system"]
        system = "\n\n".join(system_msgs) if system_msgs else None

        extra = {}
        if system:
            extra["system"] = system

        resp = client.messages.create(
            model=model or self.default_model,
            max_tokens=max_tokens or self.max_tokens,
            temperature=temperature,
            messages=user_msgs,
            **extra,
        )
        return resp.content[0].text

    def analyze_image(self, image_path, prompt, model=None):
        client = self._get_client()
        with open(image_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        ext = os.path.splitext(image_path)[1].lstrip(".").lower()
        media_type = f"image/{ext}" if ext != "jpg" else "image/jpeg"

        resp = client.messages.create(
            model=model or self.default_model,
            max_tokens=self.max_tokens,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": data}},
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )
        return resp.content[0].text

    def test_connection(self):
        try:
            self.chat([{"role": "user", "content": "ping"}], max_tokens=10)
            return {"ok": True, "message": "Anthropic connection successful."}
        except Exception as e:
            return {"ok": False, "message": str(e)}
