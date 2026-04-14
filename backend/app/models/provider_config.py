"""
ProviderConfig model — user-saved LLM provider configuration.
Supports multiple providers with per-task model routing.
"""

import uuid
from datetime import datetime, timezone

from ..database import db


class ProviderConfig(db.Model):
    __tablename__ = 'provider_configs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    name = db.Column(db.String(100), nullable=False)          # e.g. "My OpenAI" or "Claude Pro"
    provider_type = db.Column(db.String(50), nullable=False)  # openai | anthropic | qwen | gemini | custom
    base_url = db.Column(db.String(512))
    api_key_ref = db.Column(db.String(512))                   # encrypted or raw key (env-ref in prod)
    default_model = db.Column(db.String(200))
    fallback_model = db.Column(db.String(200))
    max_tokens = db.Column(db.Integer, default=4096)
    temperature = db.Column(db.Float, default=0.3)
    multimodal_enabled = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=False)

    # Per-task model routing: {"creative_vision": "gpt-4o", "sentiment": "gpt-4o-mini", ...}
    task_routing = db.Column(db.JSON, default=dict)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self, include_key=False):
        data = {
            'id': self.id,
            'name': self.name,
            'provider_type': self.provider_type,
            'base_url': self.base_url,
            'default_model': self.default_model,
            'fallback_model': self.fallback_model,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'multimodal_enabled': self.multimodal_enabled,
            'is_active': self.is_active,
            'task_routing': self.task_routing or {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_key:
            data['api_key_ref'] = self.api_key_ref
        return data
