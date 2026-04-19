"""
Dashboard service — composes the full dashboard JSON payload by calling
keyword, sentiment, and impact services and assembling them with overview cards.
"""

import logging
from typing import Dict

from app.models.campaign import Campaign
from app.models.creative_asset import CreativeAsset
from app.models.mention import Mention
from app.models.performance_metric import PerformanceMetric

from . import impact_analysis_service, keyword_analysis_service, sentiment_analysis_service

logger = logging.getLogger("bigbrother.services.dashboard")


def build_dashboard(campaign_id: str) -> Dict:
    """
    Build the dashboard payload consumed by DashboardView.vue.
    """
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return {"error": "Campaign not found"}

    keywords = keyword_analysis_service.analyze_campaign(campaign_id)
    sentiment = sentiment_analysis_service.analyze_campaign(campaign_id)
    impact = impact_analysis_service.analyze_campaign(campaign_id)

    total_mentions = Mention.query.filter_by(campaign_id=campaign_id).count()
    total_assets = CreativeAsset.query.filter_by(campaign_id=campaign_id).count()
    total_metrics = PerformanceMetric.query.filter_by(campaign_id=campaign_id).count()

    # Derive top theme + biggest risk for overview cards
    top_theme = keywords["top_phrases"][0]["phrase"] if keywords["top_phrases"] else (
        keywords["top_words"][0]["term"] if keywords["top_words"] else None
    )
    biggest_risk = keywords["negative_linked"][0]["term"] if keywords["negative_linked"] else None

    overview = {
        "total_mentions": total_mentions,
        "total_assets": total_assets,
        "performance_rows": total_metrics,
        "positive_share": sentiment["overall"].get("positive_share", 0),
        "negative_share": sentiment["overall"].get("negative_share", 0),
        "neutral_share": sentiment["overall"].get("neutral_share", 0),
        "impact_score": impact.get("impact_score"),
        "impact_type": impact.get("impact_type", "not_computed"),
        "top_theme": top_theme,
        "biggest_risk": biggest_risk,
    }

    return {
        "campaign": campaign.to_dict(),
        "overview": overview,
        "keywords": keywords,
        "sentiment": sentiment,
        "impact": impact,
        "recommendations": impact.get("recommendations", []),
    }
