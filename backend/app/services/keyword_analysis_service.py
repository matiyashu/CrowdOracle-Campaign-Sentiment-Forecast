"""
Keyword analysis service — extracts top words, phrases, rising terms, and
negatively-linked terms from a campaign's mentions.

Pure-Python (NLTK optional). Designed to degrade gracefully when stopword
corpora aren't downloaded yet.
"""

import logging
import re
from collections import Counter
from datetime import datetime
from typing import Dict, List, Tuple

from app.models.mention import Mention

logger = logging.getLogger("bigbrother.services.keyword_analysis")

_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z\-']{1,}")

# Minimal multi-language stopword fallback so the service works without NLTK data.
_BASE_STOPWORDS = {
    # English
    "the", "a", "an", "and", "or", "but", "if", "while", "with", "to", "of", "in",
    "on", "for", "is", "are", "was", "were", "be", "been", "being", "this", "that",
    "these", "those", "it", "its", "as", "at", "by", "from", "have", "has", "had",
    "do", "does", "did", "you", "your", "yours", "we", "our", "ours", "they",
    "them", "their", "i", "me", "my", "mine", "he", "she", "his", "her", "him",
    "what", "which", "who", "whom", "so", "than", "then", "too", "very", "can",
    "will", "just", "not", "no", "yes", "also", "more", "most", "some", "any",
    "all", "about", "into", "out", "up", "down", "over", "under", "after", "before",
    # Indonesian / Malay (common conversational fillers)
    "yang", "dan", "di", "ke", "dari", "untuk", "dengan", "ini", "itu", "ada",
    "saya", "kamu", "dia", "kita", "kami", "mereka", "tidak", "bukan", "akan",
    "sudah", "sedang", "telah", "juga", "saja", "lagi", "lah", "kok", "deh",
}

_NEG_HINTS = {
    "bad", "terrible", "awful", "horrible", "worst", "hate", "trash", "scam",
    "broken", "slow", "expensive", "overpriced", "buggy", "fail", "failed",
    "disappointed", "regret", "useless", "ripoff", "boring", "ugly", "lousy",
    "buruk", "jelek", "mahal", "lambat", "rusak", "kecewa", "menyebalkan",
}


def _tokens(text: str) -> List[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text or "")]


def _stopwords() -> set:
    try:
        from nltk.corpus import stopwords  # type: ignore
        sw = set()
        for lang in ("english", "indonesian"):
            try:
                sw.update(stopwords.words(lang))
            except LookupError:
                pass
        return sw or _BASE_STOPWORDS
    except Exception:
        return _BASE_STOPWORDS


def _filtered(tokens: List[str], sw: set) -> List[str]:
    return [t for t in tokens if len(t) > 2 and t not in sw]


def _ngrams(tokens: List[str], n: int) -> List[str]:
    return [" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


def _split_by_midpoint(mentions: List[Mention]) -> Tuple[List[Mention], List[Mention]]:
    dated = [m for m in mentions if m.created_at_source]
    if len(dated) < 4:
        return [], []
    dated.sort(key=lambda m: m.created_at_source)
    mid = len(dated) // 2
    return dated[:mid], dated[mid:]


def analyze_campaign(campaign_id: str, top_n: int = 25) -> Dict:
    """
    Run keyword analysis for a campaign and return the dashboard payload.
    """
    mentions = Mention.query.filter_by(campaign_id=campaign_id).all()
    if not mentions:
        return {
            "campaign_id": campaign_id,
            "top_words": [],
            "top_phrases": [],
            "rising_terms": [],
            "negative_linked": [],
            "total_mentions": 0,
        }

    sw = _stopwords()

    word_counter: Counter = Counter()
    bigram_counter: Counter = Counter()
    trigram_counter: Counter = Counter()

    neg_token_counter: Counter = Counter()

    for m in mentions:
        toks = _filtered(_tokens(m.text or ""), sw)
        word_counter.update(toks)
        bigram_counter.update(_ngrams(toks, 2))
        trigram_counter.update(_ngrams(toks, 3))

        if m.sentiment == "negative":
            neg_token_counter.update(toks)

    # Negative-linked terms: tokens disproportionately appearing in negative mentions
    negative_linked = []
    for tok, neg_count in neg_token_counter.most_common(50):
        total = word_counter.get(tok, 1)
        share = neg_count / total if total else 0
        if neg_count >= 3 and share >= 0.4:
            negative_linked.append({"term": tok, "negative_count": neg_count,
                                    "total_count": total, "negative_share": round(share, 3)})

    # Rising terms: compare second-half to first-half frequency
    first, second = _split_by_midpoint(mentions)
    rising_terms = []
    if first and second:
        first_counter: Counter = Counter()
        second_counter: Counter = Counter()
        for m in first:
            first_counter.update(_filtered(_tokens(m.text or ""), sw))
        for m in second:
            second_counter.update(_filtered(_tokens(m.text or ""), sw))

        for tok, sc in second_counter.most_common(80):
            fc = first_counter.get(tok, 0)
            if sc < 3:
                continue
            growth = (sc - fc) / max(fc, 1)
            if growth >= 0.5:
                rising_terms.append({"term": tok, "first_half": fc, "second_half": sc,
                                     "growth": round(growth, 2)})
        rising_terms.sort(key=lambda r: r["growth"], reverse=True)
        rising_terms = rising_terms[:top_n]

    # Heuristic: pad negative_linked with explicit negative-hint matches
    for tok, count in word_counter.most_common(200):
        if tok in _NEG_HINTS and count >= 2 and not any(n["term"] == tok for n in negative_linked):
            negative_linked.append({"term": tok, "negative_count": count,
                                    "total_count": count, "negative_share": 1.0,
                                    "source": "lexicon"})

    return {
        "campaign_id": campaign_id,
        "top_words": [{"term": w, "count": c} for w, c in word_counter.most_common(top_n)],
        "top_phrases": (
            [{"phrase": p, "count": c, "n": 2} for p, c in bigram_counter.most_common(top_n)] +
            [{"phrase": p, "count": c, "n": 3} for p, c in trigram_counter.most_common(top_n // 2)]
        ),
        "rising_terms": rising_terms,
        "negative_linked": negative_linked[:top_n],
        "total_mentions": len(mentions),
    }
