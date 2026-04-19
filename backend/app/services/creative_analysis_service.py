"""
Creative analysis service.

Pipeline:
    image → optional OCR (pytesseract) → vision LLM summary
    video → frame sample (moviepy) → vision LLM summary on first frame
            → optional transcription via the configured provider
    copy  → LLM hook/CTA/tone extraction

Each entry point updates the CreativeAsset row in place and returns it.
The functions are blocking; callers run them inside a background thread when
they want async behavior (see api/creatives.py).
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

from ..database import db
from ..models.creative_asset import CreativeAsset
from ..utils.logger import get_logger
from .llm.registry import get_provider

logger = get_logger("bigbrother.services.creative_analysis")


# ---- Prompts ---------------------------------------------------------------

VISION_PROMPT = (
    "You are analyzing a marketing creative. Return STRICT JSON with these keys: "
    '"visual_summary" (1-3 sentences describing what is shown), '
    '"cta" (the call-to-action visible in the image, or null), '
    '"detected_hooks" (array of short strings — emotional or attention hooks), '
    '"emotional_tone" (one of: aspirational, urgent, playful, trustworthy, '
    'fearful, celebratory, neutral), '
    '"detected_topics" (array of short topic tags), '
    '"brand_logo_present" (boolean), '
    '"offer_clarity_score" (float 0..1 — how clearly the offer/value is communicated). '
    "Only output JSON. No prose."
)

COPY_PROMPT_TEMPLATE = (
    "You are analyzing a marketing copy/ad text. Return STRICT JSON with: "
    '"visual_summary" (1-2 sentence summary of the message), '
    '"cta" (the call-to-action sentence, or null), '
    '"detected_hooks" (array of short strings), '
    '"emotional_tone" (one of: aspirational, urgent, playful, trustworthy, '
    'fearful, celebratory, neutral), '
    '"detected_topics" (array of short topic tags), '
    '"offer_clarity_score" (float 0..1). '
    "Only output JSON. No prose.\n\nCOPY:\n{copy_text}"
)


# ---- Helpers ---------------------------------------------------------------

def _parse_json_strict(raw: str) -> dict[str, Any]:
    """Parse model output, stripping ```json fences if present."""
    if not raw:
        return {}
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to extract the first {...} block
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    logger.warning("Could not parse model JSON: %s", text[:200])
    return {}


def _apply_analysis(asset: CreativeAsset, parsed: dict[str, Any]) -> None:
    """Copy parsed fields onto the SQLAlchemy row."""
    if not parsed:
        return
    if "visual_summary" in parsed:
        asset.visual_summary = parsed.get("visual_summary")
    if "cta" in parsed:
        asset.cta = parsed.get("cta")
    if "detected_hooks" in parsed:
        hooks = parsed.get("detected_hooks") or []
        asset.detected_hooks = hooks if isinstance(hooks, list) else []
    if "emotional_tone" in parsed:
        asset.emotional_tone = parsed.get("emotional_tone")
    if "detected_topics" in parsed:
        topics = parsed.get("detected_topics") or []
        asset.detected_topics = topics if isinstance(topics, list) else []
    if "brand_logo_present" in parsed:
        asset.brand_logo_present = bool(parsed.get("brand_logo_present"))
    if "offer_clarity_score" in parsed:
        try:
            asset.offer_clarity_score = float(parsed.get("offer_clarity_score"))
        except (TypeError, ValueError):
            asset.offer_clarity_score = None


def _ocr_image(path: str) -> str | None:
    """Best-effort OCR. Returns None if pytesseract or tesseract binary is missing."""
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        logger.info("pytesseract/Pillow not installed — skipping OCR")
        return None
    try:
        with Image.open(path) as img:
            text = pytesseract.image_to_string(img)
        text = text.strip()
        return text if text else None
    except Exception as e:
        logger.warning("OCR failed for %s: %s", path, e)
        return None


def _extract_video_frame(video_path: str) -> str | None:
    """Save the first usable frame to a sidecar PNG and return its path."""
    try:
        from moviepy.editor import VideoFileClip
    except ImportError:
        logger.info("moviepy not installed — skipping video frame extraction")
        return None
    try:
        with VideoFileClip(video_path) as clip:
            t = min(1.0, clip.duration / 2)
            frame_path = f"{video_path}.frame.png"
            clip.save_frame(frame_path, t=t)
        return frame_path
    except Exception as e:
        logger.warning("Frame extraction failed for %s: %s", video_path, e)
        return None


# ---- Public API ------------------------------------------------------------

def analyze_image(asset: CreativeAsset) -> CreativeAsset:
    """Run OCR + vision LLM on an image asset and persist results."""
    if not asset.file_path or not os.path.exists(asset.file_path):
        asset.analysis_status = "failed"
        asset.analysis_error = "File missing on disk"
        db.session.commit()
        return asset

    asset.analysis_status = "processing"
    asset.analysis_error = None
    db.session.commit()

    try:
        ocr = _ocr_image(asset.file_path)
        if ocr:
            asset.ocr_text = ocr

        provider = get_provider("creative_vision")
        raw = provider.analyze_image(asset.file_path, VISION_PROMPT)
        parsed = _parse_json_strict(raw)
        _apply_analysis(asset, parsed)

        asset.analysis_status = "done"
        db.session.commit()
        return asset
    except Exception as e:
        logger.exception("Image analysis failed for %s", asset.id)
        asset.analysis_status = "failed"
        asset.analysis_error = str(e)
        db.session.commit()
        return asset


def analyze_video(asset: CreativeAsset) -> CreativeAsset:
    """Sample one frame, run vision LLM on it, optionally transcribe audio."""
    if not asset.file_path or not os.path.exists(asset.file_path):
        asset.analysis_status = "failed"
        asset.analysis_error = "File missing on disk"
        db.session.commit()
        return asset

    asset.analysis_status = "processing"
    asset.analysis_error = None
    db.session.commit()

    try:
        provider = get_provider("creative_vision")

        frame_path = _extract_video_frame(asset.file_path)
        if frame_path and os.path.exists(frame_path):
            try:
                raw = provider.analyze_image(frame_path, VISION_PROMPT)
                parsed = _parse_json_strict(raw)
                _apply_analysis(asset, parsed)
            finally:
                try:
                    os.remove(frame_path)
                except OSError:
                    pass

        # Optional transcription — providers that don't support it raise NotImplementedError
        try:
            transcript_provider = get_provider("transcript")
            transcript = transcript_provider.transcribe(asset.file_path)
            if transcript:
                asset.transcript = transcript.strip() or None
        except NotImplementedError:
            logger.info("Transcription not supported by configured provider; skipping")
        except Exception as e:
            logger.warning("Transcription failed for %s: %s", asset.id, e)

        asset.analysis_status = "done"
        db.session.commit()
        return asset
    except Exception as e:
        logger.exception("Video analysis failed for %s", asset.id)
        asset.analysis_status = "failed"
        asset.analysis_error = str(e)
        db.session.commit()
        return asset


def analyze_copy(asset: CreativeAsset) -> CreativeAsset:
    """Read a text/markdown asset and run hook/CTA/tone extraction."""
    if not asset.file_path or not os.path.exists(asset.file_path):
        asset.analysis_status = "failed"
        asset.analysis_error = "File missing on disk"
        db.session.commit()
        return asset

    asset.analysis_status = "processing"
    asset.analysis_error = None
    db.session.commit()

    try:
        from ..utils.file_parser import _read_text_with_fallback
        copy_text = _read_text_with_fallback(asset.file_path)
        # Persist the raw text in ocr_text so dashboards have a single field to read from
        asset.ocr_text = copy_text

        provider = get_provider("creative_vision")
        prompt = COPY_PROMPT_TEMPLATE.format(copy_text=copy_text[:4000])
        raw = provider.chat(
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        parsed = _parse_json_strict(raw)
        _apply_analysis(asset, parsed)

        asset.analysis_status = "done"
        db.session.commit()
        return asset
    except Exception as e:
        logger.exception("Copy analysis failed for %s", asset.id)
        asset.analysis_status = "failed"
        asset.analysis_error = str(e)
        db.session.commit()
        return asset


def analyze_asset(asset: CreativeAsset) -> CreativeAsset:
    """Dispatch on asset_type."""
    if asset.asset_type == "image":
        return analyze_image(asset)
    if asset.asset_type == "video":
        return analyze_video(asset)
    if asset.asset_type in ("copy", "document"):
        return analyze_copy(asset)
    asset.analysis_status = "failed"
    asset.analysis_error = f"Unsupported asset_type: {asset.asset_type}"
    db.session.commit()
    return asset
