#!/usr/bin/env python3
"""Build a model x eval-category table (per-category correctness as a percentage).

Data comes from the `category_scores` field in each `evals_summary.json` (inside the
`evals-summary` workflow artifact) in recent successful [Evals - GHA](
https://github.com/langchain-ai/deepagents/actions/workflows/evals.yml) runs. Runs are
processed from **newest to oldest**; the first time we see a **(model, category)** pair
wins, so the table shows the most recent result for that pair.

  export GITHUB_TOKEN=ghp_...  # read access to Actions artifacts for langchain-ai/deepagents
  python3 -m pip install requests
  python scripts/refresh_deepagents_category_matrix.py
  python scripts/refresh_deepagents_category_matrix.py --write  # overwrites the snippet; models.mdx includes it

With no `GITHUB_TOKEN` or if CI did not return scores, the table still has headers and a single
status row.

`--write` overwrites the snippet with **the markdown table only** (no intro; document prose lives in
`models.mdx`).

The table uses a fixed set of six eval categories (see `FIXED_CATEGORY_COLUMNS` in the script)
plus a **Model** column; rows are ordered by **provider** (google_genai, openai, anthropic, then
other `provider:model` ids alphabetically by provider and model). The **highest** score in each
category column is shown in **bold** (tied scores are all bolded). Models with **fewer than four**
of the six category scores are **omitted** (see `MIN_FILLED_CATEGORIES` in the script).
"""

from __future__ import annotations

import argparse
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from typing import Any, Optional, Tuple

# (percentage label, source workflow run `html_url` for that `evals_summary` row)
CellData = Tuple[str, Optional[str]]

_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
from gh_artifact_download import download_artifact_bytes as _download_artifact_bytes

# Written by --write. models.mdx imports and renders it.
DEFAULT_SNIPPET_RELPATH = "src/snippets/deepagents-eval-category-matrix.mdx"
DEFAULT_SNIPPET_PATH = _REPO_ROOT / DEFAULT_SNIPPET_RELPATH

OWNER = "langchain-ai"
REPO = "deepagents"
WORKFLOW_ID = 240654164

# Fixed six eval categories (excludes `unit_test`): `category_scores` id -> table header.
FIXED_CATEGORY_COLUMNS: list[Tuple[str, str]] = [
    ("file_operations", "File Ops"),
    ("retrieval", "Retrieval"),
    ("tool_use", "Tool Use"),
    ("memory", "Memory"),
    ("conversation", "Conversation"),
    ("summarization", "Summarization"),
]
FIXED_CATEGORY_KEYS: list[str] = [a for a, _ in FIXED_CATEGORY_COLUMNS]
FIXED_HEADER_LABELS: list[str] = [b for _, b in FIXED_CATEGORY_COLUMNS]

# Minimum number of the six fixed categories with a non-missing score; sparser rows are not shown.
MIN_FILLED_CATEGORIES: int = 4

# `provider:model` keys: primary provider order, then all other provider ids A–Z, then model id.
TIER1_PROVIDERS: tuple[str, str, str] = ("google_genai", "openai", "anthropic")


def _parse_provider_id(model_key: str) -> str:
    if ":" in model_key:
        return str(model_key.split(":", 1)[0]).strip()
    return ""


def _model_key_sort_key(model_key: str) -> tuple:
    prov = _parse_provider_id(model_key)
    mkl = model_key.lower()
    if prov in TIER1_PROVIDERS:
        return (0, TIER1_PROVIDERS.index(prov), mkl)
    if prov:
        return (1, prov.lower(), mkl)
    return (2, "", mkl)


def _column_maxima(
    merged: dict[str, dict[str, CellData]], cat_keys: list[str]
) -> dict[str, float | None]:
    """Largest 0..100 value per column, or None if the column is all non-numeric."""
    out: dict[str, float | None] = {}
    for c in cat_keys:
        vals: list[float] = []
        for rowd in merged.values():
            x = _parse_pct_to_0_100(rowd.get(c, ("—", None))[0])
            if x is not None:
                vals.append(x)
        out[c] = max(vals) if vals else None
    return out


def _is_best_in_column(pct: str, col_max: float | None) -> bool:
    v = _parse_pct_to_0_100(pct)
    if v is None or col_max is None:
        return False
    return v == col_max


def _token() -> str | None:
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if t in (None, "", "notset"):
        return None
    return t


def _get_json(path: str, token: str | None) -> Any:
    url = f"https://api.github.com{path}" if path.startswith("/") else path
    req = urllib.request.Request(
        url,
        headers={"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"},
    )
    if token:
        # Classic PAT: both `Bearer` and `token` work; try Bearer first.
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def _github_api_error_context(exc: urllib.error.HTTPError) -> str:
    body: bytes
    try:
        body = exc.read()
    except (OSError, TypeError, AttributeError):
        try:
            b = exc.fp
            if b is None or not hasattr(b, "read"):
                return ""
            body = b.read()
        except (OSError, TypeError, AttributeError):
            return ""
    if not body:
        return ""
    try:
        o = json.loads(body.decode("utf-8", errors="replace"))
        m = o.get("message", "")
        if m:
            return f" (API message: {m})"
    except (TypeError, ValueError, json.JSONDecodeError, AttributeError):
        pass
    return ""


def _fetch_runs(per_page: int) -> list[dict[str, Any]]:
    path = (
        f"/repos/{OWNER}/{REPO}/actions/workflows/{WORKFLOW_ID}/runs"
        f"?per_page={per_page}&status=completed"
    )
    data = _get_json(path, None)
    return list(data.get("workflow_runs") or [])


def _list_artifacts(run_id: int, token: str) -> list[dict[str, Any]]:
    path = f"/repos/{OWNER}/{REPO}/actions/runs/{run_id}/artifacts?per_page=100"
    data = _get_json(path, token)
    return list(data.get("artifacts") or [])


def _print_artifact_access_help(first_err: str) -> None:
    print(
        "No evals-summary zips were opened. First error encountered:\n  ",
        first_err,
        file=sys.stderr,
    )
    if "list artifacts" in first_err and "403" in first_err:
        org = "langchain-ai"
        print(
            f"\nHTTP 403 on **list workflow run artifacts** means GitHub rejected the token for "
            f"Actions in `{OWNER}/{REPO}` (this is the API call to browse artifacts, before download). "
            f"That almost always is one of:\n\n"
            f"1. **SAML / SSO (most common for `{org}`)**: A fine-grained or classic token must be "
            f"**SSO-authorized** for the org. In GitHub: **Settings** → **Developer settings** → "
            f"**Personal access tokens** → find this token → **Configure SSO** or **Enable SSO** → "
            f"**Authorize** for **{org}**.\n\n"
            f"2. **Fine-grained token**: **Repository access** must list **`{OWNER}/{REPO}`** (not a fork). "
            f"**Repository permissions** → **Actions** → **Read**.\n\n"
            f"3. **Use GitHub CLI** (its token is often already SSO-authorized). Run: "
            f"`gh auth login` then: `export GITHUB_TOKEN=\"$(gh auth token)\"` and run this script again."
            f"\n",
            file=sys.stderr,
        )
    else:
        print(
            "\nIf 401/403: fine-grained token needs **Actions: Read** on this repo; for SAML orgs, "
            "SSO-authorize the token. Classic token may need **repo** scope. "
            "For download errors (S3, not this list error), the script already uses the `requests` package.",
            file=sys.stderr,
        )


def _extract_evals_summary(zip_data: bytes) -> list[dict[str, object]] | None:
    z = zipfile.ZipFile(io.BytesIO(zip_data))
    for n in z.namelist():
        if n.endswith("evals_summary.json"):
            parsed = json.loads(z.read(n).decode("utf-8"))
            if isinstance(parsed, list):
                return [dict(x) for x in parsed]
    return None


def _fmt_pct(raw: object) -> str:
    if raw is None or raw == "—":
        return "—"
    if isinstance(raw, str) and not raw.strip():
        return "—"
    s = str(raw).strip()
    if s in ("n/a", "—", "N/A", "NaN", "null"):
        return "—"
    try:
        v = float(s)
    except (TypeError, ValueError):
        return "—"
    if v < 0:
        return "—"
    if v > 1.0 + 1e-6:
        if v > 100.0 + 1e-6:
            return "—"
        return f"{round(v):d}%"
    return f"{round(100.0 * v):d}%"


def _parse_pct_to_0_100(pct: str) -> float | None:
    """Parse a table cell like `87%` to a 0..100 float (sorting, column max, bolding)."""
    if not pct or pct == "—":
        return None
    t = str(pct).strip().rstrip("%")
    try:
        n = float(t)
    except (TypeError, ValueError):
        return None
    if n < 0 or n > 100.0 + 1e-6:
        return None
    return n


def _filled_category_count(rowd: dict[str, CellData], cat_keys: list[str]) -> int:
    """How many of the fixed columns have a parseable 0..100% score (including 0%)."""
    n = 0
    for c in cat_keys:
        if _parse_pct_to_0_100(rowd.get(c, ("—", None))[0]) is not None:
            n += 1
    return n


def _escape_md_cell(s: str) -> str:
    return s.replace("|", r"\|")


def _format_stat_cell(cell: CellData, *, bold: bool = False) -> str:
    """Format `NN%` and optionally link to the source workflow run; bold the cell when True."""
    pct, run_url = cell
    if not run_url or not pct or pct == "—":
        inner = _escape_md_cell(pct) if pct else "—"
    else:
        # Avoid breaking the markdown link label: escape ] if present
        label = pct.replace("]", r"\]")
        inner = f"[{label}]({run_url})"
    if bold and inner and inner != "—":
        return f"**{inner}**"
    return inner


def _run_html_url(r: dict[str, Any], rid: int) -> str:
    u = str(r.get("html_url", "")).strip()
    if u:
        return u
    return f"https://github.com/{OWNER}/{REPO}/actions/runs/{rid}"


def _merge_rows(
    runs: list[dict[str, Any]],
    token: str,
) -> tuple[dict[str, dict[str, CellData]], int]:
    """model_id -> category_id -> (NN% text, run link); count of evals-summary zips we opened."""
    out: dict[str, dict[str, CellData]] = {}
    n_fetch = 0
    runs = sorted(
        [x for x in runs if str(x.get("conclusion", "")) == "success"],
        key=lambda r: str(r.get("created_at", "")),
        reverse=True,
    )
    first_err: str | None = None
    for r in runs:
        rid = int(r["id"])
        time.sleep(0.1)
        try:
            arts = _list_artifacts(rid, token)
        except urllib.error.HTTPError as e:
            if first_err is None:
                first_err = (
                    f"list artifacts for run {rid}: {e!s}{_github_api_error_context(e)}"
                )
            continue
        except OSError as e:
            if first_err is None:
                first_err = f"list artifacts for run {rid}: {e}"
            continue
        ev = next((a for a in arts if a.get("name") == "evals-summary"), None)
        if not ev:
            continue
        dl = str(ev.get("archive_download_url", ""))
        if not dl:
            continue
        try:
            data = _download_artifact_bytes(dl, token)
        except SystemExit:
            raise
        except Exception as e:  # noqa: BLE001
            if first_err is None:
                first_err = f"download artifact (run {rid}): {e!r}"
            continue
        n_fetch += 1
        run_url = _run_html_url(r, rid)
        reports = _extract_evals_summary(data) or []
        for rep in reports:
            mid = str(rep.get("model", "")).strip()
            if not mid:
                continue
            sc = rep.get("category_scores")
            if not isinstance(sc, dict):
                continue
            m_out = out.setdefault(mid, {})
            for cat, val in sc.items():
                ckey = str(cat)
                if ckey in m_out:
                    continue
                pct = _fmt_pct(val)
                m_out[ckey] = (pct, run_url)
    if n_fetch == 0 and token:
        if first_err:
            _print_artifact_access_help(first_err)
        else:
            print(
                "Scanned success runs but none listed an `evals-summary` artifact. "
                "Try increasing --per-page.",
                file=sys.stderr,
            )
    return out, n_fetch


def _table_with_status_row(
    status_first_cell: str, cat_keys: list[str], display_headers: list[str]
) -> str:
    """A full-width status message in the Model column; other columns are em dashes."""
    if len(cat_keys) != len(display_headers):
        raise ValueError("cat_keys and display_headers must be the same length")
    headers: list[str] = [
        "Model",
        *[_escape_md_cell(h) for h in display_headers],
    ]
    ncols = len(headers)
    tlines: list[str] = [
        "| " + " | ".join(headers) + " |",
        "| :--- |" + " ---: |" * (ncols - 1),
        f"| {status_first_cell} | " + " | ".join(["—"] * (ncols - 1)) + " |",
    ]
    return "\n".join(tlines) + "\n"


def _table_markdown(
    token: str | None,
    merged: dict[str, dict[str, CellData]],
    cat_keys: list[str],
    display_headers: list[str],
    n_fetched: int,
    n_models_unfiltered: int = 0,
) -> str:
    """Markdown for the data table only (for the generated snippet; no intro or callouts)."""
    if len(cat_keys) != len(display_headers):
        raise ValueError("cat_keys and display_headers must be the same length")
    if merged:
        headers: list[str] = [
            "Model",
            *[_escape_md_cell(h) for h in display_headers],
        ]
        ncols = len(headers)
        tlines: list[str] = [
            "| " + " | ".join(headers) + " |",
            "| :--- |" + " ---: |" * (ncols - 1),
        ]
        col_max = _column_maxima(merged, cat_keys)
        sorted_rows = sorted(merged.items(), key=lambda it: _model_key_sort_key(it[0]))
        for mkey, rowd in sorted_rows:
            rest = [
                _format_stat_cell(
                    rowd.get(c, ("—", None)),
                    bold=_is_best_in_column(
                        rowd.get(c, ("—", None))[0], col_max.get(c)
                    ),
                )
                for c in cat_keys
            ]
            body: list[str] = [_escape_md_cell(mkey)] + rest
            tlines.append("| " + " | ".join(body) + " |")
        return "\n".join(tlines) + "\n"

    if not token and cat_keys:
        return _table_with_status_row(
            "_Set `GITHUB_TOKEN` and run `python scripts/refresh_deepagents_category_matrix.py --write` to load scores from CI._",
            cat_keys,
            display_headers,
        )
    if (
        token
        and n_fetched > 0
        and n_models_unfiltered > 0
    ):
        return _table_with_status_row(
            "_No models have scores in at least four of the six category columns._",
            cat_keys,
            display_headers,
        )
    if token and n_fetched > 0:
        return _table_with_status_row(
            "_No per-category `category_scores` in the `evals_summary` entries we read._",
            cat_keys,
            display_headers,
        )
    if token and n_fetched == 0:
        return _table_with_status_row(
            "_No `evals-summary` artifacts were loaded. Install `requests`, set `GITHUB_TOKEN` with **Actions: Read** on the repo, use `gh auth token` if the org uses SSO, and see the script’s stderr. Try a larger `--per-page` if needed._",
            cat_keys,
            display_headers,
        )
    return _table_with_status_row(
        "_No data._", cat_keys, display_headers
    )


def _write_snippet(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    out = body.rstrip() + "\n"
    path.write_text(out, encoding="utf-8")
    print(f"Wrote {path}", file=sys.stderr)


def build_fragment(per_page: int) -> str:
    tok = _token()
    n_fetched = 0
    merged: dict[str, dict[str, CellData]] = {}
    if tok:
        runs = _fetch_runs(int(per_page))
        merged, n_fetched = _merge_rows(runs, tok)
    n_models_unfiltered = len(merged)
    merged = {
        k: v
        for k, v in merged.items()
        if _filled_category_count(v, FIXED_CATEGORY_KEYS) >= MIN_FILLED_CATEGORIES
    }
    return _table_markdown(
        token=tok,
        merged=merged,
        cat_keys=FIXED_CATEGORY_KEYS,
        display_headers=FIXED_HEADER_LABELS,
        n_fetched=n_fetched,
        n_models_unfiltered=n_models_unfiltered,
    )


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Regenerate the eval-category matrix snippet (included from models.mdx)"
    )
    ap.add_argument(
        "--per-page", type=int, default=100, help="Number of latest completed runs to scan (newer first in API)."
    )
    ap.add_argument(
        "--write",
        action="store_true",
        help=f"Overwrite the snippet (default: {DEFAULT_SNIPPET_RELPATH}) with generated MDX",
    )
    ap.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_SNIPPET_PATH,
        help="Output snippet path (default: repo / src/snippets/deepagents-eval-category-matrix.mdx).",
    )
    args = ap.parse_args()
    frag = build_fragment(int(args.per_page))
    if not args.write:
        sys.stdout.write(frag)
        return 0
    out_path = args.file
    if not out_path.is_absolute():
        out_path = (_REPO_ROOT / out_path).resolve()
    _write_snippet(out_path, frag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
