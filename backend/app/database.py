"""
Database initialization — SQLAlchemy instance shared across all models.
Import `db` from here everywhere instead of creating new instances.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """Bind db to the Flask app and create all tables."""
    db.init_app(app)
    with app.app_context():
        db.create_all()
