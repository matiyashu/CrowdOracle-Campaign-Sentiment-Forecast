"""
Campaign ingestion service.
Handles create, update, and metadata validation for Campaign records.
"""

from __future__ import annotations

from datetime import date

from app.database import db
from app.models.campaign import Campaign


def create_campaign(data: dict) -> Campaign:
    """
    Create and persist a new Campaign.

    Expected keys in data:
        name (required), brand (required), objective, markets, channels,
        start_date (YYYY-MM-DD), end_date (YYYY-MM-DD), tags, status
    """
    _validate_required(data, ["name", "brand"])

    campaign = Campaign(
        name=data["name"].strip(),
        brand=data["brand"].strip(),
        objective=data.get("objective", "").strip() or None,
        markets=data.get("markets", []),
        channels=data.get("channels", []),
        start_date=_parse_date(data.get("start_date")),
        end_date=_parse_date(data.get("end_date")),
        tags=data.get("tags", []),
        status=data.get("status", "draft"),
    )
    db.session.add(campaign)
    db.session.commit()
    return campaign


def update_campaign(campaign: Campaign, data: dict) -> Campaign:
    """Apply a partial update (PATCH) to an existing campaign."""
    field_map = {
        "name": str,
        "brand": str,
        "objective": str,
        "markets": list,
        "channels": list,
        "tags": list,
        "status": str,
    }
    for field, cast in field_map.items():
        if field in data:
            value = data[field]
            if isinstance(value, str):
                value = value.strip() or None
            setattr(campaign, field, value)

    if "start_date" in data:
        campaign.start_date = _parse_date(data["start_date"])
    if "end_date" in data:
        campaign.end_date = _parse_date(data["end_date"])

    db.session.commit()
    return campaign


def delete_campaign(campaign: Campaign) -> None:
    db.session.delete(campaign)
    db.session.commit()


# ── helpers ──────────────────────────────────────────────────────────────────

def _validate_required(data: dict, fields: list[str]) -> None:
    missing = [f for f in fields if not data.get(f)]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid date format '{value}'. Use YYYY-MM-DD.")
