"""Open draft pull requests against the docs repository.

PRs must be grounded in the current docs file contents and in product-source
evidence. Callers pass ``old_content`` that must match ``main`` exactly, so the
agent cannot invent a whole page from memory without first reading it.
"""

from __future__ import annotations

import json
import re
from typing import Any

import httpx
from langchain.tools import tool

from tools.credentials import github_token
from tools.evidence import ensure_evidence_in_body, parse_evidence_json
from tools.source import verify_evidence_in_source

DOCS_REPO = "langchain-ai/docs"
DEFAULT_BASE = "main"


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug[:40] or "update"


async def _gh(
    method: str,
    path: str,
    *,
    token: str,
    json_body: dict[str, Any] | None = None,
    accept: str | None = None,
) -> Any:
    headers = {
        "Accept": accept or "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "docs-release-watch",
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.request(
            method,
            f"https://api.github.com{path}",
            headers=headers,
            json=json_body,
        )
        if response.status_code >= 400:
            raise RuntimeError(
                f"GitHub {method} {path} failed ({response.status_code}): {response.text}"
            )
        if response.status_code == 204 or not response.content:
            return None
        if accept and "raw" in accept:
            return response.text
        return response.json()


def _normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def parse_files_json(files_json: str) -> list[dict[str, str]]:
    """Parse files_json into {path, old_content, new_content} entries."""
    try:
        files = json.loads(files_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"files_json must be valid JSON: {exc}") from exc

    if not isinstance(files, list) or not files:
        raise ValueError(
            "files_json must be a non-empty JSON array of "
            "{path, old_content, new_content} objects."
        )

    normalized: list[dict[str, str]] = []
    for index, item in enumerate(files):
        if not isinstance(item, dict):
            raise ValueError(f"files_json[{index}] must be an object.")
        if "path" not in item or "new_content" not in item:
            raise ValueError(
                f"files_json[{index}] must include path and new_content."
            )
        if "old_content" not in item:
            raise ValueError(
                f"files_json[{index}] must include old_content. "
                "Call get_docs_file first and pass its content unchanged as "
                "old_content (use an empty string only for a new file)."
            )
        path = str(item["path"]).lstrip("/")
        if not path:
            raise ValueError(f"files_json[{index}].path must be non-empty.")
        if path.startswith("docs-release-watch/"):
            raise ValueError("Do not modify the agent project from a docs PR.")
        old_content = _normalize_newlines(str(item["old_content"]))
        new_content = _normalize_newlines(str(item["new_content"]))
        if old_content == new_content:
            raise ValueError(
                f"files_json[{index}] ({path}): new_content is identical to "
                "old_content; omit unchanged files."
            )
        normalized.append(
            {
                "path": path,
                "old_content": old_content,
                "new_content": new_content,
            }
        )
    return normalized


async def fetch_docs_file_content(
    path: str,
    *,
    token: str,
    ref: str = DEFAULT_BASE,
) -> str | None:
    """Return the file text at ref, or None when the path does not exist."""
    clean = path.lstrip("/")
    encoded_path = "/".join(part for part in clean.split("/") if part)
    headers = {
        "Accept": "application/vnd.github.raw+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "docs-release-watch",
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.get(
            f"https://api.github.com/repos/{DOCS_REPO}/contents/{encoded_path}",
            headers=headers,
            params={"ref": ref},
        )
    if response.status_code == 404:
        return None
    if response.status_code >= 400:
        raise RuntimeError(
            f"GitHub GET contents/{encoded_path} failed "
            f"({response.status_code}): {response.text}"
        )
    return _normalize_newlines(response.text)


def verify_old_content_matches_base(
    path: str,
    old_content: str,
    base_content: str | None,
) -> None:
    """Refuse edits whose claimed base does not match the live docs file."""
    if base_content is None:
        if old_content != "":
            raise ValueError(
                f"{path}: file does not exist on the base branch, so "
                "old_content must be an empty string for a new file."
            )
        return
    if old_content == "":
        raise ValueError(
            f"{path}: file already exists on the base branch. Pass the exact "
            "current contents from get_docs_file as old_content."
        )
    if old_content != base_content:
        raise ValueError(
            f"{path}: old_content does not match the base branch. Call "
            "get_docs_file again and start from that content; do not invent "
            "or regenerate the whole page from memory."
        )


@tool(parse_docstring=True)
async def get_docs_file(path: str, ref: str = DEFAULT_BASE) -> str:
    """Read a file from langchain-ai/docs at the given ref.

    Always call this before editing a page. Pass the returned content unchanged
    as old_content when calling create_draft_docs_pr.

    Args:
        path: Path relative to the docs repo root
            (for example src/oss/deepagents/customization.mdx).
        ref: Git ref to read (default: main).
    """
    token = await github_token()
    clean = path.lstrip("/")
    if not clean:
        raise ValueError("path must be a non-empty docs-relative path.")
    content = await fetch_docs_file_content(clean, token=token, ref=ref)
    if content is None:
        return json.dumps(
            {
                "path": clean,
                "ref": ref,
                "exists": False,
                "content": "",
            }
        )
    return json.dumps(
        {
            "path": clean,
            "ref": ref,
            "exists": True,
            "content": content,
        }
    )


@tool(parse_docstring=True)
async def create_draft_docs_pr(
    title: str,
    body: str,
    branch_name: str,
    files_json: str,
    evidence_json: str,
    base_branch: str = DEFAULT_BASE,
    commit_message: str = "",
) -> str:
    """Create a draft PR on langchain-ai/docs with surgical file edits.

    Each file must include old_content that exactly matches the base branch
    (from get_docs_file) and the edited new_content. evidence_json must cite
    product source at the release tag.

    Args:
        title: Pull request title for one feature only.
        body: Pull request body. Include Closes [DOC-N](linear-url) under a
            Linear heading so CI can sync status. A Source evidence section
            is appended from evidence_json when missing.
        branch_name: New branch name to create from the base branch.
        files_json: JSON array of {path, old_content, new_content}.
            old_content must match the base branch exactly (empty string for
            a new file). Paths are relative to the docs repo root.
        evidence_json: JSON object with source_repo, source_tag, and items
            [{path, symbol}] or [{path, quote}] verified in product source.
        base_branch: Base branch to branch from (default: main).
        commit_message: Optional commit message. Defaults to the PR title.
    """
    token = await github_token()
    evidence = parse_evidence_json(evidence_json)
    verification = await verify_evidence_in_source(evidence, token=token)
    files = parse_files_json(files_json)

    for file in files:
        base_content = await fetch_docs_file_content(
            file["path"], token=token, ref=base_branch
        )
        verify_old_content_matches_base(
            file["path"], file["old_content"], base_content
        )

    pr_body = ensure_evidence_in_body(body, evidence)

    branch = branch_name.strip().replace(" ", "-")
    if not branch.startswith("docs/"):
        branch = f"docs/{_slugify(branch)}"

    ref = await _gh(
        "GET", f"/repos/{DOCS_REPO}/git/ref/heads/{base_branch}", token=token
    )
    base_sha = ref["object"]["sha"]
    base_commit = await _gh(
        "GET", f"/repos/{DOCS_REPO}/git/commits/{base_sha}", token=token
    )
    base_tree_sha = base_commit["tree"]["sha"]

    tree_items: list[dict[str, str]] = []
    for file in files:
        blob = await _gh(
            "POST",
            f"/repos/{DOCS_REPO}/git/blobs",
            token=token,
            json_body={"content": file["new_content"], "encoding": "utf-8"},
        )
        tree_items.append(
            {
                "path": file["path"],
                "mode": "100644",
                "type": "blob",
                "sha": blob["sha"],
            }
        )

    tree = await _gh(
        "POST",
        f"/repos/{DOCS_REPO}/git/trees",
        token=token,
        json_body={"base_tree": base_tree_sha, "tree": tree_items},
    )
    message = commit_message.strip() or title.strip()
    commit = await _gh(
        "POST",
        f"/repos/{DOCS_REPO}/git/commits",
        token=token,
        json_body={
            "message": message,
            "tree": tree["sha"],
            "parents": [base_sha],
        },
    )

    await _gh(
        "POST",
        f"/repos/{DOCS_REPO}/git/refs",
        token=token,
        json_body={"ref": f"refs/heads/{branch}", "sha": commit["sha"]},
    )

    pr = await _gh(
        "POST",
        f"/repos/{DOCS_REPO}/pulls",
        token=token,
        json_body={
            "title": title.strip(),
            "body": pr_body,
            "head": branch,
            "base": base_branch,
            "draft": True,
        },
    )

    return json.dumps(
        {
            "number": pr["number"],
            "url": pr["html_url"],
            "branch": branch,
            "base": base_branch,
            "draft": True,
            "files": [file["path"] for file in files],
            "commit_sha": commit["sha"],
            "evidence": evidence,
            "evidence_verified": verification,
        }
    )
