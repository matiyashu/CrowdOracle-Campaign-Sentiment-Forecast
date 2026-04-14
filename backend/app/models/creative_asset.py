"""
CreativeAsset model — uploaded marketing creative (image, video, copy, landing page).
"""

import uuid
from datetime import datetime, timezone

from ..database import db


class CreativeAsset(db.Model):
    __tablename__ = 'creative_assets'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = db.Column(db.String(36), db.ForeignKey('campaigns.id'), nullable=False)

    # File metadata
    original_filename = db.Column(db.String(512))
    file_path = db.Column(db.String(1024))
    asset_type = db.Column(db.String(50))   # image | video | copy | landing
    file_size_bytes = db.Column(db.BigInteger)
    mime_type = db.Column(db.String(128))

    # Campaign metadata
    channel = db.Column(db.String(100))     # Meta | TikTok | Google | etc.
    publish_date = db.Column(db.Date)
    market = db.Column(db.String(50))
    tags = db.Column(db.JSON, default=list)

    # AI analysis outputs
    ocr_text = db.Column(db.Text)
    transcript = db.Column(db.Text)
    visual_summary = db.Column(db.Text)
    cta = db.Column(db.String(512))
    detected_hooks = db.Column(db.JSON, default=list)
    emotional_tone = db.Column(db.String(100))
    detected_topics = db.Column(db.JSON, default=list)
    brand_logo_present = db.Column(db.Boolean)
    offer_clarity_score = db.Column(db.Float)

    analysis_status = db.Column(db.String(50), default='pending')  # pending | processing | done | failed
    analysis_error = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'original_filename': self.original_filename,
            'file_path': self.file_path,
            'asset_type': self.asset_type,
            'file_size_bytes': self.file_size_bytes,
            'mime_type': self.mime_type,
            'channel': self.channel,
            'publish_date': self.publish_date.isoformat() if self.publish_date else None,
            'market': self.market,
            'tags': self.tags or [],
            'ocr_text': self.ocr_text,
            'transcript': self.transcript,
            'visual_summary': self.visual_summary,
            'cta': self.cta,
            'detected_hooks': self.detected_hooks or [],
            'emotional_tone': self.emotional_tone,
            'detected_topics': self.detected_topics or [],
            'brand_logo_present': self.brand_logo_present,
            'offer_clarity_score': self.offer_clarity_score,
            'analysis_status': self.analysis_status,
            'analysis_error': self.analysis_error,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
