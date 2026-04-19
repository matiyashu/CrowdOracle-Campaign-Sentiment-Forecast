"""
Configuration management.
Loads all settings from the .env file at the project root.
"""

import os
from dotenv import load_dotenv

# Load the .env file from the project root
# Path: BigBrother/.env  (relative to backend/app/config.py)
project_root_env = os.path.join(os.path.dirname(__file__), '../../.env')

if os.path.exists(project_root_env):
    load_dotenv(project_root_env, override=True)
else:
    # No .env at root — fall back to environment variables (production)
    load_dotenv(override=True)


class Config:
    """Flask configuration class"""

    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'bigbrother-secret-key')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

    # JSON: disable ASCII escaping so non-ASCII characters render directly (not as \uXXXX)
    JSON_AS_ASCII = False

    # LLM (unified OpenAI-compatible format)
    LLM_API_KEY = os.environ.get('LLM_API_KEY')
    LLM_BASE_URL = os.environ.get('LLM_BASE_URL', 'https://api.openai.com/v1')
    LLM_MODEL_NAME = os.environ.get('LLM_MODEL_NAME', 'gpt-4o-mini')

    # Zep Cloud knowledge graph
    ZEP_API_KEY = os.environ.get('ZEP_API_KEY')

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///crowdoracle.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # LLM Provider Registry
    DEFAULT_PROVIDER = os.environ.get('DEFAULT_PROVIDER', 'openai')
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

    # File upload
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500 MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../uploads')
    MEDIA_UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../uploads/media')
    DATA_UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../uploads/data')
    ALLOWED_EXTENSIONS = {
        'pdf', 'md', 'txt', 'markdown',       # Documents
        'png', 'jpg', 'jpeg', 'webp', 'gif',  # Images
        'mp4', 'mov', 'avi', 'mkv', 'webm',   # Videos
        'csv', 'xlsx', 'json',                 # Data exports
    }

    # Text processing
    DEFAULT_CHUNK_SIZE = 500
    DEFAULT_CHUNK_OVERLAP = 50

    # OASIS simulation
    OASIS_DEFAULT_MAX_ROUNDS = int(os.environ.get('OASIS_DEFAULT_MAX_ROUNDS', '10'))
    OASIS_SIMULATION_DATA_DIR = os.path.join(os.path.dirname(__file__), '../uploads/simulations')
    OASIS_TWITTER_ACTIONS = [
        'CREATE_POST', 'LIKE_POST', 'REPOST', 'FOLLOW', 'DO_NOTHING', 'QUOTE_POST'
    ]
    OASIS_REDDIT_ACTIONS = [
        'LIKE_POST', 'DISLIKE_POST', 'CREATE_POST', 'CREATE_COMMENT',
        'LIKE_COMMENT', 'DISLIKE_COMMENT', 'SEARCH_POSTS', 'SEARCH_USER',
        'TREND', 'REFRESH', 'DO_NOTHING', 'FOLLOW', 'MUTE'
    ]

    # Report Agent
    REPORT_AGENT_MAX_TOOL_CALLS = int(os.environ.get('REPORT_AGENT_MAX_TOOL_CALLS', '5'))
    REPORT_AGENT_MAX_REFLECTION_ROUNDS = int(os.environ.get('REPORT_AGENT_MAX_REFLECTION_ROUNDS', '2'))
    REPORT_AGENT_TEMPERATURE = float(os.environ.get('REPORT_AGENT_TEMPERATURE', '0.5'))

    @classmethod
    def validate(cls):
        """
        Validate required configuration values.

        Returns a list of warnings (non-fatal). BigBrother's marketing features
        route LLM calls through per-provider ProviderConfig DB records, so a
        missing LLM_API_KEY only blocks legacy simulation features. ZEP_API_KEY
        is likewise optional (only needed for knowledge-graph flows).
        """
        warnings = []
        if not cls.LLM_API_KEY:
            warnings.append("LLM_API_KEY is not set — legacy simulation features will fail until a provider is configured via the UI.")
        if not cls.ZEP_API_KEY:
            warnings.append("ZEP_API_KEY is not set — Zep knowledge-graph features will be unavailable.")
        return warnings
