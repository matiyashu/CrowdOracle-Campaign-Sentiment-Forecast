"""
Marketing report service — generates a narrative campaign report from the
dashboard_service payload using the configured report_writer LLM provider.

Outputs both structured JSON sections and a rendered markdown document so the
frontend can show either form and the user can download the markdown directly.
"""

import json
import logging
import re
from datetime import datetime, timezone
from typing import Dict, List

from .dashboard_service import build_dashboard
from .llm.registry import get_provider

logger = logging.getLogger("bigbrother.services.marketing_report")

SYSTEM_PROMPT = """You are a senior marketing analyst writing a concise campaign impact report.
Produce STRICT JSON matching the schema below. No prose outside the JSON.

Schema:
{
  "executive_summary": "2-3 sentence top-line takeaway grounded in the numbers provided.",
  "conversation_signal": "one paragraph on volume, top themes, rising terms.",
  "sentiment_read": "one paragraph on positive/negative split, aspect risks.",
  "creative_performance": "one paragraph on which creatives resonate and why.",
  "business_outcome": "one paragraph or 'Business metrics not available — impact score is a partial estimate.'",
  "recommendations": [
    {"priority": "high|medium|low", "action": "short imperative", "rationale": "one line"}
  ],
  "risks": ["short bullet", "..."],
  "next_steps": ["short bullet", "..."]
}

Rules:
- Ground every claim in the provided snapshot — never invent numbers.
- If a section has no data, say so explicitly.
- Keep each prose section under 120 words.
- Return 3-6 recommendations, 2-4 risks, 2-4 next_steps.
"""


def _strip_fences(raw: str) -> str:
    s = raw.strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?\s*", "", s)
        s = re.sub(r"\s*```$", "", s)
    return s


def _parse_json(raw: str) -> Dict:
    try:
        return json.loads(_strip_fences(raw))
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    return {"executive_summary": "LLM returned malformed JSON.", "_raw": raw}


def _compact_snapshot(dashboard: Dict) -> Dict:
    """Reduce the dashboard payload to a token-efficient shape for the prompt."""
    sent = dashboard.get("sentiment", {})
    imp = dashboard.get("impact", {})
    kw = dashboard.get("keywords", {})
    return {
        "campaign": {
            "name": dashboard["campaign"]["name"],
            "brand": dashboard["campaign"]["brand"],
            "objective": dashboard["campaign"].get("objective"),
            "markets": dashboard["campaign"].get("markets"),
            "channels": dashboard["campaign"].get("channels"),
        },
        "overview": dashboard.get("overview", {}),
        "impact": {
            "score": imp.get("impact_score"),
            "type": imp.get("impact_type"),
            "components": {
                k: {"score": v.get("score")} for k, v in (imp.get("component_scores") or {}).items()
            },
        },
        "sentiment_overall": sent.get("overall"),
        "sentiment_by_aspect": sent.get("by_aspect", [])[:8],
        "top_phrases": kw.get("top_phrases", [])[:10],
        "rising_terms": kw.get("rising_terms", [])[:8],
        "negative_linked": kw.get("negative_linked", [])[:8],
        "top_assets": imp.get("asset_scores", [])[:5],
    }


def _render_markdown(campaign: Dict, sections: Dict, dashboard: Dict) -> str:
    lines: List[str] = []
    lines.append(f"# Campaign Report — {campaign['name']}")
    lines.append(f"_{campaign['brand']} · generated {datetime.now(timezone.utc).isoformat()}_\n")
    ov = dashboard.get("overview", {})
    lines.append(f"**Impact Score:** {ov.get('impact_score', '—')} ({ov.get('impact_type', 'n/a')})")
    lines.append(f"**Mentions:** {ov.get('total_mentions', 0)} · "
                 f"Positive {round((ov.get('positive_share') or 0) * 100)}% · "
                 f"Negative {round((ov.get('negative_share') or 0) * 100)}%\n")

    def _section(title: str, body: str):
        if not body:
            return
        lines.append(f"## {title}")
        lines.append(body + "\n")

    _section("Executive Summary", sections.get("executive_summary", ""))
    _section("Conversation Signal", sections.get("conversation_signal", ""))
    _section("Sentiment Read", sections.get("sentiment_read", ""))
    _section("Creative Performance", sections.get("creative_performance", ""))
    _section("Business Outcome", sections.get("business_outcome", ""))

    recs = sections.get("recommendations") or []
    if recs:
        lines.append("## Recommendations")
        for r in recs:
            pri = (r.get("priority") or "medium").upper()
            lines.append(f"- **[{pri}]** {r.get('action', '')} — {r.get('rationale', '')}")
        lines.append("")

    risks = sections.get("risks") or []
    if risks:
        lines.append("## Risks")
        for r in risks:
            lines.append(f"- {r}")
        lines.append("")

    nexts = sections.get("next_steps") or []
    if nexts:
        lines.append("## Next Steps")
        for n in nexts:
            lines.append(f"- {n}")
        lines.append("")

    return "\n".join(lines)


def generate_report(campaign_id: str) -> Dict:
    """
    Build the dashboard → send a compact snapshot to the report_writer LLM →
    return structured sections + rendered markdown.
    """
    dashboard = build_dashboard(campaign_id)
    if "error" in dashboard:
        return dashboard

    snapshot = _compact_snapshot(dashboard)

    try:
        provider = get_provider("report_writer")
    except Exception as e:
        logger.warning("report_writer provider unavailable: %s", e)
        return {
            "campaign_id": campaign_id,
            "sections": {"executive_summary": "LLM provider not configured for report_writer."},
            "markdown": f"# {dashboard['campaign']['name']}\n\n_LLM provider not configured._\n",
            "snapshot": snapshot,
        }

    user_prompt = (
        "Write the campaign report as STRICT JSON matching the schema. "
        "Snapshot:\n" + json.dumps(snapshot, ensure_ascii=False, indent=2)
    )

    try:
        raw = provider.chat(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
        )
    except Exception as e:
        logger.exception("report LLM call failed")
        return {
            "campaign_id": campaign_id,
            "sections": {"executive_summary": f"LLM call failed: {e}"},
            "markdown": f"# {dashboard['campaign']['name']}\n\n_LLM call failed: {e}_\n",
            "snapshot": snapshot,
        }

    sections = _parse_json(raw)
    markdown = _render_markdown(dashboard["campaign"], sections, dashboard)

    return {
        "campaign_id": campaign_id,
        "campaign": dashboard["campaign"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sections": sections,
        "markdown": markdown,
        "snapshot": snapshot,
    }
