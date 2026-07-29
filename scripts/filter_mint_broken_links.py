#!/usr/bin/env python3
"""Filter mint broken-links output for known false positives.

Mint crawls ``build/snippets/**`` as standalone pages. After language-prefixed
snippet copies (see ``DocumentationBuilder._process_snippet_markdown_file``),
wrong-language copies look broken (e.g. ``snippets/javascript/oss/python-*.mdx``
with ``/oss/javascript/...`` links to Python-only pages). Drop those sections
only; keep matching-language and shared snippet reports so real breaks still
surface.

Also drops OpenAPI-generated paths that exist at deploy time but not in local
builds, and legacy relative-path false positives.

Reads mint output from stdin (or --input), writes filtered output to stdout.
Pass --check-anchors to also drop known smithdb migration anchor false positives.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import PurePosixPath

EXCLUDE_SUBSTRINGS = (
    "/langsmith/agent-server-api/",
    "/langsmith/smith-api",
    "/api-reference/",
    "../langchain/",
    "../integrations/",
    "../langgraph/local-server",
)

SMITHDB_ANCHOR_RE = re.compile(
    r"/langsmith/smithdb-sdk-migration#(traces-query|runs-query|exceptions)$"
)

_FILE_SUFFIXES = (".mdx", ".md", ".jsx", ".tsx", ".html")
_LANG_DIRS = frozenset({"python", "javascript"})


def _is_file_header(line: str) -> bool:
    """Return True if line looks like a mint broken-links file header."""
    if not line or line[0].isspace():
        return False
    stripped = line.strip()
    return stripped.endswith(_FILE_SUFFIXES)


def is_cross_language_snippet(path: str) -> bool:
    """Return True if this standalone snippet copy has the wrong language prefix.

    Language-specific download/featured snippets are named ``python-*`` or
    ``javascript-*``. Emitting both language copies rewrites ``/oss/`` links to
    that copy's language, which breaks for the mismatched copy. The default
    ``snippets/oss/...`` path is always Python-prefixed, so ``javascript-*``
    files there are also mismatches.
    """
    if not path.startswith("snippets/"):
        return False

    parts = PurePosixPath(path).parts
    filename = parts[-1]

    if len(parts) >= 2 and parts[1] in _LANG_DIRS:
        lang = parts[1]
        if filename.startswith("python-") and lang != "python":
            return True
        if filename.startswith("javascript-") and lang != "javascript":
            return True
        return False

    # Default path (no language dir): content is Python-prefixed.
    return filename.startswith("javascript-")


def filter_broken_links(text: str, *, check_anchors: bool = False) -> str:
    """Drop cross-language snippet sections and known false-positive link lines."""
    text = text.replace("\u00a0", " ")
    out: list[str] = []
    skip_section = False

    for line in text.splitlines(keepends=True):
        if _is_file_header(line):
            skip_section = is_cross_language_snippet(line.strip())
        if skip_section:
            continue
        if any(s in line for s in EXCLUDE_SUBSTRINGS):
            continue
        if check_anchors and SMITHDB_ANCHOR_RE.search(line.rstrip("\n")):
            continue
        out.append(line)

    return "".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-anchors",
        action="store_true",
        help="Also filter known smithdb migration anchor false positives",
    )
    parser.add_argument(
        "--input",
        default="-",
        help="Path to mint output (default: stdin)",
    )
    args = parser.parse_args()

    if args.input == "-":
        text = sys.stdin.read()
    else:
        with open(args.input, encoding="utf-8") as f:
            text = f.read()

    sys.stdout.write(filter_broken_links(text, check_anchors=args.check_anchors))


if __name__ == "__main__":
    main()
