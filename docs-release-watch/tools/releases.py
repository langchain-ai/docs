"""GitHub release helpers for product documentation updates."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
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
        "source_path_prefixes": config.get("source_path_prefixes", []),
        "skill": config["skill"],
        "changelog_url": config["changelog_url"],
        "release_tag_prefix": config.get("release_tag_prefix", ""),
        "memory_file": config.get(
            "memory_file",
            f"/memories/agent/{product}-releases.md",
        ),
    }


def _path_in_prefixes(path: str, prefixes: list[str]) -> bool:
    if not prefixes:
        return True
    return any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in prefixes)


def summarize_compare_files(
    files: list[dict[str, Any]],
    *,
    source_path_prefixes: list[str],
    max_files: int = 80,
    max_patch_chars: int = 1200,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Filter and truncate a GitHub compare ``files`` list for the agent."""
    filtered: list[dict[str, Any]] = []
    skipped_outside_prefix = 0
    for file in files:
        filename = str(file.get("filename") or "")
        if not filename:
            continue
        if not _path_in_prefixes(filename, source_path_prefixes):
            skipped_outside_prefix += 1
            continue
        patch = str(file.get("patch") or "")
        if len(patch) > max_patch_chars:
            patch = patch[: max_patch_chars - 15] + "\n...[truncated]"
        filtered.append(
            {
                "filename": filename,
                "status": file.get("status"),
                "additions": file.get("additions"),
                "deletions": file.get("deletions"),
                "changes": file.get("changes"),
                "patch": patch,
            }
        )

    truncated = len(filtered) > max_files
    return filtered[:max_files], {
        "file_count_returned": min(len(filtered), max_files),
        "file_count_matched_prefix": len(filtered),
        "file_count_skipped_outside_prefix": skipped_outside_prefix,
        "files_truncated": truncated,
        "source_path_prefixes": source_path_prefixes,
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
async def get_eligible_release(
    product: str = "openwiki",
    min_age_days: int = 7,
    max_age_days: int = 30,
) -> str:
    """Find the newest product release in the age window.

    A release is eligible when it is at least ``min_age_days`` old and at most
    ``max_age_days`` old. That keeps first runs from backfilling ancient
    history: only versions from roughly the last month are in scope.

    Args:
        product: Product key from the registry (for example openwiki or deepagents).
        min_age_days: Minimum age in days before a release is eligible (default: 7).
        max_age_days: Maximum age in days; older releases are ignored (default: 30).
            Must be greater than min_age_days.
    """
    if max_age_days <= min_age_days:
        raise ValueError(
            f"max_age_days ({max_age_days}) must be greater than "
            f"min_age_days ({min_age_days})."
        )

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

    now = datetime.now(UTC)
    min_cutoff = now - timedelta(days=min_age_days)
    max_cutoff = now - timedelta(days=max_age_days)
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
        # Window: published on or before min_cutoff, and on or after max_cutoff.
        if max_cutoff <= when <= min_cutoff:
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
                    f"No non-prerelease release for {repo}{prefix_note} is between "
                    f"{min_age_days} and {max_age_days} days old."
                ),
                "min_age_days": min_age_days,
                "max_age_days": max_age_days,
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
            "candidates_in_window": [
                {
                    "tag": row["tag"],
                    "published_at": row["published_at"],
                }
                for row in eligible
            ],
            "min_age_days": min_age_days,
            "max_age_days": max_age_days,
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


async def _resolve_previous_tag(
    product: str,
    head_tag: str,
    *,
    token: str | None,
) -> str | None:
    """Return the next-older non-prerelease tag with the same product prefix."""
    config = get_product(product)
    repo = config["github_repo"]
    prefix = str(config.get("release_tag_prefix") or "")
    releases = await _github_get(f"/repos/{repo}/releases?per_page=100", token=token)
    if not isinstance(releases, list):
        return None
    matching: list[str] = []
    for release in releases:
        if release.get("draft") or release.get("prerelease"):
            continue
        tag = release.get("tag_name")
        if not _matches_prefix(tag, prefix):
            continue
        matching.append(str(tag))
    try:
        index = matching.index(head_tag)
    except ValueError:
        return None
    if index + 1 >= len(matching):
        return None
    return matching[index + 1]


@tool(parse_docstring=True)
async def get_release_diff(
    product: str,
    head_tag: str,
    base_tag: str = "",
) -> str:
    """Compare product source between two release tags.

    Prefer this over release-note prose when deciding what changed. Returns
    commits and changed files (with truncated patches) scoped to the product's
    source_path_prefixes when configured.

    Args:
        product: Product key from the registry (for example openwiki or deepagents).
        head_tag: Newer release tag (the eligible release).
        base_tag: Older release tag to diff against. When empty, uses the
            previous same-prefix release from the feed.
    """
    config = get_product(product)
    repo = config["github_repo"]
    prefix = str(config.get("release_tag_prefix") or "")
    if not _matches_prefix(head_tag, prefix):
        raise ValueError(
            f"head_tag {head_tag!r} does not match required prefix {prefix!r} "
            f"for product {product!r}."
        )

    token = None
    try:
        token = await github_token()
    except RuntimeError:
        pass

    resolved_base = (base_tag or "").strip()
    if resolved_base:
        if not _matches_prefix(resolved_base, prefix):
            raise ValueError(
                f"base_tag {resolved_base!r} does not match required prefix "
                f"{prefix!r} for product {product!r}."
            )
    else:
        resolved_base = await _resolve_previous_tag(
            product, head_tag, token=token
        ) or ""

    if not resolved_base:
        return json.dumps(
            {
                **_public_product_fields(product, config),
                "head_tag": head_tag,
                "base_tag": None,
                "compare_url": None,
                "commits": [],
                "files": [],
                "stats": {},
                "reason": (
                    "No previous same-prefix release found to diff against. "
                    "Inspect the head tag with get_product_source_file and "
                    "get_release_notes instead."
                ),
            }
        )

    encoded_base = quote(resolved_base, safe="")
    encoded_head = quote(head_tag, safe="")
    compare = await _github_get(
        f"/repos/{repo}/compare/{encoded_base}...{encoded_head}",
        token=token,
    )

    commits = [
        {
            "sha": (commit.get("sha") or "")[:12],
            "message": ((commit.get("commit") or {}).get("message") or "")
            .split("\n", 1)[0]
            .strip(),
            "html_url": commit.get("html_url"),
        }
        for commit in (compare.get("commits") or [])[:40]
    ]
    prefixes = list(config.get("source_path_prefixes") or [])
    files, file_stats = summarize_compare_files(
        list(compare.get("files") or []),
        source_path_prefixes=prefixes,
    )
    return json.dumps(
        {
            **_public_product_fields(product, config),
            "head_tag": head_tag,
            "base_tag": resolved_base,
            "compare_status": compare.get("status"),
            "ahead_by": compare.get("ahead_by"),
            "behind_by": compare.get("behind_by"),
            "total_commits": compare.get("total_commits"),
            "html_url": compare.get("html_url"),
            "commits": commits,
            "commits_truncated": len(compare.get("commits") or []) > 40,
            "files": files,
            "stats": file_stats,
        }
    )
