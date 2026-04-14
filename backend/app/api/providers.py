"""
Providers API blueprint — manage LLM provider configurations.

Endpoints:
    GET    /api/providers/list
    POST   /api/providers/save
    POST   /api/providers/test-connection
    PATCH  /api/providers/<provider_id>
    DELETE /api/providers/<provider_id>
    POST   /api/providers/set-active
    POST   /api/providers/task-routing
"""

from flask import Blueprint, jsonify, request

from app.database import db
from app.models.provider_config import ProviderConfig
from app.services.llm.registry import _build_provider

providers_bp = Blueprint("providers", __name__)

SUPPORTED_TYPES = {"openai", "anthropic", "qwen", "gemini", "custom"}


def _ok(data=None, **kwargs):
    return jsonify({"success": True, "data": data, **kwargs})


def _err(message: str, status: int = 400):
    return jsonify({"success": False, "error": message}), status


@providers_bp.route("/list", methods=["GET"])
def list_providers():
    configs = ProviderConfig.query.order_by(ProviderConfig.created_at).all()
    return _ok([c.to_dict() for c in configs])


@providers_bp.route("/save", methods=["POST"])
def save_provider():
    data = request.get_json(silent=True) or {}
    provider_type = data.get("provider_type", "").lower()
    if provider_type not in SUPPORTED_TYPES:
        return _err(f"Unsupported provider_type. Choose from: {', '.join(SUPPORTED_TYPES)}")
    if not data.get("name"):
        return _err("'name' is required")

    config = ProviderConfig(
        name=data["name"].strip(),
        provider_type=provider_type,
        base_url=data.get("base_url"),
        api_key_ref=data.get("api_key"),
        default_model=data.get("default_model"),
        fallback_model=data.get("fallback_model"),
        max_tokens=int(data.get("max_tokens", 4096)),
        temperature=float(data.get("temperature", 0.3)),
        multimodal_enabled=bool(data.get("multimodal_enabled", False)),
        task_routing=data.get("task_routing", {}),
        is_active=bool(data.get("is_active", False)),
    )
    db.session.add(config)
    db.session.commit()
    return _ok(config.to_dict()), 201


@providers_bp.route("/test-connection", methods=["POST"])
def test_connection():
    data = request.get_json(silent=True) or {}
    provider_type = data.get("provider_type", "openai").lower()
    api_key = data.get("api_key", "")
    base_url = data.get("base_url")
    model = data.get("default_model", "gpt-4o-mini")

    try:
        provider = _build_provider(provider_type, api_key, base_url, model)
        result = provider.test_connection()
        return _ok(result)
    except Exception as e:
        return _ok({"ok": False, "message": str(e)})


@providers_bp.route("/<provider_id>", methods=["PATCH"])
def patch_provider(provider_id):
    config = ProviderConfig.query.get(provider_id)
    if not config:
        return _err("Provider not found", 404)

    data = request.get_json(silent=True) or {}
    updatable = ["name", "base_url", "default_model", "fallback_model",
                 "max_tokens", "temperature", "multimodal_enabled", "task_routing"]
    for field in updatable:
        if field in data:
            setattr(config, field, data[field])
    if "api_key" in data:
        config.api_key_ref = data["api_key"]

    db.session.commit()
    return _ok(config.to_dict())


@providers_bp.route("/<provider_id>", methods=["DELETE"])
def delete_provider(provider_id):
    config = ProviderConfig.query.get(provider_id)
    if not config:
        return _err("Provider not found", 404)
    db.session.delete(config)
    db.session.commit()
    return _ok({"deleted": provider_id})


@providers_bp.route("/set-active", methods=["POST"])
def set_active():
    data = request.get_json(silent=True) or {}
    provider_id = data.get("provider_id")
    if not provider_id:
        return _err("'provider_id' is required")

    config = ProviderConfig.query.get(provider_id)
    if not config:
        return _err("Provider not found", 404)

    # Deactivate all, then activate the chosen one
    ProviderConfig.query.update({"is_active": False})
    config.is_active = True
    db.session.commit()
    return _ok(config.to_dict())


@providers_bp.route("/task-routing", methods=["POST"])
def update_task_routing():
    """Save per-task model routing to the active provider."""
    data = request.get_json(silent=True) or {}
    routing = data.get("routing")
    if not isinstance(routing, dict):
        return _err("'routing' must be a dict mapping task names to model strings")

    config = ProviderConfig.query.filter_by(is_active=True).first()
    if not config:
        return _err("No active provider. Set one first via /set-active.")

    config.task_routing = routing
    db.session.commit()
    return _ok(config.to_dict())
