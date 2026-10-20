from __future__ import annotations

import json
import re
import unicodedata

from app.config import resource_path


def _load_terms() -> tuple[list[str], list[str]]:
    with resource_path("app/detection/terms.json").open(encoding="utf-8") as file:
        terms = json.load(file)
    return terms["domain_terms"], terms["promotion_terms"]


DOMAIN_TERMS, PROMOTION_TERMS = _load_terms()


def _contains_term(text: str, term: str) -> bool:
    normalized_term = unicodedata.normalize("NFKC", term).casefold()
    if normalized_term.isascii() and normalized_term.isalnum():
        return re.search(rf"(?<![a-z0-9]){re.escape(normalized_term)}(?![a-z0-9])", text) is not None
    return normalized_term in text


def has_advertising_context(raw_text: str) -> bool:
    """Return true only when a domain term and a promotion term co-occur."""
    normalized = unicodedata.normalize("NFKC", raw_text).casefold()
    has_domain = any(_contains_term(normalized, term) for term in DOMAIN_TERMS)
    has_promotion = any(_contains_term(normalized, term) for term in PROMOTION_TERMS)
    return has_domain and has_promotion
