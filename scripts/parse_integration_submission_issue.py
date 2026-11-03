#!/usr/bin/env python3
"""Parse a GitHub issue-form body for integration submissions into JSON.

GitHub issue forms render as markdown sections headed by ``### <label>``.
This script maps those labels to stable keys for the Deep Agents workflow.
It does not execute or evaluate field values.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any


# Issue-form section titles -> output keys.
FIELD_MAP: dict[str, str] = {
    "Display or class name": "display_name",
    "Language": "language",
    "Component type": "component",
    "PyPI package name": "pypi_package",
    "npm package name": "npm_package",
    "Docs URL": "docs_url",
    "Source repository": "github_repo",
    "Short provider description": "provider_description",
    "Capability flags (optional)": "capability_notes",
    "Confirmations": "confirmations",
}

HEADING_RE = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)


def _parse_sections(body: str) -> dict[str, str]:
    matches = list(HEADING_RE.finditer(body))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        value = body[start:end].strip()
        # Checkbox forms often include HTML comments; drop them.
        value = re.sub(r"<!--.*?-->", "", value, flags=re.DOTALL).strip()
        sections[title] = value
    return sections


def _clean_optional(value: str) -> str | None:
    value = value.strip()
    if not value or value.lower() in {"n/a", "na", "none", "_no response_"}:
        return None
    return value


def parse_issue_body(body: str) -> dict[str, Any]:
    sections = _parse_sections(body or "")
    parsed: dict[str, Any] = {}
    missing: list[str] = []

    for title, key in FIELD_MAP.items():
        if title not in sections:
            if key in {
                "pypi_package",
                "npm_package",
                "github_repo",
                "capability_notes",
                "confirmations",
            }:
                parsed[key] = None if key != "confirmations" else []
                continue
            missing.append(title)
            continue
        raw = sections[title]
        if key == "confirmations":
            checked = re.findall(r"^\s*-\s*\[x\]\s*(.+?)\s*$", raw, flags=re.IGNORECASE | re.MULTILINE)
            parsed[key] = checked
            continue
        cleaned = _clean_optional(raw)
        parsed[key] = cleaned

    errors: list[str] = []
    if missing:
        errors.append(f"Missing required sections: {', '.join(missing)}")

    language = (parsed.get("language") or "").strip()
    pypi = parsed.get("pypi_package")
    npm = parsed.get("npm_package")
    if language in {"Python", "Both"} and not pypi:
        errors.append("PyPI package name is required when Language is Python or Both")
    if language in {"TypeScript", "Both"} and not npm:
        errors.append("npm package name is required when Language is TypeScript or Both")
    if not parsed.get("display_name"):
        errors.append("Display or class name is required")
    if not parsed.get("component"):
        errors.append("Component type is required")
    if not parsed.get("docs_url"):
        errors.append("Docs URL is required")
    if not parsed.get("provider_description"):
        errors.append("Short provider description is required")

    return {
        "ok": not errors,
        "errors": errors,
        "fields": parsed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--body-file",
        help="Path to a file containing the issue body (default: stdin)",
    )
    parser.add_argument(
        "--issue-number",
        type=int,
        help="GitHub issue number to include in the payload",
    )
    parser.add_argument(
        "--issue-url",
        help="GitHub issue URL to include in the payload",
    )
    parser.add_argument(
        "--author",
        help="GitHub login of the issue author",
    )
    args = parser.parse_args()

    if args.body_file:
        body = open(args.body_file, encoding="utf-8").read()
    else:
        body = sys.stdin.read()

    result = parse_issue_body(body)
    result["issue_number"] = args.issue_number
    result["issue_url"] = args.issue_url
    result["author"] = args.author
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
