"""Read and verify product source at a release tag.

Write tools call ``verify_evidence_in_source`` so citations cannot be invented.
The agent should also call ``get_product_source_file`` while investigating.
"""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import quote

import httpx
from langchain.tools import tool

from tools.credentials import github_token
from tools.evidence import parse_evidence_json


def _normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _encode_repo_path(path: str) -> str:
    return "/".join(quote(part, safe="") for part in path.lstrip("/").split("/") if part)


async def fetch_repo_file(
    repo: str,
    path: str,
    *,
    ref: str,
    token: str | None = None,
) -> str | None:
    """Return file text at ref, or None when the path does not exist."""
    clean_repo = repo.strip().strip("/")
    encoded_path = _encode_repo_path(path)
    headers = {
        "Accept": "application/vnd.github.raw+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "docs-release-watch",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.get(
            f"https://api.github.com/repos/{clean_repo}/contents/{encoded_path}",
            headers=headers,
            params={"ref": ref},
        )
        if token and response.status_code in {401, 403}:
            headers.pop("Authorization", None)
            response = await client.get(
                f"https://api.github.com/repos/{clean_repo}/contents/{encoded_path}",
                headers=headers,
                params={"ref": ref},
            )

    if response.status_code == 404:
        return None
    if response.status_code >= 400:
        raise RuntimeError(
            f"GitHub GET {clean_repo}@{ref}:{path} failed "
            f"({response.status_code}): {response.text}"
        )
    return _normalize_newlines(response.text)


def claim_appears_in_source(
    content: str,
    *,
    symbol: str | None = None,
    quote: str | None = None,
) -> bool:
    """Return True when the cited symbol or quote appears in the file text."""
    if symbol and symbol in content:
        return True
    if quote and quote in content:
        return True
    return False


async def verify_evidence_in_source(
    evidence: dict[str, Any],
    *,
    token: str | None = None,
) -> dict[str, Any]:
    """Fetch each evidence path at the tag and require the symbol/quote to appear.

    Raises ValueError when a path is missing or the citation is not found in the
    file. Returns a small verification summary for tool responses.
    """
    repo = evidence["source_repo"]
    tag = evidence["source_tag"]
    checked: list[dict[str, str]] = []

    for index, item in enumerate(evidence["items"]):
        path = item["path"]
        symbol = item.get("symbol")
        quote = item.get("quote")
        content = await fetch_repo_file(repo, path, ref=tag, token=token)
        if content is None:
            raise ValueError(
                f"evidence_json.items[{index}]: `{repo}@{tag}:{path}` was not "
                "found. Call get_product_source_file (or clone the product at "
                "the tag) and cite a real path from that checkout."
            )
        if not claim_appears_in_source(content, symbol=symbol, quote=quote):
            detail = symbol or quote or ""
            raise ValueError(
                f"evidence_json.items[{index}]: `{detail}` was not found in "
                f"`{repo}@{tag}:{path}`. Investigate the tagged source and cite "
                "a symbol or quote that actually appears in the file."
            )
        checked.append(
            {
                "path": path,
                "matched": symbol or (quote[:80] if quote else ""),
            }
        )

    return {
        "source_repo": repo,
        "source_tag": tag,
        "verified_items": checked,
    }


async def _optional_github_token() -> str | None:
    try:
        return await github_token()
    except RuntimeError:
        return None


@tool(parse_docstring=True)
async def get_product_source_file(repo: str, path: str, ref: str) -> str:
    """Read a file from a product GitHub repository at a tag or commit.

    Use this before drafting docs. Confirm APIs, flags, CLI commands, defaults,
    and behavior in the eligible release tag. Pass the same repo/tag/path into
    evidence_json when shipping.

    Args:
        repo: GitHub owner/repo (for example langchain-ai/deepagentsjs).
        path: Path within the repository
            (for example libs/deepagents/src/middleware/foo.ts).
        ref: Git tag, branch, or commit SHA (for example deepagents@1.14.2).
    """
    clean_repo = (repo or "").strip().strip("/")
    clean_path = (path or "").strip().lstrip("/")
    clean_ref = (ref or "").strip()
    if not clean_repo or "/" not in clean_repo:
        raise ValueError("repo must be an owner/repo string.")
    if not clean_path:
        raise ValueError("path must be a non-empty repository-relative path.")
    if not clean_ref:
        raise ValueError("ref must be a tag, branch, or commit SHA.")

    token = await _optional_github_token()
    content = await fetch_repo_file(
        clean_repo, clean_path, ref=clean_ref, token=token
    )
    if content is None:
        return json.dumps(
            {
                "repo": clean_repo,
                "path": clean_path,
                "ref": clean_ref,
                "exists": False,
                "content": "",
            }
        )
    return json.dumps(
        {
            "repo": clean_repo,
            "path": clean_path,
            "ref": clean_ref,
            "exists": True,
            "content": content,
        }
    )
