"""
Mention ingestion service.

Parses a CSV/XLSX upload of public mentions and inserts Mention rows.
Optionally enriches each row in a background pass:
    - language detection via langdetect
    - sentiment + aspect + emotion + topics via the configured LLM provider

Returns an ingestion summary the caller can echo back to the API client.
"""

from __future__ import annotations

import json
import re
from io import BytesIO
from typing import Any

from ..database import db
from ..models.mention import Mention
from ..utils.logger import get_logger
from .llm.registry import get_provider

logger = get_logger("bigbrother.services.mention_ingestion")


REQUIRED_COLUMNS = {"text"}
OPTIONAL_COLUMNS = {
    "source_platform", "author_handle", "created_at", "engagement_count", "url"
}

SENTIMENT_PROMPT = (
    "You are an analyst classifying a single public mention about a marketing "
    "campaign. Return STRICT JSON with: "
    '"sentiment" (positive|negative|neutral), '
    '"sentiment_score" (float -1..1), '
    '"aspect" (one of: price, quality, delivery, ux, offer, creative, creator, '
    'brand_trust, other), '
    '"emotion" (joy|anger|frustration|excitement|confusion|trust|disappointment|neutral), '
    '"extracted_topics" (array of short topic tags). '
    "Only output JSON. No prose.\n\nMENTION:\n{text}"
)


# ---- Parsing ---------------------------------------------------------------

def parse_dataframe(file_bytes: bytes, filename: str):
    """Return a pandas DataFrame from CSV/XLSX bytes, with normalized columns."""
    import pandas as pd

    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    raw = BytesIO(file_bytes)
    if ext == "csv":
        df = pd.read_csv(raw)
    elif ext == "xlsx":
        df = pd.read_excel(raw)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df


def validate_columns(df) -> list[str]:
    """Return a list of error strings (empty if valid)."""
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        return [f"Missing required column: {col}" for col in sorted(missing)]
    return []


# ---- Ingestion -------------------------------------------------------------

def _row_to_mention(campaign_id: str, row: dict[str, Any]) -> Mention | None:
    text = str(row.get("text", "")).strip()
    if not text:
        return None

    import pandas as pd
    created_at_source = None
    raw_dt = row.get("created_at")
    if raw_dt is not None and str(raw_dt).strip():
        try:
            created_at_source = pd.to_datetime(raw_dt).to_pydatetime()
        except Exception:
            created_at_source = None

    try:
        engagement = int(row.get("engagement_count", 0) or 0)
    except (TypeError, ValueError):
        engagement = 0

    return Mention(
        campaign_id=campaign_id,
        source_platform=(str(row.get("source_platform", "")).strip() or None),
        text=text,
        author_handle=(str(row.get("author_handle", "")).strip() or None),
        created_at_source=created_at_source,
        engagement_count=engagement,
        url=(str(row.get("url", "")).strip() or None),
    )


def ingest_mentions(campaign_id: str, file_bytes: bytes, filename: str) -> dict[str, Any]:
    """Parse a file and insert Mention rows. Returns a summary dict."""
    df = parse_dataframe(file_bytes, filename)
    errors = validate_columns(df)
    if errors:
        return {"inserted": 0, "skipped": 0, "errors": errors}

    inserted = 0
    skipped = 0
    inserted_ids: list[str] = []

    for _, row in df.iterrows():
        mention = _row_to_mention(campaign_id, row.to_dict())
        if mention is None:
            skipped += 1
            continue
        db.session.add(mention)
        inserted += 1
        inserted_ids.append(mention.id)

    db.session.commit()
    return {
        "inserted": inserted,
        "skipped": skipped,
        "campaign_id": campaign_id,
        "mention_ids": inserted_ids,
        "errors": [],
    }


# ---- Enrichment ------------------------------------------------------------

def _detect_language(text: str) -> str | None:
    try:
        from langdetect import detect, DetectorFactory
        DetectorFactory.seed = 0
        return detect(text)
    except Exception:
        return None


def _parse_json_strict(raw: str) -> dict[str, Any]:
    if not raw:
        return {}
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    return {}


def enrich_mention(mention: Mention) -> Mention:
    """Run language detection + LLM sentiment/aspect/topics on a single Mention."""
    if not mention.text:
        return mention

    if not mention.language:
        mention.language = _detect_language(mention.text)

    try:
        provider = get_provider("sentiment")
        prompt = SENTIMENT_PROMPT.format(text=mention.text[:2000])
        raw = provider.chat(
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        parsed = _parse_json_strict(raw)

        if "sentiment" in parsed:
            mention.sentiment = parsed.get("sentiment")
        if "sentiment_score" in parsed:
            try:
                mention.sentiment_score = float(parsed.get("sentiment_score"))
            except (TypeError, ValueError):
                mention.sentiment_score = None
        if "aspect" in parsed:
            mention.aspect = parsed.get("aspect")
        if "emotion" in parsed:
            mention.emotion = parsed.get("emotion")
        if "extracted_topics" in parsed:
            topics = parsed.get("extracted_topics") or []
            mention.extracted_topics = topics if isinstance(topics, list) else []

        db.session.commit()
    except Exception as e:
        logger.warning("Mention enrichment failed for %s: %s", mention.id, e)
        db.session.rollback()

    return mention


def enrich_mentions(campaign_id: str, mention_ids: list[str] | None = None) -> dict[str, Any]:
    """Run enrichment over all (or a specified subset of) a campaign's mentions."""
    query = Mention.query.filter_by(campaign_id=campaign_id)
    if mention_ids:
        query = query.filter(Mention.id.in_(mention_ids))
    mentions = query.all()

    enriched = 0
    for mention in mentions:
        enrich_mention(mention)
        enriched += 1

    return {"enriched": enriched, "campaign_id": campaign_id}
