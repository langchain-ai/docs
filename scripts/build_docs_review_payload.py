"""Turn docs-review agent findings into a GitHub pull request review payload.

The `docs-review-bot-prs` workflow asks the docs-review agent to write its
findings as JSON. This script keeps the findings GitHub can anchor inline (lines
inside the PR diff) and renders each as a review comment, with a `suggestion`
block when the finding carries a replacement. Findings outside the diff move to
the review body, because a single out-of-diff line makes GitHub reject the whole
review.

Usage:
    python scripts/build_docs_review_payload.py FINDINGS_JSON BASE_REF OUT_JSON
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

MARKER = "<!-- docs-review-bot-prs -->"
HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def commentable_lines(base_ref: str) -> dict[str, set[int]]:
    """Map each changed file to the new-side line numbers inside its diff hunks."""
    diff = subprocess.run(
        ["git", "diff", "--unified=3", f"{base_ref}...HEAD", "--", "src/"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    lines: dict[str, set[int]] = {}
    path = None
    for row in diff.splitlines():
        if row.startswith("+++ "):
            path = row[6:] if row.startswith("+++ b/") else None
            if path:
                lines.setdefault(path, set())
        elif path and (match := HUNK_RE.match(row)):
            start = int(match.group(1))
            count = int(match.group(2)) if match.group(2) is not None else 1
            lines[path].update(range(start, start + count))
    return lines


def render_comment(finding: dict) -> str:
    """Render one finding as an inline comment body."""
    parts = [MARKER, f"**Rule:** {finding['rule']}", "", finding["explanation"]]
    replacement = finding.get("replacement")
    if replacement is not None:
        parts += ["", "```suggestion", replacement.rstrip("\n"), "```"]
    return "\n".join(parts)


def main() -> int:
    """Build the review payload and write it to OUT_JSON."""
    findings_path, base_ref, out_path = sys.argv[1:4]
    data = json.loads(Path(findings_path).read_text())
    allowed = commentable_lines(base_ref)

    comments = []
    leftovers = []
    for finding in data.get("findings", []):
        path = finding.get("path")
        end = finding.get("line")
        start = finding.get("start_line") or end
        if not path or not isinstance(end, int) or not isinstance(start, int):
            continue
        span = set(range(start, end + 1))
        if path in allowed and span <= allowed[path]:
            comment = {
                "path": path,
                "line": end,
                "side": "RIGHT",
                "body": render_comment(finding),
            }
            if start != end:
                comment.update(start_line=start, start_side="RIGHT")
            comments.append(comment)
        else:
            leftovers.append(
                f"- `{path}:{end}`: **{finding['rule']}**. {finding['explanation']}"
            )

    body = [MARKER, "### Automated docs review", "", data.get("summary", "").strip()]
    if leftovers:
        body += ["", "Findings outside the diff:", "", *leftovers]
    if not comments and not leftovers:
        body += ["", "No findings."]

    payload = {"event": "COMMENT", "body": "\n".join(body), "comments": comments}
    Path(out_path).write_text(json.dumps(payload))
    print(f"{len(comments)} inline comments, {len(leftovers)} in the review body")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
