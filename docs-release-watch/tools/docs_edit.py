"""Validate surgical docs edits and check whether docs already cover a symbol.

Catches whole-page rewrites and accidental edits to the wrong language fence.
Also rebases a stale old→new edit onto the live base when the page moved.
"""

from __future__ import annotations

import difflib
import json
import re
from typing import Any, Optional

import httpx
from langchain.tools import tool

from tools.credentials import github_token
from tools.products import get_product

DOCS_REPO = "langchain-ai/docs"

# Existing files may change at most this fraction of lines (insertions+deletions
# relative to the larger of old/new line counts). New files are exempt.
DEFAULT_MAX_LINE_CHURN = 0.35

_FENCE_RE = re.compile(
    r":::(python|js)\s*\n(.*?)(?:\n):::\s*(?:\n|$)",
    re.DOTALL,
)


def extract_language_fences(content: str) -> dict[str, list[str]]:
    """Return ordered fence bodies keyed by language (``python`` / ``js``)."""
    fences: dict[str, list[str]] = {"python": [], "js": []}
    for match in _FENCE_RE.finditer(content or ""):
        language = match.group(1)
        fences[language].append(match.group(2))
    return fences


def line_churn_ratio(old_content: str, new_content: str) -> float:
    """Return changed-line ratio using a multiset line-diff estimate."""
    old_lines = (old_content or "").splitlines()
    new_lines = (new_content or "").splitlines()
    if not old_lines and not new_lines:
        return 0.0
    old_set_counts: dict[str, int] = {}
    for line in old_lines:
        old_set_counts[line] = old_set_counts.get(line, 0) + 1
    new_set_counts: dict[str, int] = {}
    for line in new_lines:
        new_set_counts[line] = new_set_counts.get(line, 0) + 1

    shared = 0
    for line, count in old_set_counts.items():
        shared += min(count, new_set_counts.get(line, 0))
    changed = (len(old_lines) - shared) + (len(new_lines) - shared)
    baseline = max(len(old_lines), len(new_lines), 1)
    return changed / baseline


def _find_subsequence(haystack: list[str], needle: list[str]) -> Optional[int]:
    """Return the start index of needle in haystack, or None if missing/ambiguous."""
    if not needle:
        return None
    n = len(needle)
    hits = [
        index
        for index in range(0, len(haystack) - n + 1)
        if haystack[index : index + n] == needle
    ]
    if len(hits) != 1:
        return None
    return hits[0]


def rebase_edit_onto_base(
    old_content: str, new_content: str, base_content: str
) -> Optional[str]:
    """Replay the old→new line edit onto ``base_content``.

    Returns the rebased file text when every changed hunk still has a unique
    anchor on the live base. Returns ``None`` when the edit cannot be applied
    cleanly (page rewrote under the agent, ambiguous anchors, or pure inserts
    without surrounding context).
    """
    if old_content == base_content:
        return new_content
    if old_content == new_content:
        return None

    old_lines = (old_content or "").splitlines(keepends=True)
    new_lines = (new_content or "").splitlines(keepends=True)
    result = list((base_content or "").splitlines(keepends=True))
    matcher = difflib.SequenceMatcher(
        a=old_lines, b=new_lines, autojunk=False
    )

    # Apply from the bottom of the file so earlier anchors stay stable.
    for tag, i1, i2, j1, j2 in reversed(matcher.get_opcodes()):
        if tag == "equal":
            continue
        old_block = old_lines[i1:i2]
        new_block = new_lines[j1:j2]
        if tag == "insert":
            # Anchor the insert after the preceding equal line when present.
            if i1 <= 0:
                return None
            anchor = old_lines[i1 - 1 : i1]
            anchor_at = _find_subsequence(result, anchor)
            if anchor_at is None:
                return None
            insert_at = anchor_at + len(anchor)
            result[insert_at:insert_at] = new_block
            continue
        index = _find_subsequence(result, old_block)
        if index is None:
            return None
        result[index : index + len(old_block)] = new_block

    rebased = "".join(result)
    if rebased == base_content:
        return None
    return rebased


def validate_language_scope(
    path: str,
    old_content: str,
    new_content: str,
    language_scope: str,
) -> None:
    """Refuse edits that change the other language fence when scope is set."""
    scope = (language_scope or "").strip().lower()
    if scope in {"", "shared", "both", "all"}:
        return
    if scope not in {"python", "js"}:
        raise ValueError(
            f"language_scope must be 'python', 'js', 'shared', or empty; "
            f"got {language_scope!r}."
        )
    other = "js" if scope == "python" else "python"
    old_fences = extract_language_fences(old_content)
    new_fences = extract_language_fences(new_content)
    if old_fences[other] != new_fences[other]:
        raise ValueError(
            f"{path}: language_scope={scope!r} but :::{other} fence content "
            "changed. Edit only the in-scope language fence, or pass "
            "language_scope='shared' when the change is truly shared."
        )


def validate_docs_edits(
    files: list[dict[str, str]],
    *,
    language_scope: str = "",
    max_line_churn: float = DEFAULT_MAX_LINE_CHURN,
) -> list[dict[str, Any]]:
    """Validate each edit; raise ValueError on unsafe churn or fence violations."""
    summaries: list[dict[str, Any]] = []
    for file in files:
        path = file["path"]
        old_content = file["old_content"]
        new_content = file["new_content"]
        is_new = old_content == ""
        churn = 1.0 if is_new else line_churn_ratio(old_content, new_content)
        if not is_new and churn > max_line_churn:
            raise ValueError(
                f"{path}: edit changes ~{churn:.0%} of lines, which exceeds the "
                f"{max_line_churn:.0%} surgical-edit limit. Shrink the diff to the "
                "sections that must change for this feature; do not regenerate "
                "the page."
            )
        validate_language_scope(path, old_content, new_content, language_scope)
        summaries.append(
            {
                "path": path,
                "is_new": is_new,
                "line_churn": round(churn, 3),
                "language_scope": language_scope or "shared",
            }
        )
    return summaries


async def _fetch_docs_file(path: str, *, token: str | None) -> str | None:
    encoded_path = "/".join(part for part in path.lstrip("/").split("/") if part)
    headers = {
        "Accept": "application/vnd.github.raw+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "docs-release-watch",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.get(
            f"https://api.github.com/repos/{DOCS_REPO}/contents/{encoded_path}",
            headers=headers,
            params={"ref": "main"},
        )
        if token and response.status_code in {401, 403}:
            headers.pop("Authorization", None)
            response = await client.get(
                f"https://api.github.com/repos/{DOCS_REPO}/contents/{encoded_path}",
                headers=headers,
                params={"ref": "main"},
            )
    if response.status_code == 404:
        return None
    if response.status_code >= 400:
        raise RuntimeError(
            f"GitHub GET docs {path} failed ({response.status_code}): {response.text}"
        )
    return response.text.replace("\r\n", "\n").replace("\r", "\n")


@tool(parse_docstring=True)
async def check_docs_coverage(
    product: str,
    needles_json: str,
    docs_paths_json: str = "[]",
) -> str:
    """Check whether symbols already appear in current docs on main.

    Use during research before setting needs_docs. If every needle is already
    present in the relevant pages, the feature is likely already documented.

    Args:
        product: Product key from the registry.
        needles_json: JSON array of strings to search for (API names, flags,
            CLI commands, option keys).
        docs_paths_json: JSON array of docs-relative file paths to scan
            (for example ["src/oss/deepagents/customization.mdx"]). Required
            for a useful check; directory prefixes alone are not expanded.
    """
    config = get_product(product)
    try:
        needles = json.loads(needles_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"needles_json must be valid JSON: {exc}") from exc
    if not isinstance(needles, list) or not needles:
        raise ValueError("needles_json must be a non-empty JSON array of strings.")
    clean_needles = [str(item).strip() for item in needles if str(item).strip()]
    if not clean_needles:
        raise ValueError("needles_json must contain at least one non-empty string.")

    try:
        extra_paths = json.loads(docs_paths_json) if docs_paths_json.strip() else []
    except json.JSONDecodeError as exc:
        raise ValueError(f"docs_paths_json must be valid JSON: {exc}") from exc
    if not isinstance(extra_paths, list):
        raise ValueError("docs_paths_json must be a JSON array of paths.")

    paths: list[str] = []
    for path in [str(p) for p in extra_paths]:
        clean = path.lstrip("/")
        if not clean or clean.endswith("/"):
            continue
        if clean not in paths:
            paths.append(clean)
    exclude = list(config.get("docs_path_exclude_prefixes") or [])
    paths = [
        path
        for path in paths
        if not any(path.startswith(prefix) for prefix in exclude)
    ]
    if not paths:
        return json.dumps(
            {
                "product": product,
                "scanned_paths": [],
                "needles": clean_needles,
                "already_documented": [],
                "missing": clean_needles,
                "reason": (
                    "No concrete docs file paths to scan. Pass docs_paths_json "
                    "with page paths such as "
                    "src/oss/deepagents/customization.mdx."
                ),
            }
        )

    token = None
    try:
        token = await github_token()
    except RuntimeError:
        pass

    found: dict[str, list[str]] = {needle: [] for needle in clean_needles}
    scanned: list[str] = []
    for path in paths:
        content = await _fetch_docs_file(path, token=token)
        if content is None:
            continue
        scanned.append(path)
        for needle in clean_needles:
            if needle in content:
                found[needle].append(path)

    already = [needle for needle, hits in found.items() if hits]
    missing = [needle for needle, hits in found.items() if not hits]
    return json.dumps(
        {
            "product": product,
            "language_scope": config.get("language_scope", "shared"),
            "scanned_paths": scanned,
            "needles": clean_needles,
            "hits": found,
            "already_documented": already,
            "missing": missing,
        }
    )
