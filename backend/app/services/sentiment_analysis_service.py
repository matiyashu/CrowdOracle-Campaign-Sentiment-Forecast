"""
Sentiment analysis service — aggregates mention sentiment into the dashboard
shape: overall split, per-aspect breakdown, daily trend, emotion split.

Reads pre-computed sentiment from Mention rows (set by mention_ingestion_service
during enrichment). Falls back to a tiny lexical heuristic for rows that haven't
been enriched yet so the dashboard is never empty.
"""

import logging
from collections import Counter, defaultdict
from typing import Dict, List

from app.models.mention import Mention

logger = logging.getLogger("bigbrother.services.sentiment_analysis")

ASPECTS = ["price", "quality", "delivery", "ux", "offer", "creative", "creator", "brand_trust"]

_POS_LEX = {"love", "great", "amazing", "best", "perfect", "excellent", "awesome",
            "fantastic", "good", "happy", "smooth", "fast", "worth", "recommend",
            "bagus", "suka", "cinta", "mantap", "keren"}
_NEG_LEX = {"bad", "terrible", "awful", "worst", "hate", "trash", "scam", "broken",
            "slow", "expensive", "buggy", "fail", "disappointed", "regret",
            "buruk", "jelek", "mahal", "rusak", "kecewa"}


def _lexical_fallback(text: str) -> str:
    if not text:
        return "neutral"
    toks = {t.lower() for t in text.split()}
    pos = len(toks & _POS_LEX)
    neg = len(toks & _NEG_LEX)
    if pos > neg:
        return "positive"
    if neg > pos:
        return "negative"
    return "neutral"


def _bucket(m: Mention) -> str:
    return m.sentiment if m.sentiment in ("positive", "negative", "neutral") else _lexical_fallback(m.text)


def _share(part: int, total: int) -> float:
    return round(part / total, 3) if total else 0.0


def analyze_campaign(campaign_id: str) -> Dict:
    """
    Return the full sentiment dashboard payload for a campaign.
    """
    mentions = Mention.query.filter_by(campaign_id=campaign_id).all()
    total = len(mentions)
    if total == 0:
        return {
            "campaign_id": campaign_id,
            "overall": {"positive_share": 0, "negative_share": 0, "neutral_share": 0, "total": 0},
            "by_aspect": [],
            "by_day": [],
            "emotion_split": {},
            "language_split": {},
        }

    bucket_counts = Counter()
    aspect_buckets: Dict[str, Counter] = defaultdict(Counter)
    day_buckets: Dict[str, Counter] = defaultdict(Counter)
    emotion_counts = Counter()
    language_counts = Counter()

    for m in mentions:
        b = _bucket(m)
        bucket_counts[b] += 1

        if m.aspect:
            aspect_buckets[m.aspect][b] += 1

        if m.created_at_source:
            key = m.created_at_source.date().isoformat()
            day_buckets[key][b] += 1

        if m.emotion:
            emotion_counts[m.emotion] += 1
        if m.language:
            language_counts[m.language] += 1

    by_aspect: List[Dict] = []
    for aspect in sorted(aspect_buckets.keys()):
        counts = aspect_buckets[aspect]
        sub_total = sum(counts.values())
        by_aspect.append({
            "aspect": aspect,
            "total": sub_total,
            "positive_share": _share(counts["positive"], sub_total),
            "negative_share": _share(counts["negative"], sub_total),
            "neutral_share": _share(counts["neutral"], sub_total),
        })

    by_day: List[Dict] = []
    for day in sorted(day_buckets.keys()):
        counts = day_buckets[day]
        sub_total = sum(counts.values())
        by_day.append({
            "date": day,
            "total": sub_total,
            "positive": counts["positive"],
            "negative": counts["negative"],
            "neutral": counts["neutral"],
            "positive_share": _share(counts["positive"], sub_total),
            "negative_share": _share(counts["negative"], sub_total),
        })

    return {
        "campaign_id": campaign_id,
        "overall": {
            "total": total,
            "positive_share": _share(bucket_counts["positive"], total),
            "negative_share": _share(bucket_counts["negative"], total),
            "neutral_share": _share(bucket_counts["neutral"], total),
            "positive": bucket_counts["positive"],
            "negative": bucket_counts["negative"],
            "neutral": bucket_counts["neutral"],
        },
        "by_aspect": by_aspect,
        "by_day": by_day,
        "emotion_split": dict(emotion_counts),
        "language_split": dict(language_counts),
    }
