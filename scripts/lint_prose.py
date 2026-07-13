#!/usr/bin/env python3
"""Fallback prose checker for docs when Vale is unavailable.

This is intentionally lightweight: it catches the most common literal-identifier
mistakes in changelog copy so `make lint_prose` still works in environments
where the Vale binary is not installed.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HTTP_METHOD_RE = re.compile(r'(?<!`)\b(POST|GET|PUT|PATCH|DELETE) /[^`\s]+')
ENV_VAR_RE = re.compile(r'(?<!`)(?:[A-Z][A-Z0-9_]*_[A-Z0-9_]+)')
# Lightweight checks for a few common doc identifiers that should be backticked
# when mentioned as literals.
LITERAL_PHRASES = [
    re.compile(r'(?<!`)\bLANGSMITH_ENDPOINT\b'),
    re.compile(r'(?<!`)\bOTEL_RESOURCE_ATTRIBUTES\b'),
    re.compile(r'(?<!`)\bFF_BULK_EXPORT_DEFAULT_COMPRESSION\b'),
    re.compile(r'(?<!`)\bENGINE_ANTHROPIC_BASE_URL\b'),
    re.compile(r'(?<!`)\bdefault_redirect_uri\b'),
    re.compile(r'(?<!`)\btest_thread_id\b'),
    re.compile(r'(?<!`)\bsession_id\b'),
]
DOUBLE_SPACE_RE = re.compile(r'\b[a-z]+\s{2,}[a-z]')


def iter_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(sorted(p for p in path.rglob("*") if p.suffix in {".md", ".mdx"}))
        else:
            files.append(path)
    return files


def main(argv: list[str]) -> int:
    if argv:
        input_paths = [Path(arg) for arg in argv]
    else:
        input_paths = [Path("src")]

    files = iter_files(input_paths)
    if not files:
        print("No files to lint.")
        return 0

    issues: list[str] = []
    for file_path in files:
        try:
            text = file_path.read_text()
        except FileNotFoundError:
            issues.append(f"{file_path}: file not found")
            continue

        for lineno, line in enumerate(text.splitlines(), start=1):
            for regex in (HTTP_METHOD_RE, DOUBLE_SPACE_RE, *LITERAL_PHRASES):
                if regex.search(line):
                    issues.append(f"{file_path}:{lineno}: {line.strip()}")
                    break

    if issues:
        print("Fallback prose checks found issues:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print(f"Fallback prose checks passed for {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
