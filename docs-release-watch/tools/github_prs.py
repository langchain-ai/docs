"""Open draft pull requests against the docs repository."""

from __future__ import annotations

import json
import re
from typing import Any

import httpx
from langchain.tools import tool

from tools.credentials import github_token

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
) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
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
        return response.json()


@tool(parse_docstring=True)
async def create_draft_docs_pr(
    title: str,
    body: str,
    branch_name: str,
    files_json: str,
    base_branch: str = DEFAULT_BASE,
    commit_message: str = "",
) -> str:
    """Create a draft PR on langchain-ai/docs with the provided file contents.

    Args:
        title: Pull request title for one feature only.
        body: Pull request body. Include the Linear issue URL.
        branch_name: New branch name to create from the base branch.
        files_json: JSON array of objects with path and content keys.
            Paths are relative to the docs repo root
            (for example src/oss/openwiki/integrations.mdx).
        base_branch: Base branch to branch from (default: main).
        commit_message: Optional commit message. Defaults to the PR title.
    """
    token = await github_token()
    try:
        files = json.loads(files_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"files_json must be valid JSON: {exc}") from exc

    if not isinstance(files, list) or not files:
        raise ValueError("files_json must be a non-empty JSON array of {path, content}.")

    normalized: list[dict[str, str]] = []
    for item in files:
        if not isinstance(item, dict) or "path" not in item or "content" not in item:
            raise ValueError("Each file must be an object with path and content strings.")
        path = str(item["path"]).lstrip("/")
        if path.startswith("docs-release-watch/"):
            raise ValueError("Do not modify the agent project from a docs PR.")
        normalized.append({"path": path, "content": str(item["content"])})

    branch = branch_name.strip().replace(" ", "-")
    if not branch.startswith("docs/"):
        branch = f"docs/{_slugify(branch)}"

    ref = await _gh("GET", f"/repos/{DOCS_REPO}/git/ref/heads/{base_branch}", token=token)
    base_sha = ref["object"]["sha"]
    base_commit = await _gh("GET", f"/repos/{DOCS_REPO}/git/commits/{base_sha}", token=token)
    base_tree_sha = base_commit["tree"]["sha"]

    tree_items: list[dict[str, str]] = []
    for file in normalized:
        blob = await _gh(
            "POST",
            f"/repos/{DOCS_REPO}/git/blobs",
            token=token,
            json_body={"content": file["content"], "encoding": "utf-8"},
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
            "body": body.strip(),
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
            "files": [file["path"] for file in normalized],
            "commit_sha": commit["sha"],
        }
    )
