"""Merge, screen, and post AI docs review findings on a pull request.

The review passes (`docs-review`, `verify-against-source`, `docs-team-voice`) each
write a findings file in the format `.agents/skills/docs-review/ci-mode.md`
defines. This script is the only part of the workflow that writes to GitHub, and
it runs no model.

Subcommands:

- ``sanitize``: strip private evidence and drop findings whose public text
  matches a private-source pattern. Runs in the review job, before upload,
  because this repository's artifacts and logs are public.
- ``post``: validate, dedupe, render one summary comment and inline review
  comments, and set the review label. ``--dry-run`` prints the rendering
  instead of calling the API.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

MARKER = "<!-- ai-docs-review -->"
FINDING_MARKER = "<!-- ai-docs-review-finding:{fp} -->"
API = "https://api.github.com"

SEVERITIES = ("must_fix", "major", "minor")
FIX_CLASSES = ("auto", "suggest", "human")
SKILLS = ("docs-review", "verify-against-source", "docs-team-voice")
SEVERITY_RANK = {s: i for i, s in enumerate(SEVERITIES)}

LABEL_LOW_RISK = "ai-review: low-risk"
LABEL_NEEDS_HUMAN = "ai-review: needs-human"
LABELS = {
    LABEL_LOW_RISK: ("0e8a16", "AI review found nothing that needs a human decision"),
    LABEL_NEEDS_HUMAN: ("d93f0b", "AI review found something a person has to decide"),
}

# Text in a public field that names private source. A match is dropped unless
# the same token already appears in the PR's own diff.
PRIVATE_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in (
        r"langchainplus",
        r"langgraph-api",
        r"smith-(?:backend|go|frontend)",
        r"host-backend",
        r"lc_config",
        r"managed-deepagents-sdk",
        r"\bFF_[A-Z0-9_]{3,}\b",
        r"\beppo\b",
    )
]

# Paths in the diff that make a PR higher risk regardless of findings.
HIGH_RISK_PATHS = (
    re.compile(r"^src/docs\.json$"),
    re.compile(r"^src/snippets/"),
    re.compile(r"^src/code-samples/"),
)
LOW_RISK_MAX_CHANGED_LINES = 50

MAX_TEXT = 4000
MAX_INLINE = 25
STOPWORDS = frozenset(
    ["a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "in", "is", "it", "its", "of", "on", "or", "that", "the", "this", "to", "with", "not", "no", "does", "page", "diff", "line"]
)


@dataclass
class Finding:
    """One validated finding, with public fields only."""

    skill: str
    file: str
    line: int | None
    end_line: int | None
    severity: str
    fix_class: str
    rule: str
    summary: str
    replacement: str | None
    evidence_kind: str
    evidence_public: str
    skills: list[str] = field(default_factory=list)

    @property
    def fingerprint(self) -> str:
        """Stable id across pushes, so a rerun does not repost a finding."""
        words = " ".join(sorted(_words(self.summary)))
        raw = f"{self.file}|{self.rule}|{words}"
        return hashlib.sha256(raw.encode()).hexdigest()[:12]


@dataclass
class Diff:
    """Changed files and, per file, the line numbers the diff added or changed."""

    files: dict[str, str]  # path -> status letter (A, M, D, R)
    lines: dict[str, set[int]]
    added_text: str

    @property
    def changed_line_count(self) -> int:
        return sum(len(v) for v in self.lines.values())


# ---------------------------------------------------------------------------
# Parsing and validation


def _words(text: str) -> set[str]:
    return {
        w
        for w in re.findall(r"[a-z0-9_]+", text.lower())
        if w not in STOPWORDS and len(w) > 2
    }


def _clean(text: object, limit: int = MAX_TEXT) -> str:
    """Coerce model text into something safe to post."""
    s = "" if text is None else str(text)
    s = re.sub(r"<!--.*?-->", "", s, flags=re.DOTALL)  # no hidden markers
    s = re.sub(
        r"<(/?)(script|iframe|img|details|summary)\b",
        r"&lt;\1\2",
        s,
        flags=re.IGNORECASE,
    )
    s = re.sub(r"(?<![\w`])@(?=[A-Za-z0-9-])", "@\u200b", s)  # no pings
    return s.strip()[:limit]


def _as_line(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value if value > 0 else None


def parse_findings(data: object, skill_hint: str = "") -> tuple[list[Finding], int]:
    """Return valid findings from one findings file, and how many were rejected."""
    if not isinstance(data, dict) or not isinstance(data.get("findings"), list):
        return [], 1
    skill = data.get("skill") if data.get("skill") in SKILLS else skill_hint
    out, rejected = [], 0
    for raw in data["findings"]:
        if not isinstance(raw, dict):
            rejected += 1
            continue
        path = str(raw.get("file") or "")
        if (
            raw.get("severity") not in SEVERITIES
            or raw.get("fix_class") not in FIX_CLASSES
            or not path
            or ".." in Path(path).parts
            or path.startswith("/")
            or not str(raw.get("summary") or "").strip()
        ):
            rejected += 1
            continue
        line = _as_line(raw.get("line"))
        end = _as_line(raw.get("end_line")) or line
        if line and end and end < line:
            end = line
        ev = raw.get("evidence") if isinstance(raw.get("evidence"), dict) else {}
        replacement = raw.get("replacement")
        out.append(
            Finding(
                skill=skill or "docs-review",
                file=path,
                line=line,
                end_line=end,
                severity=raw["severity"],
                fix_class=raw["fix_class"],
                rule=_clean(raw.get("rule"), 200),
                summary=_clean(raw.get("summary"), 1500),
                replacement=None
                if replacement is None
                else str(replacement)[:MAX_TEXT],
                evidence_kind=_clean(ev.get("kind"), 20) or "none",
                evidence_public=_clean(ev.get("public"), 600),
                skills=[skill or "docs-review"],
            )
        )
    return out, rejected


def screen_private(
    findings: list[Finding], diff_text: str
) -> tuple[list[Finding], int]:
    """Drop findings whose public text names private source the diff does not."""
    kept, dropped = [], 0
    for f in findings:
        public = " ".join([f.summary, f.evidence_public, f.rule, f.replacement or ""])
        leaked = False
        for pat in PRIVATE_PATTERNS:
            for m in pat.finditer(public):
                if m.group(0).lower() not in diff_text.lower():
                    leaked = True
                    break
            if leaked:
                break
        if leaked:
            dropped += 1
        else:
            kept.append(f)
    return kept, dropped


def dedupe(findings: list[Finding]) -> list[Finding]:
    """Merge findings two passes raised about the same problem."""
    merged: list[Finding] = []
    for f in sorted(findings, key=lambda x: SEVERITY_RANK[x.severity]):
        twin = next((m for m in merged if _same_problem(m, f)), None)
        if twin is None:
            merged.append(f)
            continue
        for s in f.skills:
            if s not in twin.skills:
                twin.skills.append(s)
        # A replacement is only valid for the exact range it was written for.
        same_range = (twin.line, twin.end_line) == (f.line, f.end_line)
        if (
            same_range
            and twin.replacement is None
            and f.replacement is not None
            and twin.fix_class != "human"
        ):
            twin.replacement, twin.fix_class = f.replacement, f.fix_class
    return merged


def _overlap(a: Finding, b: Finding) -> float:
    wa, wb = _words(a.summary), _words(b.summary)
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / min(len(wa), len(wb))


def _same_problem(a: Finding, b: Finding) -> bool:
    if a.line is None and b.line is None:
        # File-level findings, such as a missing nav entry, can name either file.
        return _overlap(a, b) >= (0.4 if a.file == b.file else 0.5)
    if a.file != b.file or a.line is None or b.line is None:
        return False
    if (a.end_line or a.line) < b.line or (b.end_line or b.line) < a.line:
        return False
    # A fix and a question over different ranges are two actions; keep both.
    if (a.line, a.end_line) != (b.line, b.end_line) and (a.replacement is None) != (
        b.replacement is None
    ):
        return False
    return _overlap(a, b) >= 0.4


# ---------------------------------------------------------------------------
# Diff


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, check=True, timeout=120
    ).stdout


def read_diff(base: str, head: str) -> Diff:
    """Read changed files and changed line numbers between two commits."""
    for sha in (base, head):
        if not re.fullmatch(r"[0-9a-f]{7,40}", sha):
            raise ValueError(f"not a commit SHA: {sha!r}")
    files: dict[str, str] = {}
    for row in _git("diff", "--name-status", "-M", base, head).splitlines():
        parts = row.split("\t")
        if len(parts) >= 2:
            files[parts[-1]] = parts[0][0]
    lines: dict[str, set[int]] = {}
    added: list[str] = []
    current = None
    for row in _git("diff", "-U0", "-M", base, head).splitlines():
        if row.startswith("+++ "):
            current = row[6:] if row.startswith("+++ b/") else None
            continue
        m = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", row)
        if m and current:
            start, count = int(m.group(1)), int(m.group(2) or "1")
            lines.setdefault(current, set()).update(range(start, start + count))
        elif row.startswith("+") and not row.startswith("+++"):
            added.append(row[1:])
    return Diff(files=files, lines=lines, added_text="\n".join(added))


def choose_label(findings: list[Finding], diff: Diff, task_checks: list[dict]) -> str:
    """Pick the review label by a fixed rule, never by the model."""
    if any(
        f.severity in ("must_fix", "major") or f.fix_class == "human" for f in findings
    ):
        return LABEL_NEEDS_HUMAN
    for tc in task_checks:
        if (
            tc.get("documents_claimed_change") == "no"
            or tc.get("contradicts_product") == "yes"
        ):
            return LABEL_NEEDS_HUMAN
    if any(status != "M" for status in diff.files.values()):
        return LABEL_NEEDS_HUMAN
    if any(p.search(path) for path in diff.files for p in HIGH_RISK_PATHS):
        return LABEL_NEEDS_HUMAN
    if diff.changed_line_count > LOW_RISK_MAX_CHANGED_LINES:
        return LABEL_NEEDS_HUMAN
    return LABEL_LOW_RISK


# ---------------------------------------------------------------------------
# Rendering


def _inline_ok(f: Finding, diff: Diff) -> bool:
    """Inline a finding that blocks, or that carries a one-click fix.

    Inline comments are the only place a reviewer can react to one finding, so
    everything worth grading goes inline. A minor note with no fix stays in the
    summary.
    """
    has_fix = f.replacement is not None and f.fix_class != "human"
    if f.line is None or not (f.severity in ("must_fix", "major") or has_fix):
        return False
    changed = diff.lines.get(f.file, set())
    return all(n in changed for n in range(f.line, (f.end_line or f.line) + 1))


def _suggestion(f: Finding) -> str:
    if f.replacement is None or f.fix_class == "human":
        return ""
    fence = "````" if "```" in f.replacement else "```"
    return f"\n\n{fence}suggestion\n{f.replacement}\n{fence}"


def _label(f: Finding) -> str:
    return {"must_fix": "Must fix", "major": "Major", "minor": "Minor"}[f.severity]


def render_inline(f: Finding) -> str:
    """Body of one inline review comment."""
    rule = f" · {f.rule}" if f.rule else ""
    evidence = (
        f"\n\n<sub>Evidence: {f.evidence_public}</sub>" if f.evidence_public else ""
    )
    return (
        f"**{_label(f)}**{rule}\n\n{f.summary}{_suggestion(f)}{evidence}\n\n"
        f"<sub>AI docs review ({', '.join(f.skills)}). React 👍 if this helped, 👎 if not.</sub>\n"
        f"{FINDING_MARKER.format(fp=f.fingerprint)}"
    )


def _loc(f: Finding) -> str:
    return f"`{f.file}:{f.line}`" if f.line else f"`{f.file}`"


def render_summary(
    findings: list[Finding],
    inline: list[Finding],
    label: str,
    head: str,
    not_checked: list[str],
    stats: dict[str, int],
) -> str:
    """The single summary comment, replaced on every run."""
    inline_fps = {f.fingerprint for f in inline}
    blocking = [f for f in findings if f.severity in ("must_fix", "major")]
    rules = [
        f for f in findings if f.severity == "minor" and f.skill != "docs-team-voice"
    ]
    voice = [
        f for f in findings if f.severity == "minor" and f.skill == "docs-team-voice"
    ]
    out = [
        MARKER,
        "## AI docs review",
        "",
        f"Reviewed `{head[:12]}`: {len(blocking)} must fix or major, {len(rules)} minor, "
        f"{len(voice)} voice suggestions. Label: `{label}`.",
        "",
        "This is a first pass for style and technical accuracy. A docs team reviewer "
        "still reviews the PR. React 👍 or 👎 on any finding so the review can improve.",
    ]

    def section(title: str, rows: list[Finding], collapsed: bool) -> None:
        if not rows:
            return
        out.append("")
        body = []
        for f in rows:
            where = "inline" if f.fingerprint in inline_fps else _loc(f)
            text = f.summary.replace("\n", " ")
            body.append(f"- **{_label(f)}** ({where}): {text}")
        if collapsed:
            out.append(f"<details><summary>{title} ({len(rows)})</summary>\n")
            out.extend(body)
            out.append("\n</details>")
        else:
            out.append(f"### {title}\n")
            out.extend(body)

    section("Must fix and major", blocking, collapsed=False)
    section("Minor", rules, collapsed=True)
    section("Voice suggestions", voice, collapsed=True)
    if not_checked:
        out.append("")
        out.append(f"<details><summary>Not checked ({len(not_checked)})</summary>\n")
        out.extend(f"- {_clean(n, 400)}" for n in not_checked[:20])
        out.append("\n</details>")
    if stats.get("rejected") or stats.get("private") or stats.get("failed"):
        out.append("")
        out.append(
            f"<sub>Dropped {stats.get('rejected', 0)} malformed and "
            f"{stats.get('private', 0)} private-source findings. "
            f"{stats.get('failed', 0)} of 3 passes did not finish.</sub>"
        )
    out.append("")
    out.append(
        "<sub>Add the `skip-ai-review` label to turn this off for this PR.</sub>"
    )
    return "\n".join(out)


# ---------------------------------------------------------------------------
# GitHub API


class GitHub:
    """Minimal REST client: the token comes from the environment only."""

    def __init__(self, repo: str, token: str) -> None:
        if not re.fullmatch(r"[\w.-]+/[\w.-]+", repo):
            raise ValueError(f"bad repo: {repo!r}")
        self.repo, self.token = repo, token

    def call(self, method: str, path: str, body: object | None = None) -> object:
        req = urllib.request.Request(
            f"{API}/repos/{self.repo}{path}",
            data=None if body is None else json.dumps(body).encode(),
            method=method,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 - fixed https host
            raw = resp.read()
        return json.loads(raw) if raw else None

    def paginate(self, path: str) -> list:
        out, page = [], 1
        while True:
            sep = "&" if "?" in path else "?"
            batch = self.call("GET", f"{path}{sep}per_page=100&page={page}")
            if not isinstance(batch, list) or not batch:
                return out
            out.extend(batch)
            page += 1


def post(
    gh: GitHub, pr: int, head: str, summary: str, inline: list[Finding], label: str
) -> None:
    """Write the summary, the new inline comments, and the label."""
    comments = gh.paginate(f"/issues/{pr}/comments")
    mine = next((c for c in comments if MARKER in (c.get("body") or "")), None)
    if mine:
        gh.call("PATCH", f"/issues/comments/{mine['id']}", {"body": summary})
    else:
        gh.call("POST", f"/issues/{pr}/comments", {"body": summary})

    posted = " ".join(c.get("body") or "" for c in gh.paginate(f"/pulls/{pr}/comments"))
    fresh = [f for f in inline if FINDING_MARKER.format(fp=f.fingerprint) not in posted]
    if fresh:
        review = {
            "commit_id": head,
            "event": "COMMENT",
            "body": "AI docs review: findings that need a look. See the summary comment for the rest.",
            "comments": [_review_comment(f) for f in fresh],
        }
        try:
            gh.call("POST", f"/pulls/{pr}/reviews", review)
        except urllib.error.HTTPError as err:
            if err.code != 422:
                raise
            print(
                f"::warning::inline review rejected ({err.code}); findings stay in the summary"
            )

    current = {lbl["name"] for lbl in gh.paginate(f"/issues/{pr}/labels")}
    for name in LABELS:
        if name in current and name != label:
            gh.call("DELETE", f"/issues/{pr}/labels/{urllib.parse.quote(name)}")
    if label not in current:
        color, desc = LABELS[label]
        try:
            gh.call(
                "POST", "/labels", {"name": label, "color": color, "description": desc}
            )
        except urllib.error.HTTPError as err:
            if err.code != 422:  # 422 = already exists
                raise
        gh.call("POST", f"/issues/{pr}/labels", {"labels": [label]})


def _review_comment(f: Finding) -> dict:
    c: dict = {
        "path": f.file,
        "line": f.end_line or f.line,
        "side": "RIGHT",
        "body": render_inline(f),
    }
    if f.end_line and f.line and f.end_line > f.line:
        c["start_line"], c["start_side"] = f.line, "RIGHT"
    return c


# ---------------------------------------------------------------------------
# Commands


def _load_dir(path: Path) -> list[tuple[str, object]]:
    root = path.resolve()
    out = []
    for p in sorted(root.glob("*.json")):
        p.resolve().relative_to(root)
        try:
            out.append((p.stem, json.loads(p.read_text())))
        except (json.JSONDecodeError, UnicodeDecodeError):
            out.append((p.stem, None))
    return out


# Generic credential shapes, checked even when the secret values are unknown.
TOKEN_PATTERNS = [
    re.compile(p)
    for p in (
        r"gh[pousr]_[A-Za-z0-9]{30,}",
        r"github_pat_[A-Za-z0-9_]{40,}",
        r"sk-ant-[A-Za-z0-9_-]{20,}",
        r"AKIA[0-9A-Z]{16}",
        r"xox[abprs]-[A-Za-z0-9-]{10,}",
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    )
]


def _encodings(secret: str) -> set[str]:
    """Forms a model could write a secret in: literal, reversed, hex, base64."""
    raw = secret.encode()
    forms = {secret, secret[::-1], binascii.hexlify(raw).decode()}
    # base64 output depends on alignment; strip the edge characters that
    # depend on neighbouring bytes so a substring match still finds it.
    for pad in range(3):
        for enc in (base64.b64encode, base64.urlsafe_b64encode):
            b = enc(b"\0" * pad + raw).decode().rstrip("=")
            forms.add(b[(pad * 4 + 2) // 3 : -2] if len(b) > 8 else b)
    return {f for f in forms if len(f) >= 8}


def find_secret(text: str, secrets: list[str]) -> bool:
    """True when text contains a known secret in any common encoding, or a token shape."""
    if any(p.search(text) for p in TOKEN_PATTERNS):
        return True
    squashed = re.sub(r"\s+", "", text)
    for secret in secrets:
        if len(secret) < 8:
            continue
        for form in _encodings(secret):
            if form in text or form in squashed:
                return True
    return False


def cmd_sanitize(args: argparse.Namespace) -> int:
    """Rewrite raw findings with public fields only."""
    diff = read_diff(args.base, args.head)
    src, dst = Path(args.input).resolve(), Path(args.output).resolve()
    dst.mkdir(parents=True, exist_ok=True)
    # Secret values reach this step only, never the agent. A hit anywhere
    # withholds every pass, and the match itself is never printed.
    secrets = []
    for line in os.environ.get("AI_REVIEW_SECRETS", "").splitlines():
        # A custom header line is "Name: value"; the value alone is the secret.
        secrets += [line.strip(), line.partition(":")[2].strip()]
    secrets = [s for s in secrets if s]
    raw_text = " ".join(
        p.read_text(errors="replace") for p in sorted(src.glob("*.json")) if p.is_file()
    )
    if find_secret(raw_text, secrets):
        print("::error::A review pass wrote a credential-shaped value. All findings withheld.")
        for skill in SKILLS:
            withheld = {"skill": skill, "ok": False, "withheld": True, "findings": []}
            (dst / f"{skill}.json").write_text(json.dumps(withheld))
        return 1
    for skill in SKILLS:
        raw_path = src / f"{skill}.json"
        result: dict = {
            "skill": skill,
            "ok": False,
            "findings": [],
            "rejected": 0,
            "private": 0,
        }
        if raw_path.is_file():
            try:
                data = json.loads(raw_path.read_text())
            except (json.JSONDecodeError, UnicodeDecodeError):
                data = None
            findings, rejected = parse_findings(data, skill)
            findings, private = screen_private(findings, diff.added_text)
            result.update(
                ok=data is not None,
                rejected=rejected,
                private=private,
                findings=[_public_dict(f) for f in findings],
                task_check=(data or {}).get("task_check")
                if isinstance((data or {}).get("task_check"), dict)
                else None,
                not_checked=[
                    _clean(n, 400)
                    for n in (data or {}).get("not_checked", [])
                    if isinstance(n, str)
                ][:20],
            )
            result["not_checked"], _ = _screen_strings(
                result["not_checked"], diff.added_text
            )
        (dst / f"{skill}.json").write_text(json.dumps(result, indent=1))
        print(
            f"{skill}: ok={result['ok']} findings={len(result['findings'])} rejected={result['rejected']} private={result['private']}"
        )
    return 0


def _screen_strings(items: list[str], diff_text: str) -> tuple[list[str], int]:
    kept = []
    for s in items:
        if any(
            m.group(0).lower() not in diff_text.lower()
            for p in PRIVATE_PATTERNS
            for m in p.finditer(s)
        ):
            continue
        kept.append(s)
    return kept, len(items) - len(kept)


def _public_dict(f: Finding) -> dict:
    return {
        "file": f.file,
        "line": f.line,
        "end_line": f.end_line,
        "severity": f.severity,
        "fix_class": f.fix_class,
        "rule": f.rule,
        "summary": f.summary,
        "replacement": f.replacement,
        "evidence": {"kind": f.evidence_kind, "public": f.evidence_public},
    }


def cmd_post(args: argparse.Namespace) -> int:
    """Merge sanitized findings and post them, or print with --dry-run."""
    diff = read_diff(args.base, args.head)
    findings: list[Finding] = []
    task_checks, not_checked = [], []
    stats = {"rejected": 0, "private": 0, "failed": 0}
    for name, data in _load_dir(Path(args.input)):
        if not isinstance(data, dict) or not data.get("ok"):
            stats["failed"] += 1
            continue
        parsed, rejected = parse_findings(data, name)
        parsed, private = screen_private(parsed, diff.added_text)  # belt and braces
        stats["rejected"] += rejected + int(data.get("rejected", 0))
        stats["private"] += private + int(data.get("private", 0))
        findings.extend(
            f for f in parsed if f.file in diff.files or f.file.startswith("src/")
        )
        if isinstance(data.get("task_check"), dict):
            task_checks.append(data["task_check"])
        not_checked.extend(n for n in data.get("not_checked", []) if isinstance(n, str))
    stats["failed"] += max(0, len(SKILLS) - len(_load_dir(Path(args.input))))

    findings = dedupe(findings)
    findings.sort(key=lambda f: (SEVERITY_RANK[f.severity], f.file, f.line or 0))
    inline = [f for f in findings if _inline_ok(f, diff)][:MAX_INLINE]
    label = choose_label(findings, diff, task_checks) if stats["failed"] == 0 else ""
    summary = render_summary(
        findings, inline, label or "none (a pass failed)", args.head, not_checked, stats
    )

    if args.dry_run:
        print(summary)
        for f in inline:
            print(f"\n--- inline {f.file}:{f.line}\n{render_inline(f)}")
        return 0
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("GITHUB_TOKEN is not set", file=sys.stderr)
        return 1
    gh = GitHub(args.repo, token)
    post(gh, args.pr, args.head, summary, inline, label or LABEL_NEEDS_HUMAN)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("sanitize", "post"):
        p = sub.add_parser(name)
        p.add_argument(
            "--input", required=True, help="Directory of findings JSON files"
        )
        p.add_argument("--base", required=True, help="Merge-base commit SHA")
        p.add_argument("--head", required=True, help="Reviewed commit SHA")
    sub.choices["sanitize"].add_argument("--output", required=True)
    sub.choices["post"].add_argument(
        "--repo", default=os.environ.get("GITHUB_REPOSITORY", "")
    )
    sub.choices["post"].add_argument("--pr", type=int, required=True)
    sub.choices["post"].add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    return cmd_sanitize(args) if args.command == "sanitize" else cmd_post(args)


if __name__ == "__main__":
    sys.exit(main())
