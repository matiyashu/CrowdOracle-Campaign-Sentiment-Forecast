"""
Campaign API blueprint.

Endpoints:
    POST   /api/campaign/create
    GET    /api/campaign/list
    GET    /api/campaign/<campaign_id>
    PATCH  /api/campaign/<campaign_id>
    DELETE /api/campaign/<campaign_id>
"""

from flask import Blueprint, jsonify, request

from app.models.campaign import Campaign
from app.services.campaign_ingestion_service import (
    create_campaign,
    update_campaign,
    delete_campaign,
)

campaign_bp = Blueprint("campaign", __name__)


# ── helpers ──────────────────────────────────────────────────────────────────

def _ok(data=None, **kwargs):
    return jsonify({"success": True, "data": data, **kwargs})


def _err(message: str, status: int = 400):
    return jsonify({"success": False, "error": message}), status


def _get_campaign_or_404(campaign_id: str):
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return None
    return campaign


# ── routes ───────────────────────────────────────────────────────────────────

@campaign_bp.route("/create", methods=["POST"])
def create():
    data = request.get_json(silent=True) or {}
    try:
        campaign = create_campaign(data)
        return _ok(campaign.to_dict()), 201
    except ValueError as e:
        return _err(str(e))
    except Exception as e:
        return _err(f"Failed to create campaign: {e}", 500)


@campaign_bp.route("/list", methods=["GET"])
def list_campaigns():
    status_filter = request.args.get("status")
    query = Campaign.query.order_by(Campaign.created_at.desc())
    if status_filter:
        query = query.filter_by(status=status_filter)
    campaigns = query.all()
    return _ok([c.to_dict() for c in campaigns])


@campaign_bp.route("/<campaign_id>", methods=["GET"])
def get_campaign(campaign_id):
    campaign = _get_campaign_or_404(campaign_id)
    if not campaign:
        return _err("Campaign not found", 404)
    return _ok(campaign.to_dict())


@campaign_bp.route("/<campaign_id>", methods=["PATCH"])
def patch_campaign(campaign_id):
    campaign = _get_campaign_or_404(campaign_id)
    if not campaign:
        return _err("Campaign not found", 404)
    data = request.get_json(silent=True) or {}
    try:
        campaign = update_campaign(campaign, data)
        return _ok(campaign.to_dict())
    except ValueError as e:
        return _err(str(e))
    except Exception as e:
        return _err(f"Failed to update campaign: {e}", 500)


@campaign_bp.route("/<campaign_id>", methods=["DELETE"])
def remove_campaign(campaign_id):
    campaign = _get_campaign_or_404(campaign_id)
    if not campaign:
        return _err("Campaign not found", 404)
    try:
        delete_campaign(campaign)
        return _ok({"deleted": campaign_id})
    except Exception as e:
        return _err(f"Failed to delete campaign: {e}", 500)
