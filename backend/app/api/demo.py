"""
Demo mode API — seeds pre-built campaign packages so first-time users
can explore every CrowdOracle feature without uploading anything.

Demo campaigns are tagged with 'demo' (via Campaign.tags) so they can
be listed, filtered, and reset without a schema migration.

Endpoints:
    GET    /api/demo/packages       list available demo packages
    POST   /api/demo/load            seed one package, return campaign_id
    POST   /api/demo/reset           delete every demo-tagged campaign
"""

from __future__ import annotations

import json
import random
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from flask import Blueprint, jsonify, request

from app.database import db
from app.models.campaign import Campaign
from app.models.creative_asset import CreativeAsset
from app.models.mention import Mention
from app.models.performance_metric import PerformanceMetric

demo_bp = Blueprint("demo", __name__)

PACKAGES_DIR = Path(__file__).resolve().parent.parent / "demo" / "packages"
DEMO_TAG = "demo"


def _ok(data=None, **kwargs):
    return jsonify({"success": True, "data": data, **kwargs})


def _err(message: str, status: int = 400):
    return jsonify({"success": False, "error": message}), status


def _load_package(package_id: str) -> dict | None:
    path = PACKAGES_DIR / f"{package_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _list_packages() -> list[dict]:
    if not PACKAGES_DIR.exists():
        return []
    result = []
    for f in sorted(PACKAGES_DIR.glob("*.json")):
        try:
            pkg = json.loads(f.read_text(encoding="utf-8"))
            result.append({
                "package_id": pkg.get("package_id") or f.stem,
                "title": pkg.get("title") or pkg.get("campaign", {}).get("name"),
                "description": pkg.get("description", ""),
                "brand": pkg.get("campaign", {}).get("brand"),
                "markets": pkg.get("campaign", {}).get("markets", []),
                "channels": pkg.get("campaign", {}).get("channels", []),
            })
        except Exception:
            continue
    return result


@demo_bp.route("/packages", methods=["GET"])
def list_packages():
    return _ok(_list_packages())


@demo_bp.route("/load", methods=["POST"])
def load_package():
    body = request.get_json(silent=True) or {}
    package_id = body.get("package_id")
    if not package_id:
        return _err("'package_id' is required")

    pkg = _load_package(package_id)
    if not pkg:
        return _err(f"Unknown demo package: {package_id}", 404)

    c_spec = pkg.get("campaign", {})
    tags = list(c_spec.get("tags", []))
    if DEMO_TAG not in tags:
        tags.append(DEMO_TAG)

    def _parse_date(v):
        if not v:
            return None
        try:
            return datetime.strptime(v, "%Y-%m-%d").date()
        except Exception:
            return None

    campaign = Campaign(
        name=c_spec.get("name", "Demo campaign"),
        brand=c_spec.get("brand", "Demo"),
        objective=c_spec.get("objective"),
        markets=c_spec.get("markets", []),
        channels=c_spec.get("channels", []),
        start_date=_parse_date(c_spec.get("start_date")),
        end_date=_parse_date(c_spec.get("end_date")),
        tags=tags,
        status=c_spec.get("status", "active"),
    )
    db.session.add(campaign)
    db.session.flush()

    asset_lookup: dict[str, str] = {}
    for idx, a in enumerate(pkg.get("creatives", [])):
        asset = CreativeAsset(
            campaign_id=campaign.id,
            original_filename=a.get("file") or f"demo_asset_{idx}",
            asset_type=a.get("asset_type", "image"),
            channel=a.get("channel"),
            ocr_text=a.get("ocr_text"),
            transcript=a.get("transcript"),
            visual_summary=a.get("visual_summary"),
            cta=a.get("cta"),
            detected_hooks=a.get("detected_hooks", []),
            emotional_tone=a.get("emotional_tone"),
            detected_topics=a.get("detected_topics", []),
            brand_logo_present=a.get("brand_logo_present"),
            offer_clarity_score=a.get("offer_clarity_score"),
            analysis_status="done",
        )
        db.session.add(asset)
        db.session.flush()
        if a.get("ref"):
            asset_lookup[a["ref"]] = asset.id

    for m in pkg.get("mentions", []):
        created = m.get("created_at_source")
        created_dt = None
        if created:
            try:
                created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            except Exception:
                created_dt = None

        mention = Mention(
            campaign_id=campaign.id,
            source_platform=m.get("source_platform", "twitter"),
            text=m.get("text", ""),
            author_handle=m.get("author_handle"),
            created_at_source=created_dt,
            engagement_count=int(m.get("engagement_count", 0)),
            url=m.get("url"),
            sentiment=m.get("sentiment"),
            sentiment_score=m.get("sentiment_score"),
            aspect=m.get("aspect"),
            emotion=m.get("emotion"),
            language=m.get("language", "en"),
            extracted_topics=m.get("extracted_topics", []),
            linked_asset_id=asset_lookup.get(m.get("linked_asset_ref")) if m.get("linked_asset_ref") else None,
        )
        db.session.add(mention)

    for p in pkg.get("performance", []):
        pdate = p.get("date")
        pdate_parsed = _parse_date(pdate)
        if not pdate_parsed:
            continue
        metric = PerformanceMetric(
            campaign_id=campaign.id,
            date=pdate_parsed,
            channel=p.get("channel"),
            market=p.get("market"),
            spend=float(p.get("spend", 0)),
            impressions=int(p.get("impressions", 0)),
            reach=int(p.get("reach", 0)),
            clicks=int(p.get("clicks", 0)),
            ctr=p.get("ctr"),
            cpc=p.get("cpc"),
            engagements=int(p.get("engagements", 0)),
            engagement_rate=p.get("engagement_rate"),
            conversions=int(p.get("conversions", 0)),
            cpa=p.get("cpa"),
            cvr=p.get("cvr"),
            revenue=float(p.get("revenue", 0)),
            roas=p.get("roas"),
        )
        db.session.add(metric)

    db.session.commit()
    return _ok({
        "campaign_id": campaign.id,
        "campaign": campaign.to_dict(),
        "package_id": package_id,
    }), 201


@demo_bp.route("/reset", methods=["POST"])
def reset_demo():
    body = request.get_json(silent=True) or {}
    target = body.get("campaign_id")

    if target:
        c = Campaign.query.get(target)
        if not c or DEMO_TAG not in (c.tags or []):
            return _err("Not a demo campaign.", 404)
        db.session.delete(c)
        db.session.commit()
        return _ok({"deleted": [target]})

    demo_campaigns = [c for c in Campaign.query.all() if DEMO_TAG in (c.tags or [])]
    ids = [c.id for c in demo_campaigns]
    for c in demo_campaigns:
        db.session.delete(c)
    db.session.commit()
    return _ok({"deleted": ids})
