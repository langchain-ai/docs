"""Shared source-evidence validation for Linear issues and docs PRs.

Release notes are leads, not ground truth. Write tools refuse to ship without
at least one product-source citation at the release tag.
"""

from __future__ import annotations

import json
from typing import Any


def parse_evidence_json(evidence_json: str) -> dict[str, Any]:
    """Parse and validate evidence_json for a single feature.

    Expected shape::

        {
          "source_repo": "langchain-ai/deepagentsjs",
          "source_tag": "deepagents@1.14.2",
          "items": [
            {
              "path": "libs/deepagents/src/middleware/foo.ts",
              "symbol": "offloadBinaryContent"
            }
          ]
        }

    Each item must include ``path`` and at least one of ``symbol`` or ``quote``.
    """
    raw = (evidence_json or "").strip()
    if not raw:
        raise ValueError(
            "evidence_json is required. Cite the product repo at the release tag "
            "(source_repo, source_tag, and items with path + symbol or quote)."
        )
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"evidence_json must be valid JSON: {exc}") from exc

    if not isinstance(payload, dict):
        raise ValueError("evidence_json must be a JSON object.")

    source_repo = str(payload.get("source_repo") or "").strip()
    source_tag = str(payload.get("source_tag") or "").strip()
    items = payload.get("items")

    if not source_repo or "/" not in source_repo:
        raise ValueError(
            "evidence_json.source_repo must be an owner/repo string "
            "(for example langchain-ai/deepagents)."
        )
    if not source_tag:
        raise ValueError(
            "evidence_json.source_tag must be the release tag you verified against."
        )
    if not isinstance(items, list) or not items:
        raise ValueError(
            "evidence_json.items must be a non-empty array of "
            "{path, symbol} or {path, quote} objects."
        )

    normalized_items: list[dict[str, str]] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"evidence_json.items[{index}] must be an object.")
        path = str(item.get("path") or "").strip().lstrip("/")
        symbol = str(item.get("symbol") or "").strip()
        quote = str(item.get("quote") or "").strip()
        if not path:
            raise ValueError(f"evidence_json.items[{index}].path is required.")
        if not symbol and not quote:
            raise ValueError(
                f"evidence_json.items[{index}] must include symbol or quote."
            )
        entry: dict[str, str] = {"path": path}
        if symbol:
            entry["symbol"] = symbol
        if quote:
            entry["quote"] = quote
        normalized_items.append(entry)

    return {
        "source_repo": source_repo,
        "source_tag": source_tag,
        "items": normalized_items,
    }


def format_evidence_markdown(evidence: dict[str, Any]) -> str:
    """Render evidence as a markdown section for Linear / PR bodies."""
    lines = [
        "## Source evidence",
        f"- Repo: `{evidence['source_repo']}`",
        f"- Tag: `{evidence['source_tag']}`",
    ]
    for item in evidence["items"]:
        detail = item.get("symbol") or item.get("quote") or ""
        # Keep quotes short in the rendered section.
        if item.get("quote") and not item.get("symbol"):
            detail = detail.replace("\n", " ").strip()
            if len(detail) > 120:
                detail = detail[:117] + "..."
            detail = f'"{detail}"'
        lines.append(f"- `{item['path']}`: {detail}")
    return "\n".join(lines)


def ensure_evidence_in_body(body: str, evidence: dict[str, Any]) -> str:
    """Append a Source evidence section when the body does not already have one."""
    text = (body or "").strip()
    if "## Source evidence" in text:
        return text
    return f"{text}\n\n{format_evidence_markdown(evidence)}".strip()
