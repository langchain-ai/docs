#!/usr/bin/env python3
"""Build the Managed Deep Agents OAuth catalog table from the `mda` CLI.

The catalog is compiled into the CLI, so it changes with each release. This script reads it
from the installed binary instead of tracking it by hand:

  uv run python scripts/refresh_mda_oauth_catalog.py           # print the table for inspection
  uv run python scripts/refresh_mda_oauth_catalog.py --write   # overwrite the snippet

Data comes from `mda connections catalog --json`. That command reads a catalog compiled into
the binary, so it needs no LangSmith API key or workspace ID. Upgrade the CLI before running
this (`uv tool upgrade --pre managed-deepagents`), because the output only ever reflects the
version installed locally.

`--write` overwrites `src/snippets/langsmith/mda-oauth-catalog.mdx` with **the markdown table
only**. Document prose lives in `managed-deep-agents-connections.mdx`, which imports the
snippet. Do not edit the snippet by hand.

Columns are the `--oauth` value, the provider's app registration page (linked from its display
name), and the catalog's default scopes. Authorization and token URLs are deliberately omitted:
supplying those is what the catalog saves you from doing.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

_REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SNIPPET_RELPATH = "src/snippets/langsmith/mda-oauth-catalog.mdx"
DEFAULT_SNIPPET_PATH = _REPO_ROOT / DEFAULT_SNIPPET_RELPATH

CLI_TIMEOUT_SECONDS = 60
NO_SCOPES = "None"


def _resolve_mda(explicit: str | None) -> Path:
    """Return an executable `mda` path, or exit with a usable message."""
    found = explicit or shutil.which("mda")
    if not found:
        sys.exit(
            "error: `mda` not found on PATH. Install it with "
            "`uv tool install --pre managed-deepagents`, or pass --mda-bin."
        )
    path = Path(found).resolve()
    if not path.is_file():
        sys.exit(f"error: {path} is not a file")
    return path


def _fetch_catalog(mda: Path) -> list[dict[str, Any]]:
    """Run the catalog command and return its parsed JSON array."""
    try:
        proc = subprocess.run(  # noqa: S603 - fixed argv, shell=False, resolved binary
            [str(mda), "connections", "catalog", "--json"],
            capture_output=True,
            text=True,
            timeout=CLI_TIMEOUT_SECONDS,
            check=False,
            shell=False,
        )
    except subprocess.TimeoutExpired:
        sys.exit(f"error: `mda connections catalog --json` timed out after {CLI_TIMEOUT_SECONDS}s")

    if proc.returncode != 0:
        sys.exit(f"error: `mda connections catalog --json` exited {proc.returncode}\n{proc.stderr.strip()}")

    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        sys.exit(f"error: could not parse catalog JSON: {exc}")

    if not isinstance(data, list) or not data:
        sys.exit("error: catalog JSON was not a non-empty array")
    return data


def _cell(value: str) -> str:
    """Escape a value for a markdown table cell."""
    return value.replace("|", "\\|").strip()


def _https_url(value: Any) -> str | None:
    """Return value if it is a well-formed absolute https URL, else None."""
    if not isinstance(value, str) or not value:
        return None
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        return None
    return value


def _register_cell(entry: dict[str, Any]) -> str:
    """Provider display name, linked to its app registration page when there is one."""
    name = _cell(str(entry.get("display_name") or entry.get("service") or ""))
    url = _https_url(entry.get("client_registration_url"))
    return f"[{name}]({url})" if url else name


def _scopes_cell(entry: dict[str, Any]) -> str:
    """Default scopes as inline code, or a marker when the catalog sets none."""
    scopes = entry.get("default_scopes")
    if not isinstance(scopes, list):
        return NO_SCOPES
    rendered = [f"`{_cell(str(s))}`" for s in scopes if str(s).strip()]
    return " ".join(rendered) if rendered else NO_SCOPES


def build_table(entries: list[dict[str, Any]]) -> str:
    """Render the catalog as a markdown table, sorted by service name."""
    rows = [
        "| `--oauth` value | Register an app | Default scopes |",
        "| --- | --- | --- |",
    ]
    skipped: list[str] = []
    for entry in sorted(entries, key=lambda e: str(e.get("service", ""))):
        service = _cell(str(entry.get("service", "")))
        if not service:
            skipped.append(repr(entry)[:60])
            continue
        rows.append(f"| `{service}` | {_register_cell(entry)} | {_scopes_cell(entry)} |")
    if skipped:
        print(f"warning: skipped {len(skipped)} entries with no service name", file=sys.stderr)
    return "\n".join(rows) + "\n"


def _write_snippet(path: Path, body: str) -> None:
    """Write the table, refusing any destination outside the repository."""
    resolved = path if path.is_absolute() else (_REPO_ROOT / path)
    resolved = resolved.resolve()
    if not resolved.is_relative_to(_REPO_ROOT):
        sys.exit(f"error: refusing to write outside the repository: {resolved}")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(body, encoding="utf-8")
    print(f"wrote {resolved.relative_to(_REPO_ROOT)}")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Regenerate the MDA OAuth catalog snippet from `mda connections catalog --json`"
    )
    ap.add_argument("--mda-bin", help="Path to the mda binary (default: the one on PATH).")
    ap.add_argument(
        "--write",
        action="store_true",
        help=f"Overwrite the snippet (default: {DEFAULT_SNIPPET_RELPATH}) with the generated table",
    )
    ap.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_SNIPPET_PATH,
        help=f"Output snippet path (default: repo / {DEFAULT_SNIPPET_RELPATH}).",
    )
    args = ap.parse_args()

    entries = _fetch_catalog(_resolve_mda(args.mda_bin))
    table = build_table(entries)

    if not args.write:
        sys.stdout.write(table)
        return 0
    _write_snippet(args.file, table)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
