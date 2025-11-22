#!/usr/bin/env python3
"""Filter broken links output from Mintlify.

This script can optionally filter the output from 'mint broken-links' to:
1. Skip entire sections for integration directories (oss/python/integrations/
    and oss/javascript/integrations/)
2. Count only the visible broken links
3. Update the final summary with the correct count

Usage:
    python3 filter_broken_links.py [--exclude-integrations]

    --exclude-integrations: Filter out integration directories (default: show all)
"""

import argparse
import re
import sys


def filter_broken_links(input_stream, exclude_integrations=False):
    """Filter broken links output, optionally excluding integration directories."""
    skip = False
    link_count = 0

    for line in input_stream:
        line = line.rstrip()

        if exclude_integrations:
            # Check if this is an integration file header
            if re.match(r"^oss/(python|javascript)/integrations/", line):
                skip = True
                continue

            # Check if this is a new file header (reset skip)
            if re.match(r"^[a-zA-Z]", line) and not re.match(r"^[ \t]", line):
                skip = False

        # If we're not skipping, process the line
        if not skip:
            # Count broken links (indented lines starting with /)
            if re.match(r"^[ \t]+/", line):
                link_count += 1

            # Update the summary line with correct count
            if "broken links found." in line:
                if exclude_integrations:
                    line = re.sub(
                        r"\d+ broken links found\.",
                        f"{link_count} broken links found (excluding integrations).",
                        line,
                    )
                else:
                    line = re.sub(
                        r"\d+ broken links found\.",
                        f"{link_count} broken links found.",
                        line,
                    )

            print(line)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Filter broken links output from Mintlify"
    )
    parser.add_argument(
        "--exclude-integrations",
        action="store_true",
        help="Filter out integration directories",
    )

    args = parser.parse_args()

    try:
        filter_broken_links(sys.stdin, exclude_integrations=args.exclude_integrations)
    except KeyboardInterrupt:
        sys.exit(1)
    except BrokenPipeError:
        # Handle broken pipe gracefully
        sys.exit(0)


if __name__ == "__main__":
    main()
