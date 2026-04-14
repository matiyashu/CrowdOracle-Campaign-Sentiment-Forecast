"""
Analytics API blueprint — mentions/performance ingestion and dashboard/scoring endpoints.

Sprint 1: upload stubs + dashboard shell.
Sprint 2-3: full keyword/sentiment/impact analysis services wired in.

Endpoints:
    POST /api/analytics/mentions/upload
    POST /api/analytics/performance/upload
    GET  /api/analytics/dashboard/<campaign_id>
    GET  /api/analytics/keywords/<campaign_id>
    GET  /api/analytics/sentiment/<campaign_id>
    GET  /api/analytics/impact/<campaign_id>
    POST /api/analytics/report/generate
"""

import os

from flask import Blueprint, current_app, jsonify, request

from app.database import db
from app.models.campaign import Campaign
from app.models.mention import Mention
from app.models.performance_metric import PerformanceMetric

analytics_bp = Blueprint("analytics", __name__)


def _ok(data=None, **kwargs):
    return jsonify({"success": True, "data": data, **kwargs})


def _err(message: str, status: int = 400):
    return jsonify({"success": False, "error": message}), status


# ── Mention upload ────────────────────────────────────────────────────────────

@analytics_bp.route("/mentions/upload", methods=["POST"])
def upload_mentions():
    """
    Accept a CSV/XLSX of mentions and persist them.
    Required columns: text
    Optional: source_platform, author_handle, created_at, engagement_count, url
    """
    campaign_id = request.form.get("campaign_id")
    if not campaign_id:
        return _err("'campaign_id' is required")

    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return _err("Campaign not found", 404)

    file = request.files.get("file")
    if not file or not file.filename:
        return _err("No file provided")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ("csv", "xlsx"):
        return _err("Only CSV and XLSX files are supported")

    try:
        import pandas as pd
        from io import BytesIO

        raw = BytesIO(file.read())
        df = pd.read_csv(raw) if ext == "csv" else pd.read_excel(raw)
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

        if "text" not in df.columns:
            return _err("File must contain a 'text' column")

        data_folder = current_app.config["DATA_UPLOAD_FOLDER"]
        os.makedirs(data_folder, exist_ok=True)

        inserted = 0
        for _, row in df.iterrows():
            text = str(row.get("text", "")).strip()
            if not text:
                continue
            mention = Mention(
                campaign_id=campaign_id,
                source_platform=str(row.get("source_platform", "")) or None,
                text=text,
                author_handle=str(row.get("author_handle", "")) or None,
                engagement_count=int(row.get("engagement_count", 0) or 0),
                url=str(row.get("url", "")) or None,
            )
            db.session.add(mention)
            inserted += 1

        db.session.commit()
        return _ok({"inserted": inserted, "campaign_id": campaign_id})

    except Exception as e:
        db.session.rollback()
        return _err(f"Failed to parse file: {e}", 500)


# ── Performance upload ────────────────────────────────────────────────────────

@analytics_bp.route("/performance/upload", methods=["POST"])
def upload_performance():
    """
    Accept a CSV/XLSX of performance metrics.
    Required columns: date, channel
    """
    campaign_id = request.form.get("campaign_id")
    if not campaign_id:
        return _err("'campaign_id' is required")

    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return _err("Campaign not found", 404)

    file = request.files.get("file")
    if not file or not file.filename:
        return _err("No file provided")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ("csv", "xlsx"):
        return _err("Only CSV and XLSX files are supported")

    try:
        import pandas as pd
        from io import BytesIO
        from datetime import date as dt_date

        raw = BytesIO(file.read())
        df = pd.read_csv(raw) if ext == "csv" else pd.read_excel(raw)
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

        if "date" not in df.columns:
            return _err("File must contain a 'date' column")

        inserted = 0
        for _, row in df.iterrows():
            try:
                row_date = pd.to_datetime(row["date"]).date()
            except Exception:
                continue

            metric = PerformanceMetric(
                campaign_id=campaign_id,
                date=row_date,
                channel=str(row.get("channel", "")) or None,
                market=str(row.get("market", "")) or None,
                spend=float(row.get("spend", 0) or 0),
                impressions=int(row.get("impressions", 0) or 0),
                reach=int(row.get("reach", 0) or 0),
                clicks=int(row.get("clicks", 0) or 0),
                ctr=_safe_float(row.get("ctr")),
                cpc=_safe_float(row.get("cpc")),
                engagements=int(row.get("engagements", 0) or 0),
                engagement_rate=_safe_float(row.get("engagement_rate")),
                conversions=int(row.get("conversions", 0) or 0),
                cpa=_safe_float(row.get("cpa")),
                cvr=_safe_float(row.get("cvr")),
                revenue=float(row.get("revenue", 0) or 0),
                roas=_safe_float(row.get("roas")),
            )
            db.session.add(metric)
            inserted += 1

        db.session.commit()
        return _ok({"inserted": inserted, "campaign_id": campaign_id})

    except Exception as e:
        db.session.rollback()
        return _err(f"Failed to parse file: {e}", 500)


# ── Dashboard ─────────────────────────────────────────────────────────────────

@analytics_bp.route("/dashboard/<campaign_id>", methods=["GET"])
def get_dashboard(campaign_id):
    """
    Assemble the full dashboard payload for a campaign.
    Sprint 1: returns counts and stubs.
    Sprint 3: routes through keyword/sentiment/impact services.
    """
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return _err("Campaign not found", 404)

    total_mentions = Mention.query.filter_by(campaign_id=campaign_id).count()
    total_assets = campaign.creative_assets.count()

    return _ok({
        "campaign": campaign.to_dict(),
        "overview": {
            "total_mentions": total_mentions,
            "total_assets": total_assets,
            "positive_share": None,
            "negative_share": None,
            "neutral_share": None,
            "impact_score": None,
            "impact_type": "not_computed",
        },
        "top_keywords": [],
        "top_phrases": [],
        "sentiment_by_aspect": [],
        "sentiment_by_day": [],
        "creative_breakdown": [],
        "recommendations": [],
        "_note": "Full analysis available after Sprint 3 analytics services are wired in.",
    })


@analytics_bp.route("/keywords/<campaign_id>", methods=["GET"])
def get_keywords(campaign_id):
    """Sprint 3: will run keyword_analysis_service."""
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return _err("Campaign not found", 404)
    return _ok({"campaign_id": campaign_id, "top_words": [], "top_phrases": [],
                "rising_terms": [], "negative_linked": [],
                "_note": "Keyword analysis available in Sprint 3."})


@analytics_bp.route("/sentiment/<campaign_id>", methods=["GET"])
def get_sentiment(campaign_id):
    """Sprint 3: will run sentiment_analysis_service."""
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return _err("Campaign not found", 404)
    return _ok({"campaign_id": campaign_id, "overall": {}, "by_aspect": [],
                "by_day": [], "emotion_split": {},
                "_note": "Sentiment analysis available in Sprint 3."})


@analytics_bp.route("/impact/<campaign_id>", methods=["GET"])
def get_impact(campaign_id):
    """Sprint 3: will run impact_analysis_service."""
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return _err("Campaign not found", 404)
    return _ok({"campaign_id": campaign_id, "impact_score": None,
                "component_scores": {}, "asset_scores": [], "recommendations": [],
                "_note": "Impact scoring available in Sprint 3."})


@analytics_bp.route("/report/generate", methods=["POST"])
def generate_report():
    """Sprint 4: connect to MiroFish report pipeline with dashboard summary as seed."""
    return _ok({"_note": "Report generation integration available in Sprint 4."})


# ── helpers ───────────────────────────────────────────────────────────────────

def _safe_float(value) -> float | None:
    try:
        return float(value) if value is not None and str(value).strip() != "" else None
    except (ValueError, TypeError):
        return None
