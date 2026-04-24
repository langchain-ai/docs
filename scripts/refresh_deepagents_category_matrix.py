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
  python scripts/refresh_deepagents_category_matrix.py --write

With no `GITHUB_TOKEN`, the script only writes a short <Note> (no **correctness** numbers).

Column labels follow [categories.json in deepagents](
https://github.com/langchain-ai/deepagents/blob/main/libs/evals/deepagents_evals/categories.json
).
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
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
from gh_artifact_download import download_artifact_bytes as _download_artifact_bytes

OWNER = "langchain-ai"
REPO = "deepagents"
WORKFLOW_ID = 240654164
CATEGORIES_URL = (
    f"https://raw.githubusercontent.com/{OWNER}/{REPO}/main/"
    "libs/evals/deepagents_evals/categories.json"
)
DEFAULT_MDX = "src/oss/deepagents/models.mdx"
BEGIN = "<!-- eval-category-matrix:begin (generated) -->"
END = "<!-- eval-category-matrix:end -->"


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


def _load_category_meta() -> tuple[list[str], dict[str, str], list[str]]:
    with urllib.request.urlopen(CATEGORIES_URL) as r:
        raw = json.loads(r.read().decode("utf-8"))
    order = [str(c) for c in raw.get("categories", [])]
    labels: dict[str, str] = {
        str(k): str(v) for k, v in (raw.get("labels") or {}).items()
    }
    radar = [str(c) for c in raw.get("radar_categories", [])]
    if not radar:
        radar = [c for c in order if c != "unit_test"]
    return order, labels, radar


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


def _escape_md_cell(s: str) -> str:
    return s.replace("|", r"\|")


def _format_stat_cell(cell: CellData) -> str:
    """Format `NN%` and optionally link to the source workflow run."""
    pct, run_url = cell
    if not run_url or not pct or pct == "—":
        return _escape_md_cell(pct) if pct else "—"
    # Avoid breaking the markdown link label: escape ] if present
    label = pct.replace("]", r"\]")
    return f"[{label}]({run_url})"


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
        except SystemExit:  # missing `requests` in gh_artifact_download
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


def _column_order(merged: dict[str, dict[str, CellData]], default_order: list[str]) -> list[str]:
    have: set[str] = set()
    for _m, row in merged.items():
        have.update(row.keys())
    # stable: categories.json order, then any extra keys
    out: list[str] = [c for c in default_order if c in have]
    extra = sorted(have - set(out))
    return out + extra


def _markdown(
    token: str | None,
    merged: dict[str, dict[str, CellData]],
    cat_order: list[str],
    labels: dict[str, str],
    n_fetched: int,
) -> str:
    intro = (
        f"**Per-category correctness** from the `category_scores` field in "
        f"[Evals - GHA](https://github.com/{OWNER}/{REPO}/actions/workflows/evals.yml) "
        "`evals_summary.json` (inside the `evals-summary` artifact). For each `provider:model` and "
        "[eval category](https://github.com/langchain-ai/deepagents/blob/main/libs/evals/EVAL_CATALOG.md), "
        "this table takes the first value seen while walking successful runs from **newest to oldest** "
        "(`GITHUB_TOKEN` and `--per-page` are tunable). Each value links to the **workflow run** whose "
        "`evals_summary` that score came from. **Compare only the same** "
        f"[eval tier](https://github.com/{OWNER}/{REPO}/blob/main/.github/workflows/evals.yml#L135-L144) and "
        "[run inputs](https://github.com/langchain-ai/deepagents/blob/main/.github/workflows/evals.yml) "
        f"as you would when diffing one [Evals - GHA](https://github.com/{OWNER}/{REPO}/actions/workflows/evals.yml) run against another. "
    )

    lines: list[str] = [intro, ""]
    if not token:
        lines.append(
            "<Note>Generate this table: set `GITHUB_TOKEN` (artifact read for the Deep Agents repository) and run "
            "`python scripts/refresh_deepagents_category_matrix.py --write` at the documentation root. "
            "Column titles follow the `labels` map in [categories.json](https://github.com/langchain-ai/deepagents/blob/main/libs/evals/deepagents_evals/categories.json) in the Deep Agents repo. "
            "</Note>"
        )
        lines.append("")
    elif n_fetched == 0 and merged == {}:
        lines.append(
            "<Note>Could not load any `evals-summary` zips. Run `python3 -m pip install requests`. "
            "A **403** when **listing** workflow artifacts for "
            f"`{OWNER}/{REPO}` is usually **SAML / SSO** for the **langchain-ai** org: in **Settings** → **Developer settings** → **Personal access tokens**, open this token, use **Configure SSO**, and **Authorize** for that org. Or run `gh auth login` and use the token from `gh auth token` as `GITHUB_TOKEN`. The token also needs **Actions: Read** on the repository. See [SSO and personal access tokens](https://docs.github.com/en/enterprise-cloud@latest/authentication/authenticating-with-saml-single-sign-on/authorizing-a-personal-access-token-for-use-with-saml-single-sign-on) and [Managing personal access tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens). "
            "For details, look at the script’s stderr when you run it. Try a larger `--per-page` if the scan missed runs. "
            "</Note>"
        )
        lines.append("")

    if merged:
        headers: list[str] = ["Model"] + [labels.get(c, c) for c in cat_order]
        tlines: list[str] = [
            "| " + " | ".join(_escape_md_cell(x) for x in headers) + " |",
            "| :--- |" + " ---: |" * (len(headers) - 1),
        ]
        for mkey in sorted(merged, key=str.lower):
            rowd = merged[mkey]
            body: list[str] = [_escape_md_cell(mkey)]
            for c in cat_order:
                body.append(_format_stat_cell(rowd.get(c, ("—", None))))
            tlines.append("| " + " | ".join(body) + " |")
        lines.extend(tlines)
        lines.append("")
        if token and n_fetched:
            lines.append(
                "<Note>Regenerate after new CI: `python scripts/refresh_deepagents_category_matrix.py --write`</Note>"
            )
    elif token and n_fetched > 0 and not merged:
        lines.append(
            "_No per-category `category_scores` in the `evals_summary` entries we read._\n"
        )
    elif not token and not merged and cat_order:
        headers2: list[str] = ["Model"] + [labels.get(c, c) for c in cat_order]
        pad = " | ".join(["—"] * len(cat_order))
        tlines2: list[str] = [
            "| " + " | ".join(_escape_md_cell(x) for x in headers2) + " |",
            "| :--- |" + " ---: |" * (len(headers2) - 1),
            "| _Run the script in the Note to fill this table_ | " + pad + " |",
        ]
        lines.extend(tlines2)
        lines.append("")
    return "\n".join(x.rstrip() for x in lines) + "\n"


def _replace_mdx(mdx_path: str, new_inner: str) -> None:
    p = Path(mdx_path)
    text = p.read_text(encoding="utf-8")
    if BEGIN not in text or END not in text:
        sys.exit(
            f"Add these markers in {mdx_path} to enable --write:\n{BEGIN}\n{END}\n"
        )
    a = text.find(BEGIN)
    b = text.find(END)
    if a == -1 or b == -1 or b < a:
        sys.exit("Invalid marker order.")
    b_end = b + len(END)
    block = f"{BEGIN}\n{new_inner.rstrip()}\n{END}"
    p.write_text(text[:a] + block + text[b_end:], encoding="utf-8")
    print(f"Wrote {mdx_path}", file=sys.stderr)


def build_fragment(per_page: int) -> str:
    tok = _token()
    order, labels, radar = _load_category_meta()
    n_fetched = 0
    merged: dict[str, dict[str, CellData]] = {}
    if tok:
        runs = _fetch_runs(int(per_page))
        merged, n_fetched = _merge_rows(runs, tok)
    col_order = _column_order(merged, order) if merged else radar
    return _markdown(
        token=tok, merged=merged, cat_order=col_order, labels=labels, n_fetched=n_fetched
    )


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Regenerate the model × eval-category table in models.mdx"
    )
    ap.add_argument("--per-page", type=int, default=100, help="Number of latest completed runs to scan (newer first in API).")
    ap.add_argument(
        "--write", action="store_true", help=f"Patch {DEFAULT_MDX} between {BEGIN[:20]}... markers"
    )
    ap.add_argument("--file", default=DEFAULT_MDX, help="Path to the MDX file to patch")
    args = ap.parse_args()
    frag = build_fragment(int(args.per_page))
    if not args.write:
        sys.stdout.write(frag)
        return 0
    _replace_mdx(args.file, frag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
