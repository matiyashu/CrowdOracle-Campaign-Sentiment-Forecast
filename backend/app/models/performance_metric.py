"""
PerformanceMetric model — daily/weekly business metrics for a campaign channel.
Ingested via CSV/XLSX upload.
"""

import uuid
from datetime import datetime, timezone

from ..database import db


class PerformanceMetric(db.Model):
    __tablename__ = 'performance_metrics'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = db.Column(db.String(36), db.ForeignKey('campaigns.id'), nullable=False)

    date = db.Column(db.Date, nullable=False)
    channel = db.Column(db.String(100))          # Meta | TikTok | Google | etc.
    market = db.Column(db.String(50))

    # Reach & cost
    spend = db.Column(db.Float, default=0)
    impressions = db.Column(db.BigInteger, default=0)
    reach = db.Column(db.BigInteger, default=0)

    # Engagement
    clicks = db.Column(db.BigInteger, default=0)
    ctr = db.Column(db.Float)                    # click-through rate (0.0–1.0)
    cpc = db.Column(db.Float)                    # cost per click
    engagements = db.Column(db.BigInteger, default=0)
    engagement_rate = db.Column(db.Float)

    # Conversions
    conversions = db.Column(db.BigInteger, default=0)
    cpa = db.Column(db.Float)                    # cost per acquisition
    cvr = db.Column(db.Float)                    # conversion rate
    revenue = db.Column(db.Float, default=0)
    roas = db.Column(db.Float)                   # return on ad spend

    ingested_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'date': self.date.isoformat() if self.date else None,
            'channel': self.channel,
            'market': self.market,
            'spend': self.spend,
            'impressions': self.impressions,
            'reach': self.reach,
            'clicks': self.clicks,
            'ctr': self.ctr,
            'cpc': self.cpc,
            'engagements': self.engagements,
            'engagement_rate': self.engagement_rate,
            'conversions': self.conversions,
            'cpa': self.cpa,
            'cvr': self.cvr,
            'revenue': self.revenue,
            'roas': self.roas,
            'ingested_at': self.ingested_at.isoformat() if self.ingested_at else None,
        }
