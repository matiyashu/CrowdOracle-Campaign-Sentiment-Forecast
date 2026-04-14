"""
Campaign model — top-level marketing campaign workspace.
"""

import uuid
from datetime import datetime, timezone

from ..database import db


class Campaign(db.Model):
    __tablename__ = 'campaigns'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    brand = db.Column(db.String(255), nullable=False)
    objective = db.Column(db.String(255))
    markets = db.Column(db.JSON, default=list)       # e.g. ["ID", "MY"]
    channels = db.Column(db.JSON, default=list)      # e.g. ["Meta", "TikTok"]
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    tags = db.Column(db.JSON, default=list)
    status = db.Column(db.String(50), default='draft')  # draft | active | completed | archived
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    creative_assets = db.relationship('CreativeAsset', backref='campaign', lazy='dynamic',
                                      cascade='all, delete-orphan')
    mentions = db.relationship('Mention', backref='campaign', lazy='dynamic',
                               cascade='all, delete-orphan')
    performance_metrics = db.relationship('PerformanceMetric', backref='campaign', lazy='dynamic',
                                          cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'brand': self.brand,
            'objective': self.objective,
            'markets': self.markets or [],
            'channels': self.channels or [],
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'tags': self.tags or [],
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'asset_count': self.creative_assets.count(),
            'mention_count': self.mentions.count(),
        }
