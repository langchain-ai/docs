"""Read-only GitHub access for the AI docs review agent.

The agent never holds a GitHub token. In CI it calls ``gh-read``, which runs this
script as a separate user that can read the token file. The script is the
security boundary, so it accepts one thing only: a GET of an allowlisted path
under a ``langchain-ai`` repository on api.github.com.

    gh-read repos/langchain-ai/langchain/git/trees/HEAD?recursive=1
    gh-read repos/langchain-ai/langchain/contents/libs/core/pyproject.toml --raw
"""

from __future__ import annotations

import os
import re
import sys
import urllib.error
import urllib.request

API = "https://api.github.com/"
# The override is for local testing. Under sudo the caller is the agent, so it
# cannot choose which file this user reads.
TOKEN_FILE = (
    "/etc/ai-review/gh_token"
    if os.environ.get("SUDO_USER")
    else os.environ.get("AI_REVIEW_GH_TOKEN_FILE", "/etc/ai-review/gh_token")
)
MAX_BYTES = 2 * 1024 * 1024

_REPO = r"repos/langchain-ai/[A-Za-z0-9._-]+"
_REF = r"[A-Za-z0-9._/=-]+"
ALLOWED = re.compile(
    rf"^{_REPO}(?:"
    rf"|/contents(?:/[A-Za-z0-9._/@+-]*)?"
    rf"|/git/trees/{_REF}"
    rf"|/git/blobs/[0-9a-f]{{40}}"
    rf"|/commits(?:/{_REF})?"
    rf"|/compare/{_REF}\.\.\.{_REF}"
    rf"|/tags|/releases(?:/latest|/tags/{_REF})?"
    rf"|/branches(?:/{_REF})?"
    rf"|/pulls/\d+(?:/files|/commits)?"
    rf")(?:\?[A-Za-z0-9_=&.,%:/-]*)?$"
)
USAGE = "usage: gh-read <repos/langchain-ai/REPO/...> [--raw]"


def validate(path: str) -> str | None:
    """Return the normalized API path, or None when it is not allowed."""
    path = path.removeprefix("/")
    bad = ("://", "//", "\\", " ", "\t", "\n", "\r")
    if not path or any(b in path for b in bad):
        return None
    # ".." is legal only as the three-dot separator of a compare range.
    if ".." in path.replace("...", "\0"):
        return None
    return path if ALLOWED.fullmatch(path) else None


def main(argv: list[str]) -> int:
    """Fetch one allowlisted path and print the body."""
    args = [a for a in argv if a != "--raw"]
    raw = len(args) != len(argv)
    if len(args) != 1:
        print(USAGE, file=sys.stderr)
        return 2
    path = validate(args[0])
    if path is None:
        print(f"gh-read: path not allowed: {args[0][:200]}", file=sys.stderr)
        return 2
    try:
        with open(TOKEN_FILE, encoding="utf-8") as fh:
            token = fh.read().strip()
    except OSError:
        token = ""
    headers = {
        "Accept": "application/vnd.github.raw" if raw else "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "langchain-docs-ai-review",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(API + path, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 - fixed https host
            body = resp.read(MAX_BYTES + 1)
    except urllib.error.HTTPError as err:
        print(f"gh-read: HTTP {err.code} for {path}", file=sys.stderr)
        return 1
    except urllib.error.URLError as err:
        print(f"gh-read: {err.reason}", file=sys.stderr)
        return 1
    truncated = len(body) > MAX_BYTES
    sys.stdout.write(body[:MAX_BYTES].decode("utf-8", errors="replace"))
    if truncated:
        print(f"\ngh-read: output truncated at {MAX_BYTES} bytes", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
