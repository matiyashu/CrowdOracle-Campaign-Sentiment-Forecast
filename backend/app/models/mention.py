"""
Mention model — a single public mention/comment/post about a campaign.
Ingested via CSV/XLSX upload.
"""

import uuid
from datetime import datetime, timezone

from ..database import db


class Mention(db.Model):
    __tablename__ = 'mentions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = db.Column(db.String(36), db.ForeignKey('campaigns.id'), nullable=False)

    # Source data
    source_platform = db.Column(db.String(100))   # twitter | instagram | tiktok | reddit | review
    text = db.Column(db.Text, nullable=False)
    author_handle = db.Column(db.String(255))
    created_at_source = db.Column(db.DateTime)    # original publish time
    engagement_count = db.Column(db.Integer, default=0)
    url = db.Column(db.String(2048))

    # AI analysis outputs
    sentiment = db.Column(db.String(20))          # positive | neutral | negative
    sentiment_score = db.Column(db.Float)         # -1.0 to 1.0
    aspect = db.Column(db.String(100))            # price | quality | delivery | ux | offer | creative | creator | brand_trust
    emotion = db.Column(db.String(100))           # joy | anger | frustration | excitement | confusion
    language = db.Column(db.String(10))           # ISO 639-1 code
    extracted_topics = db.Column(db.JSON, default=list)
    linked_asset_id = db.Column(db.String(36), db.ForeignKey('creative_assets.id'), nullable=True)

    ingested_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'source_platform': self.source_platform,
            'text': self.text,
            'author_handle': self.author_handle,
            'created_at_source': self.created_at_source.isoformat() if self.created_at_source else None,
            'engagement_count': self.engagement_count,
            'url': self.url,
            'sentiment': self.sentiment,
            'sentiment_score': self.sentiment_score,
            'aspect': self.aspect,
            'emotion': self.emotion,
            'language': self.language,
            'extracted_topics': self.extracted_topics or [],
            'linked_asset_id': self.linked_asset_id,
            'ingested_at': self.ingested_at.isoformat() if self.ingested_at else None,
        }
