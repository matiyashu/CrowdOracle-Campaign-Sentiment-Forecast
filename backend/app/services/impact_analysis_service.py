"""
Impact analysis service — computes a transparent campaign impact score from
mentions + sentiment + performance metrics.

Score formula (0–100):
    Conversation       (35%) — mention volume + topic penetration + sentiment shift
    Creative resonance (25%) — per-asset positive-mention correlation
    Business outcome   (20%) — CTR + CVR + ROAS (skipped if no data → score becomes partial_estimate)
    Sentiment quality  (20%) — positive share minus negative concentration risk

Each component returns its own sub-score so the dashboard can show the breakdown.
"""

import logging
from collections import Counter
from typing import Dict, List

from app.models.campaign import Campaign
from app.models.creative_asset import CreativeAsset
from app.models.mention import Mention
from app.models.performance_metric import PerformanceMetric

from .sentiment_analysis_service import _bucket as _sentiment_bucket

logger = logging.getLogger("bigbrother.services.impact_analysis")


def _clamp(v: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, v))


def _conversation_score(mentions: List[Mention]) -> Dict:
    if not mentions:
        return {"score": 0.0, "mention_volume": 0, "unique_topics": 0, "sentiment_shift": 0.0}

    volume = len(mentions)
    # Volume scaled: 0 → 0, 50 → 50, 250 → 100 (logarithmic-ish via piecewise)
    if volume <= 50:
        vol_score = volume * 1.0
    elif volume <= 250:
        vol_score = 50 + (volume - 50) * 0.25
    else:
        vol_score = min(100, 100 + (volume - 250) * 0.02)

    # Topic penetration: count of distinct extracted_topics across mentions
    topic_counter: Counter = Counter()
    for m in mentions:
        for t in (m.extracted_topics or []):
            topic_counter[str(t).lower()] += 1
    unique_topics = len(topic_counter)
    topic_score = min(100, unique_topics * 4.0)  # 25 topics → 100

    # Sentiment shift: positive share in second half vs first half
    dated = [m for m in mentions if m.created_at_source]
    shift = 0.0
    if len(dated) >= 6:
        dated.sort(key=lambda m: m.created_at_source)
        mid = len(dated) // 2
        first, second = dated[:mid], dated[mid:]

        def pos_share(rows: List[Mention]) -> float:
            if not rows:
                return 0.0
            pos = sum(1 for r in rows if _sentiment_bucket(r) == "positive")
            return pos / len(rows)

        shift = pos_share(second) - pos_share(first)
    shift_score = _clamp(50 + shift * 100)

    score = _clamp(vol_score * 0.5 + topic_score * 0.25 + shift_score * 0.25)
    return {
        "score": round(score, 1),
        "mention_volume": volume,
        "unique_topics": unique_topics,
        "sentiment_shift": round(shift, 3),
    }


def _creative_resonance(mentions: List[Mention], assets: List[CreativeAsset]) -> Dict:
    if not assets:
        return {"score": 0.0, "asset_scores": []}

    by_asset: Dict[str, Dict[str, int]] = {a.id: {"positive": 0, "negative": 0, "neutral": 0, "total": 0}
                                            for a in assets}
    for m in mentions:
        if m.linked_asset_id and m.linked_asset_id in by_asset:
            slot = by_asset[m.linked_asset_id]
            slot["total"] += 1
            slot[_sentiment_bucket(m)] += 1

    asset_scores: List[Dict] = []
    for a in assets:
        slot = by_asset[a.id]
        if slot["total"] == 0:
            asset_score = 50.0  # no data → neutral baseline
        else:
            pos_share = slot["positive"] / slot["total"]
            neg_share = slot["negative"] / slot["total"]
            asset_score = _clamp(50 + (pos_share - neg_share) * 50 +
                                 min(slot["total"] * 2, 20))
        asset_scores.append({
            "asset_id": a.id,
            "asset_type": a.asset_type,
            "channel": a.channel,
            "filename": a.original_filename,
            "mention_count": slot["total"],
            "positive": slot["positive"],
            "negative": slot["negative"],
            "score": round(asset_score, 1),
        })

    asset_scores.sort(key=lambda r: r["score"], reverse=True)
    avg = sum(r["score"] for r in asset_scores) / len(asset_scores) if asset_scores else 0.0
    return {"score": round(avg, 1), "asset_scores": asset_scores}


def _business_outcome(metrics: List[PerformanceMetric]) -> Dict:
    if not metrics:
        return {"score": None, "available": False, "ctr": None, "cvr": None, "roas": None}

    ctrs = [m.ctr for m in metrics if m.ctr is not None]
    cvrs = [m.cvr for m in metrics if m.cvr is not None]
    roases = [m.roas for m in metrics if m.roas is not None]

    avg_ctr = sum(ctrs) / len(ctrs) if ctrs else None
    avg_cvr = sum(cvrs) / len(cvrs) if cvrs else None
    avg_roas = sum(roases) / len(roases) if roases else None

    # Industry rough benchmarks for normalization
    ctr_score = _clamp((avg_ctr / 0.03) * 100) if avg_ctr is not None else None  # 3% CTR = 100
    cvr_score = _clamp((avg_cvr / 0.05) * 100) if avg_cvr is not None else None  # 5% CVR = 100
    roas_score = _clamp((avg_roas / 4.0) * 100) if avg_roas is not None else None  # 4x ROAS = 100

    sub_scores = [s for s in (ctr_score, cvr_score, roas_score) if s is not None]
    final = round(sum(sub_scores) / len(sub_scores), 1) if sub_scores else None

    return {
        "score": final,
        "available": final is not None,
        "ctr": avg_ctr,
        "cvr": avg_cvr,
        "roas": avg_roas,
    }


def _sentiment_quality(mentions: List[Mention]) -> Dict:
    if not mentions:
        return {"score": 0.0, "positive_share": 0, "negative_share": 0, "risk_concentration": 0}

    counts = Counter(_sentiment_bucket(m) for m in mentions)
    total = len(mentions)
    pos_share = counts["positive"] / total
    neg_share = counts["negative"] / total

    # Risk concentration: max share of negative mentions on any single aspect
    aspect_neg = Counter()
    aspect_total = Counter()
    for m in mentions:
        if m.aspect:
            aspect_total[m.aspect] += 1
            if _sentiment_bucket(m) == "negative":
                aspect_neg[m.aspect] += 1
    concentration = 0.0
    for aspect, neg in aspect_neg.items():
        if aspect_total[aspect] >= 3:
            concentration = max(concentration, neg / aspect_total[aspect])

    score = _clamp(pos_share * 100 - neg_share * 60 - concentration * 25 + 30)
    return {
        "score": round(score, 1),
        "positive_share": round(pos_share, 3),
        "negative_share": round(neg_share, 3),
        "risk_concentration": round(concentration, 3),
    }


def _recommendations(component_scores: Dict, asset_scores: List[Dict]) -> List[Dict]:
    recs: List[Dict] = []

    # Scale: top-performing assets
    top_assets = [a for a in asset_scores if a["score"] >= 70 and a["mention_count"] >= 3][:3]
    for a in top_assets:
        recs.append({
            "bucket": "scale",
            "title": f"Scale {a['asset_type']} on {a['channel'] or 'main channel'}",
            "detail": f"Asset {a['filename']} earns {a['score']}/100 from {a['mention_count']} mentions.",
            "asset_id": a["asset_id"],
        })

    # Optimize: mid-tier assets with positive bias
    mid_assets = [a for a in asset_scores if 50 <= a["score"] < 70 and a["mention_count"] >= 2][:3]
    for a in mid_assets:
        recs.append({
            "bucket": "optimize",
            "title": f"Optimize {a['asset_type']} {a['filename']}",
            "detail": f"Promising signal but mixed; iterate hook or CTA. Score {a['score']}.",
            "asset_id": a["asset_id"],
        })

    # Rework: low scorers
    low_assets = [a for a in asset_scores if a["score"] < 40 and a["mention_count"] >= 2][:3]
    for a in low_assets:
        recs.append({
            "bucket": "rework",
            "title": f"Rework {a['asset_type']} {a['filename']}",
            "detail": f"Negative-leaning conversation ({a['negative']} negatives). Consider redesign.",
            "asset_id": a["asset_id"],
        })

    # Investigate: business signal missing or sentiment quality low
    if not component_scores.get("business", {}).get("available"):
        recs.append({
            "bucket": "investigate",
            "title": "Upload performance metrics",
            "detail": "Without spend/CTR/CVR data, impact score is a partial estimate. Import a CSV.",
        })
    sent_q = component_scores.get("sentiment", {})
    if sent_q.get("risk_concentration", 0) >= 0.4:
        recs.append({
            "bucket": "investigate",
            "title": "Negative sentiment concentrated on one aspect",
            "detail": f"Risk concentration {sent_q['risk_concentration']}. Inspect by-aspect chart and address root cause.",
        })

    return recs


def analyze_campaign(campaign_id: str) -> Dict:
    """
    Compute the full impact analysis payload for a campaign.
    """
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return {"error": "Campaign not found"}

    mentions = Mention.query.filter_by(campaign_id=campaign_id).all()
    assets = CreativeAsset.query.filter_by(campaign_id=campaign_id).all()
    metrics = PerformanceMetric.query.filter_by(campaign_id=campaign_id).all()

    conversation = _conversation_score(mentions)
    creative = _creative_resonance(mentions, assets)
    business = _business_outcome(metrics)
    sentiment = _sentiment_quality(mentions)

    if business["available"]:
        impact = (conversation["score"] * 0.35 +
                  creative["score"] * 0.25 +
                  business["score"] * 0.20 +
                  sentiment["score"] * 0.20)
        impact_type = "full"
    else:
        # Renormalize without business signal
        impact = (conversation["score"] * 0.45 +
                  creative["score"] * 0.30 +
                  sentiment["score"] * 0.25)
        impact_type = "partial_estimate"

    component_scores = {
        "conversation": conversation,
        "creative": creative,
        "business": business,
        "sentiment": sentiment,
    }

    return {
        "campaign_id": campaign_id,
        "impact_score": round(impact, 1),
        "impact_type": impact_type,
        "component_scores": component_scores,
        "asset_scores": creative["asset_scores"],
        "recommendations": _recommendations(component_scores, creative["asset_scores"]),
    }
