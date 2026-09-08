#!/usr/bin/env python3
"""Filter mint broken-links output for known false positives.

Mint checks snippet MDX as standalone files. Snippet /oss/ links are rewritten to
absolute language-prefixed paths (build/snippets/{python|javascript}/...) and only
resolve correctly when imported into a page, so snippet reports are dropped.

Also drops OpenAPI-generated paths that exist at deploy time but not in local builds.

Reads mint output from stdin (or --input), writes filtered output to stdout.
Pass --check-anchors to also drop known smithdb migration anchor false positives.
"""

from __future__ import annotations

import argparse
import re
import sys

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


def _is_file_header(line: str) -> bool:
    """Return True if line looks like a mint broken-links file header."""
    if not line or line[0].isspace():
        return False
    stripped = line.strip()
    return stripped.endswith(_FILE_SUFFIXES)


def filter_broken_links(text: str, *, check_anchors: bool = False) -> str:
    """Drop snippet sections and known false-positive link lines."""
    text = text.replace("\u00a0", " ")
    out: list[str] = []
    skip_snippet = False

    for line in text.splitlines(keepends=True):
        if _is_file_header(line):
            skip_snippet = line.startswith("snippets/")
        if skip_snippet:
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
