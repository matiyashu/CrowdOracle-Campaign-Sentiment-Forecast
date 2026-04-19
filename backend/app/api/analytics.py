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
import threading

from flask import Blueprint, current_app, jsonify, request

from app.database import db
from app.models.campaign import Campaign
from app.models.performance_metric import PerformanceMetric
from app.services.mention_ingestion_service import (
    enrich_mentions as run_enrichment,
    ingest_mentions,
)
from app.services import (
    dashboard_service,
    impact_analysis_service,
    keyword_analysis_service,
    marketing_report_service,
    sentiment_analysis_service,
)

analytics_bp = Blueprint("analytics", __name__)


def _ok(data=None, **kwargs):
    return jsonify({"success": True, "data": data, **kwargs})


def _err(message: str, status: int = 400):
    return jsonify({"success": False, "error": message}), status


# ── Mention upload ────────────────────────────────────────────────────────────

def _run_enrichment_in_thread(app, campaign_id: str, mention_ids: list[str]) -> None:
    with app.app_context():
        run_enrichment(campaign_id, mention_ids=mention_ids)


@analytics_bp.route("/mentions/upload", methods=["POST"])
def upload_mentions():
    """
    Accept a CSV/XLSX of mentions and persist them via mention_ingestion_service.

    Required columns: text
    Optional: source_platform, author_handle, created_at, engagement_count, url

    Form params:
        campaign_id (required)
        enrich = "true" | "false" (default "false") — when true, queues a background
                 LLM enrichment pass over the newly inserted rows.
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

    data_folder = current_app.config["DATA_UPLOAD_FOLDER"]
    os.makedirs(data_folder, exist_ok=True)

    try:
        summary = ingest_mentions(campaign_id, file.read(), file.filename)
    except Exception as e:
        db.session.rollback()
        return _err(f"Failed to parse file: {e}", 500)

    if summary.get("errors"):
        return _err("; ".join(summary["errors"]))

    enrich_flag = (request.form.get("enrich") or "").lower() == "true"
    if enrich_flag and summary.get("mention_ids"):
        app = current_app._get_current_object()
        thread = threading.Thread(
            target=_run_enrichment_in_thread,
            args=(app, campaign_id, summary["mention_ids"]),
            daemon=True,
        )
        thread.start()
        summary["enrichment_queued"] = True

    return _ok(summary)


@analytics_bp.route("/mentions/enrich", methods=["POST"])
def enrich_uploaded_mentions():
    """
    Trigger background LLM enrichment for a campaign's mentions.

    Request (JSON):
        {
          "campaign_id": "...",
          "mention_ids": ["...", "..."]   // optional; omit to enrich all
        }
    """
    data = request.get_json(silent=True) or {}
    campaign_id = data.get("campaign_id")
    if not campaign_id:
        return _err("'campaign_id' is required")
    if not Campaign.query.get(campaign_id):
        return _err("Campaign not found", 404)

    mention_ids = data.get("mention_ids") or []

    app = current_app._get_current_object()
    thread = threading.Thread(
        target=_run_enrichment_in_thread,
        args=(app, campaign_id, mention_ids),
        daemon=True,
    )
    thread.start()
    return _ok({"campaign_id": campaign_id, "enrichment_queued": True,
                "mention_ids": mention_ids or "all"})


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
    Assemble the full dashboard payload for a campaign via dashboard_service.
    """
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return _err("Campaign not found", 404)

    payload = dashboard_service.build_dashboard(campaign_id)
    if "error" in payload:
        return _err(payload["error"], 404)
    return _ok(payload)


@analytics_bp.route("/keywords/<campaign_id>", methods=["GET"])
def get_keywords(campaign_id):
    """Run keyword_analysis_service for the campaign."""
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return _err("Campaign not found", 404)
    return _ok(keyword_analysis_service.analyze_campaign(campaign_id))


@analytics_bp.route("/sentiment/<campaign_id>", methods=["GET"])
def get_sentiment(campaign_id):
    """Run sentiment_analysis_service for the campaign."""
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return _err("Campaign not found", 404)
    return _ok(sentiment_analysis_service.analyze_campaign(campaign_id))


@analytics_bp.route("/impact/<campaign_id>", methods=["GET"])
def get_impact(campaign_id):
    """Run impact_analysis_service for the campaign."""
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return _err("Campaign not found", 404)
    payload = impact_analysis_service.analyze_campaign(campaign_id)
    if "error" in payload:
        return _err(payload["error"], 404)
    return _ok(payload)


@analytics_bp.route("/report/generate", methods=["POST"])
def generate_report():
    """
    Generate a narrative marketing report from the dashboard snapshot using the
    report_writer LLM. Synchronous — returns structured sections + markdown.

    Request (JSON): {"campaign_id": "..."}
    """
    data = request.get_json(silent=True) or {}
    campaign_id = data.get("campaign_id")
    if not campaign_id:
        return _err("'campaign_id' is required")
    if not Campaign.query.get(campaign_id):
        return _err("Campaign not found", 404)

    report = marketing_report_service.generate_report(campaign_id)
    if "error" in report:
        return _err(report["error"], 404)
    return _ok(report)


@analytics_bp.route("/dashboard/<campaign_id>/export.md", methods=["GET"])
def export_dashboard_markdown(campaign_id):
    """
    Export the dashboard as a markdown snapshot (no LLM, pure data rendering).
    Useful for offline review, copy-paste into decks, or light-weight reporting.
    """
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return _err("Campaign not found", 404)

    payload = dashboard_service.build_dashboard(campaign_id)
    md = _render_dashboard_markdown(payload)
    return (md, 200, {"Content-Type": "text/markdown; charset=utf-8",
                      "Content-Disposition": f'attachment; filename="campaign-{campaign_id}.md"'})


def _render_dashboard_markdown(d: dict) -> str:
    c = d["campaign"]
    ov = d.get("overview", {})
    sent = d.get("sentiment", {}).get("overall", {})
    kw = d.get("keywords", {})
    imp = d.get("impact", {})
    recs = d.get("recommendations", [])

    lines = [
        f"# {c['name']} — {c['brand']}",
        f"_Objective: {c.get('objective') or '—'}_\n",
        "## Overview",
        f"- **Mentions:** {ov.get('total_mentions', 0)}",
        f"- **Creatives:** {ov.get('total_assets', 0)}",
        f"- **Sentiment:** {round((sent.get('positive_share') or 0) * 100)}% positive · "
        f"{round((sent.get('negative_share') or 0) * 100)}% negative · "
        f"{round((sent.get('neutral_share') or 0) * 100)}% neutral",
        f"- **Impact Score:** {ov.get('impact_score', '—')} ({ov.get('impact_type', 'n/a')})",
        f"- **Top Theme:** {ov.get('top_theme') or '—'}",
        f"- **Biggest Risk:** {ov.get('biggest_risk') or '—'}\n",
    ]

    if kw.get("top_phrases"):
        lines.append("## Top Phrases")
        for p in kw["top_phrases"][:15]:
            lines.append(f"- {p['phrase']} ({p['count']})")
        lines.append("")

    if kw.get("rising_terms"):
        lines.append("## Rising Terms")
        for r in kw["rising_terms"][:10]:
            lines.append(f"- {r['term']} +{round(r['growth'] * 100)}% ({r['first_half']} → {r['second_half']})")
        lines.append("")

    if kw.get("negative_linked"):
        lines.append("## Risk Terms")
        for r in kw["negative_linked"][:10]:
            lines.append(f"- {r['term']} ({r['negative_count']} negative)")
        lines.append("")

    if imp.get("asset_scores"):
        lines.append("## Creative Scoreboard")
        for a in imp["asset_scores"][:15]:
            lines.append(f"- **{a.get('filename') or a['asset_id'][:8]}** "
                         f"({a['asset_type']}/{a.get('channel') or '—'}) — score {a['score']}, "
                         f"+{a['positive']} / −{a['negative']} over {a['mention_count']} mentions")
        lines.append("")

    if recs:
        lines.append("## Recommendations")
        for r in recs:
            lines.append(f"- **[{r['bucket'].upper()}]** {r['title']} — {r['detail']}")
        lines.append("")

    return "\n".join(lines)


# ── helpers ───────────────────────────────────────────────────────────────────

def _safe_float(value) -> float | None:
    try:
        return float(value) if value is not None and str(value).strip() != "" else None
    except (ValueError, TypeError):
        return None
