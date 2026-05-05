"""Extract Bluehawk-style code snippets using line-based parsing (no JS/TS lexer).

Bluehawk's TypeScript parser mis-tokenizes the substring ``/**`` inside string literals
(for example ``"/**"``) as a block comment, which breaks ``// :snippet-end:`` handling.
This tool only looks for comment-line markers, so glob patterns and other strings are safe.

Supported markers (same as this repo's Bluehawk usage):

- ``# :snippet-start: <id>`` / ``# :snippet-end:`` (Python)
- ``// :snippet-start: <id>`` / ``// :snippet-end:`` (TypeScript)
- ``# :remove-start:`` / ``# :remove-end:`` inside Python snippet bodies
- ``// :remove-start:`` / ``// :remove-end:`` inside TypeScript snippet bodies

Output files match Bluehawk: ``<source-basename>.snippet.<snippet-id>.<ext>`` in
``src/code-samples-generated/``.

Run from repo root: ``python scripts/extract_code_snippets.py``
or via ``make code-snippets``.
"""

from __future__ import annotations

import re
import sys
import textwrap
from pathlib import Path

# Markers may be indented (e.g. inside a function body).
_RE_SNIP_START_PY = re.compile(r"^\s*#\s*:snippet-start:\s*(\S+)\s*$")
_RE_SNIP_END_PY = re.compile(r"^\s*#\s*:snippet-end:\s*$")
_RE_REMOVE_START_PY = re.compile(r"^\s*#\s*:remove-start:\s*$")
_RE_REMOVE_END_PY = re.compile(r"^\s*#\s*:remove-end:\s*$")

_RE_SNIP_START_TS = re.compile(r"^\s*//\s*:snippet-start:\s*(\S+)\s*$")
_RE_SNIP_END_TS = re.compile(r"^\s*//\s*:snippet-end:\s*$")
_RE_REMOVE_START_TS = re.compile(r"^\s*//\s*:remove-start:\s*$")
_RE_REMOVE_END_TS = re.compile(r"^\s*//\s*:remove-end:\s*$")


def _strip_remove_regions(
    body: str,
    *,
    start: re.Pattern[str],
    end: re.Pattern[str],
) -> str:
    """Remove :remove-start: / :remove-end: regions, including the marker lines."""
    lines = body.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        if start.match(lines[i]):
            i += 1
            while i < len(lines) and not end.match(lines[i]):
                i += 1
            if i < len(lines):
                i += 1
            else:
                msg = "unclosed :remove-end: inside snippet"
                raise ValueError(msg)
            continue
        out.append(lines[i])
        i += 1
    return "".join(out)


def extract_snippets(
    text: str,
    *,
    language: str,
) -> list[tuple[str, str]]:
    """Return (snippet_id, body) for each ``:snippet-start:`` block in *text*."""
    if language == "python":
        start_re, end_re = _RE_SNIP_START_PY, _RE_SNIP_END_PY
        rs, re_ = _RE_REMOVE_START_PY, _RE_REMOVE_END_PY
    elif language in ("ts", "typescript", "javascript"):
        start_re, end_re = _RE_SNIP_START_TS, _RE_SNIP_END_TS
        rs, re_ = _RE_REMOVE_START_TS, _RE_REMOVE_END_TS
    else:
        msg = f"unsupported language: {language!r}"
        raise ValueError(msg)

    # Use universal newlines; preserve line endings in collected bodies via splitlines(keepends=True).
    lines = text.splitlines(keepends=True)
    results: list[tuple[str, str]] = []
    i = 0
    while i < len(lines):
        m = start_re.match(lines[i])
        if not m:
            i += 1
            continue
        snippet_id = m.group(1)
        i += 1
        buf: list[str] = []
        while i < len(lines):
            if end_re.match(lines[i]):
                i += 1
                raw = "".join(buf)
                processed = _strip_remove_regions(raw, start=rs, end=re_)
                processed = textwrap.dedent(processed)
                results.append((snippet_id, processed))
                break
            buf.append(lines[i])
            i += 1
        else:
            msg = f"unclosed snippet {snippet_id!r}"
            raise ValueError(msg)

    return results


def _iter_source_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for path in sorted(root.rglob("*.py")):
        if "node_modules" in path.parts:
            continue
        out.append(path)
    for path in sorted(root.rglob("*.ts")):
        if "node_modules" in path.parts:
            continue
        out.append(path)
    return out


def _language_for_path(path: Path) -> str:
    if path.suffix == ".py":
        return "python"
    if path.suffix == ".ts":
        return "ts"
    msg = f"expected .py or .ts, got {path.suffix!r}"
    raise ValueError(msg)


def _normalize_newlines(s: str) -> str:
    """Ensure single trailing newline, Unix line endings in output."""
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    if s and not s.endswith("\n"):
        s += "\n"
    return s


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    code_samples = repo_root / "src" / "code-samples"
    out_dir = repo_root / "src" / "code-samples-generated"

    if not code_samples.is_dir():
        print(f"error: missing {code_samples}", file=sys.stderr)
        return 1

    out_dir.mkdir(parents=True, exist_ok=True)

    for p in list(out_dir.iterdir()):
        if p.suffix in (".py", ".ts") and p.is_file():
            p.unlink()

    written: list[Path] = []
    for path in _iter_source_files(code_samples):
        language = _language_for_path(path)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as e:
            print(f"error: read {path}: {e}", file=sys.stderr)
            return 1
        try:
            pairs = extract_snippets(text, language=language)
        except ValueError as e:
            print(f"error: {path.relative_to(repo_root)}: {e}", file=sys.stderr)
            return 1
        for snippet_id, body in pairs:
            body = _normalize_newlines(body)
            out_path = out_dir / f"{path.stem}.snippet.{snippet_id}.{path.suffix.lstrip('.')}"
            out_path.write_text(body, encoding="utf-8", newline="\n")
            written.append(out_path)

    for w in sorted(written, key=lambda p: str(p)):
        print(f"Wrote {w.relative_to(repo_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
