#!/usr/bin/env python3
"""Filter mint broken-links output to only include blocks for specified files.

Reads from stdin, writes to stdout.
Usage: mint broken-links 2>&1 | python filter_broken_links_by_file.py [pattern1 pattern2 ...]
Patterns match if the build path (e.g. langsmith/admin.mdx) contains the pattern.
"""

import sys


def main() -> None:
    patterns = sys.argv[1:]
    lines = sys.stdin.read().split("\n")
    out: list[str] = []
    current_file: str | None = None

    for line in lines:
        if not line or line[0].isspace():
            # Indented line or blank: belongs to current block
            if patterns and current_file and any(p in current_file for p in patterns):
                out.append(line)
        else:
            # File header
            current_file = line.strip()
            if not patterns or any(p in current_file for p in patterns):
                out.append(line)

    sys.stdout.write("\n".join(out))


if __name__ == "__main__":
    main()
