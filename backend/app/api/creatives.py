"""
Creatives API blueprint — upload and analyze marketing creative assets.

Sprint 1: upload + retrieve endpoints.
Sprint 2: analyze endpoint with full creative_analysis_service.

Endpoints:
    POST  /api/creatives/upload
    GET   /api/creatives/<asset_id>
    GET   /api/creatives/by-campaign/<campaign_id>
    POST  /api/creatives/<asset_id>/analyze
    POST  /api/creatives/batch-analyze
    PATCH /api/creatives/<asset_id>/tags
"""

import os
import threading
import uuid

from flask import Blueprint, current_app, jsonify, request
from werkzeug.utils import secure_filename

from app.database import db
from app.models.campaign import Campaign
from app.models.creative_asset import CreativeAsset
from app.services.creative_analysis_service import analyze_asset as run_analysis

creatives_bp = Blueprint("creatives", __name__)

IMAGE_EXTS = {"png", "jpg", "jpeg", "webp", "gif"}
VIDEO_EXTS = {"mp4", "mov", "avi", "mkv", "webm"}
COPY_EXTS = {"txt", "md", "markdown"}


def _ok(data=None, **kwargs):
    return jsonify({"success": True, "data": data, **kwargs})


def _err(message: str, status: int = 400):
    return jsonify({"success": False, "error": message}), status


def _detect_type(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext in IMAGE_EXTS:
        return "image"
    if ext in VIDEO_EXTS:
        return "video"
    if ext in COPY_EXTS:
        return "copy"
    return "document"


def _allowed(filename: str) -> bool:
    allowed = current_app.config.get("ALLOWED_EXTENSIONS", set())
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in allowed


@creatives_bp.route("/upload", methods=["POST"])
def upload():
    campaign_id = request.form.get("campaign_id")
    if not campaign_id:
        return _err("'campaign_id' is required")

    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return _err("Campaign not found", 404)

    file = request.files.get("file")
    if not file or not file.filename:
        return _err("No file provided")

    if not _allowed(file.filename):
        return _err(f"File type not allowed: {file.filename}")

    media_folder = current_app.config["MEDIA_UPLOAD_FOLDER"]
    os.makedirs(media_folder, exist_ok=True)

    asset_id = str(uuid.uuid4())
    safe_name = secure_filename(file.filename)
    dest_filename = f"{asset_id}_{safe_name}"
    dest_path = os.path.join(media_folder, dest_filename)
    file.save(dest_path)

    asset = CreativeAsset(
        id=asset_id,
        campaign_id=campaign_id,
        original_filename=file.filename,
        file_path=dest_path,
        asset_type=_detect_type(file.filename),
        file_size_bytes=os.path.getsize(dest_path),
        mime_type=file.content_type,
        channel=request.form.get("channel"),
        market=request.form.get("market"),
        tags=request.form.getlist("tags"),
        analysis_status="pending",
    )

    publish_date = request.form.get("publish_date")
    if publish_date:
        from datetime import date
        try:
            asset.publish_date = date.fromisoformat(publish_date)
        except ValueError:
            pass

    db.session.add(asset)
    db.session.commit()
    return _ok(asset.to_dict()), 201


@creatives_bp.route("/<asset_id>", methods=["GET"])
def get_asset(asset_id):
    asset = CreativeAsset.query.get(asset_id)
    if not asset:
        return _err("Asset not found", 404)
    return _ok(asset.to_dict())


@creatives_bp.route("/by-campaign/<campaign_id>", methods=["GET"])
def by_campaign(campaign_id):
    assets = CreativeAsset.query.filter_by(campaign_id=campaign_id).order_by(
        CreativeAsset.created_at.desc()
    ).all()
    return _ok([a.to_dict() for a in assets])


def _run_analysis_in_thread(app, asset_id: str) -> None:
    """Background worker that runs analysis under an app context."""
    with app.app_context():
        asset = CreativeAsset.query.get(asset_id)
        if asset:
            run_analysis(asset)


def _kickoff_analysis(asset_id: str) -> None:
    app = current_app._get_current_object()
    thread = threading.Thread(
        target=_run_analysis_in_thread,
        args=(app, asset_id),
        daemon=True,
    )
    thread.start()


@creatives_bp.route("/<asset_id>/analyze", methods=["POST"])
def analyze_asset(asset_id):
    """
    Trigger AI analysis of a creative asset.

    Marks the asset as processing, then runs the creative_analysis_service in
    a background thread. Poll GET /api/creatives/<asset_id> to read the result.
    """
    asset = CreativeAsset.query.get(asset_id)
    if not asset:
        return _err("Asset not found", 404)

    asset.analysis_status = "processing"
    asset.analysis_error = None
    db.session.commit()

    _kickoff_analysis(asset_id)

    return _ok({
        "asset_id": asset_id,
        "status": "processing",
        "message": "Analysis started. Poll GET /api/creatives/<asset_id> for result.",
    })


@creatives_bp.route("/batch-analyze", methods=["POST"])
def batch_analyze():
    data = request.get_json(silent=True) or {}
    asset_ids = data.get("asset_ids", [])
    if not asset_ids:
        return _err("'asset_ids' list is required")

    queued = []
    for aid in asset_ids:
        asset = CreativeAsset.query.get(aid)
        if asset:
            asset.analysis_status = "processing"
            asset.analysis_error = None
            queued.append(aid)
    db.session.commit()

    for aid in queued:
        _kickoff_analysis(aid)

    return _ok({"queued": queued})


@creatives_bp.route("/<asset_id>/tags", methods=["PATCH"])
def update_tags(asset_id):
    asset = CreativeAsset.query.get(asset_id)
    if not asset:
        return _err("Asset not found", 404)
    data = request.get_json(silent=True) or {}
    tags = data.get("tags")
    if not isinstance(tags, list):
        return _err("'tags' must be a list")
    asset.tags = tags
    db.session.commit()
    return _ok(asset.to_dict())
