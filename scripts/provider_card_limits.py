"""Limits for all-providers Card body descriptions.

Keep new and edited provider cards at or under this length so the grid stays
scannable. Integration submission automation and unit tests share this value.
"""

from __future__ import annotations

import re
from pathlib import Path

# One short factual sentence for the all-providers card grid.
PROVIDER_CARD_DESCRIPTION_MAX_LEN = 160

CARD_BODY_RE = re.compile(
    r'<Card\s+title="(?P<title>[^"]+)"[^>]*>\s*(?P<body>.*?)\s*</Card>',
    re.S,
)

ALL_PROVIDERS_PATHS = (
    Path("src/oss/python/integrations/providers/all_providers.mdx"),
    Path("src/oss/javascript/integrations/providers/all_providers.mdx"),
)


def iter_provider_card_bodies(text: str) -> list[tuple[str, str]]:
    """Return (title, stripped body) pairs from an all_providers MDX file."""
    return [
        (match.group("title"), match.group("body").strip())
        for match in CARD_BODY_RE.finditer(text)
    ]


def descriptions_over_limit(
    text: str,
    *,
    max_len: int = PROVIDER_CARD_DESCRIPTION_MAX_LEN,
) -> list[tuple[str, int, str]]:
    """Return (title, length, body) for card bodies longer than max_len."""
    over: list[tuple[str, int, str]] = []
    for title, body in iter_provider_card_bodies(text):
        length = len(body)
        if length > max_len:
            over.append((title, length, body))
    return over


def validate_provider_description(
    description: str,
    *,
    max_len: int = PROVIDER_CARD_DESCRIPTION_MAX_LEN,
) -> str | None:
    """Return an error message if description is empty or too long, else None."""
    cleaned = (description or "").strip()
    if not cleaned:
        return "Short provider description is required"
    length = len(cleaned)
    if length > max_len:
        return (
            f"Short provider description must be at most {max_len} characters "
            f"(got {length}). Use one short factual sentence."
        )
    return None
