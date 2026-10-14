"""GitHub release helpers for product documentation updates."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import quote

import httpx
from langchain.tools import tool

from tools.credentials import github_token
from tools.products import get_product, list_products


def _parse_published_at(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _matches_prefix(tag: str | None, prefix: str) -> bool:
    if not prefix:
        return True
    return bool(tag) and str(tag).startswith(prefix)


async def _github_get(path: str, *, token: str | None = None) -> Any:
    """GET a GitHub API path.

    Public release endpoints work anonymously. If a token is present but GitHub
    rejects it (common when SAML SSO is not authorized for langchain-ai), retry
    once without auth so local Studio keeps working for read-only checks.
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "docs-release-watch",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(f"https://api.github.com{path}", headers=headers)
        if token and response.status_code in {401, 403}:
            headers.pop("Authorization", None)
            response = await client.get(
                f"https://api.github.com{path}",
                headers=headers,
            )
        response.raise_for_status()
        return response.json()


def _public_product_fields(product: str, config: dict[str, Any]) -> dict[str, Any]:
    return {
        "product": product,
        "display_name": config["display_name"],
        "github_repo": config["github_repo"],
        "docs_repo": config["docs_repo"],
        "docs_paths": config["docs_paths"],
        "docs_path_exclude_prefixes": config.get("docs_path_exclude_prefixes", []),
        "skill": config["skill"],
        "changelog_url": config["changelog_url"],
        "release_tag_prefix": config.get("release_tag_prefix", ""),
        "memory_file": config.get(
            "memory_file",
            f"/memories/agent/{product}-releases.md",
        ),
    }


@tool(parse_docstring=True)
async def list_watched_products() -> str:
    """List product keys the docs release watch agent knows how to check."""
    rows = []
    for key in list_products():
        config = get_product(key)
        rows.append(
            {
                "product": key,
                "display_name": config["display_name"],
                "skill": config["skill"],
                "release_tag_prefix": config.get("release_tag_prefix", ""),
                "docs_paths": config["docs_paths"],
            }
        )
    return json.dumps({"products": rows})


@tool(parse_docstring=True)
async def get_eligible_release(product: str = "openwiki", min_age_days: int = 7) -> str:
    """Find the newest product release published at least min_age_days ago.

    Args:
        product: Product key from the registry (for example openwiki or deepagents).
        min_age_days: Minimum age in days before a release is eligible (default: 7).
    """
    config = get_product(product)
    repo = config["github_repo"]
    prefix = str(config.get("release_tag_prefix") or "")
    token = None
    try:
        token = await github_token()
    except RuntimeError:
        # Public release lists are readable without auth; continue anonymously.
        pass

    # Monorepo feeds interleave many packages; fetch a wider page then filter.
    releases = await _github_get(f"/repos/{repo}/releases?per_page=100", token=token)
    if not isinstance(releases, list) or not releases:
        return json.dumps(
            {
                **_public_product_fields(product, config),
                "eligible": None,
                "reason": "No releases found.",
            }
        )

    cutoff = datetime.now(timezone.utc) - timedelta(days=min_age_days)
    eligible: list[dict[str, Any]] = []
    for release in releases:
        if release.get("draft") or release.get("prerelease"):
            continue
        tag = release.get("tag_name")
        if not _matches_prefix(tag, prefix):
            continue
        published_at = release.get("published_at")
        if not published_at:
            continue
        when = _parse_published_at(published_at)
        if when <= cutoff:
            eligible.append(
                {
                    "tag": tag,
                    "name": release.get("name") or tag,
                    "published_at": published_at,
                    "html_url": release.get("html_url"),
                    "body": release.get("body") or "",
                }
            )

    if not eligible:
        prefix_note = f" matching prefix {prefix!r}" if prefix else ""
        return json.dumps(
            {
                **_public_product_fields(product, config),
                "eligible": None,
                "reason": (
                    f"No non-prerelease release for {repo}{prefix_note} is at least "
                    f"{min_age_days} days old yet."
                ),
                "min_age_days": min_age_days,
            }
        )

    # Releases endpoint is newest-first; keep that order among eligible ones.
    newest = eligible[0]
    previous = eligible[1] if len(eligible) > 1 else None
    return json.dumps(
        {
            **_public_product_fields(product, config),
            "eligible": newest,
            "previous": previous,
            "min_age_days": min_age_days,
        }
    )


@tool(parse_docstring=True)
async def get_release_notes(product: str, tag: str) -> str:
    """Fetch full release notes for a product tag.

    Args:
        product: Product key from the registry (for example openwiki or deepagents).
        tag: Git tag or release name (for example v0.7.0 or deepagents==0.7.24).
    """
    config = get_product(product)
    repo = config["github_repo"]
    prefix = str(config.get("release_tag_prefix") or "")
    if not _matches_prefix(tag, prefix):
        raise ValueError(
            f"Tag {tag!r} does not match required prefix {prefix!r} for product {product!r}."
        )

    token = None
    try:
        token = await github_token()
    except RuntimeError:
        pass

    encoded_tag = quote(tag, safe="")
    release = await _github_get(
        f"/repos/{repo}/releases/tags/{encoded_tag}",
        token=token,
    )
    return json.dumps(
        {
            **_public_product_fields(product, config),
            "tag": release.get("tag_name"),
            "name": release.get("name"),
            "published_at": release.get("published_at"),
            "html_url": release.get("html_url"),
            "body": release.get("body") or "",
        }
    )
