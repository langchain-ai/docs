"""Verify that URLs listed in the generated llms.txt indexes still resolve.

The build derives API reference URLs from the OpenAPI specs by reproducing
Mintlify's slug rules. Those rules are not a published contract, so a change on
their side would silently turn hundreds of index entries into 404s without
anything in this repo failing. Page URLs come from real files and are far
safer, but they can still rot when a page is renamed mid-build.

It also compares each served section index against the build, because
Mintlify can keep serving a stale copy of a nested llms.txt after a deploy.

Run against a build tree (``make build`` first):

    uv run python scripts/check_llms_urls.py
    uv run python scripts/check_llms_urls.py --all --base-url https://docs.langchain.com
"""

from __future__ import annotations

import argparse
import random
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

MD_LINK = re.compile(r"\((https://\S+?\.md)\)")
TXT_LINK = re.compile(r"\((https://\S+?llms[\w-]*\.txt)\)")
# Derived from an OpenAPI spec rather than from a file on disk.
DERIVED = re.compile(r"/(smith-api|agent-server-api)/")

DEFAULT_BASE_URL = "https://docs.langchain.com"
REQUEST_TIMEOUT = 30
MAX_WORKERS = 4
RETRY_ATTEMPTS = 3
RETRY_BACKOFF = 1.0


def collect_urls(build_dir: Path, base_url: str) -> tuple[list[str], list[str]]:
    """Return (derived API URLs, page URLs) listed across the llms.txt indexes."""
    root_path = build_dir / "llms.txt"
    if not root_path.exists():
        msg = f"{root_path} not found. Run `make build` first."
        raise SystemExit(msg)

    root = root_path.read_text(encoding="utf-8")
    urls = set(MD_LINK.findall(root))
    for link in TXT_LINK.findall(root):
        section = build_dir / link.removeprefix(f"{base_url}/")
        if section.exists():
            urls |= set(MD_LINK.findall(section.read_text(encoding="utf-8")))

    same_origin = sorted(u for u in urls if u.startswith(f"{base_url}/"))
    return (
        [u for u in same_origin if DERIVED.search(u)],
        [u for u in same_origin if not DERIVED.search(u)],
    )


def status_of(url: str) -> int:
    """Return the HTTP status for *url*, or 0 if it stayed unreachable.

    A connection that drops is retried, and HEAD is retried as GET: some CDNs
    answer HEAD unreliably under concurrency. Without this the job reports
    healthy pages as broken, and a check that cries wolf gets ignored.
    """
    for attempt in range(RETRY_ATTEMPTS):
        for method in ("HEAD", "GET"):
            request = urllib.request.Request(url, method=method)  # noqa: S310
            try:
                with urllib.request.urlopen(  # noqa: S310
                    request, timeout=REQUEST_TIMEOUT
                ) as response:
                    return int(response.status)
            except urllib.error.HTTPError as exc:
                # A real HTTP status is an answer, not a failure to reach.
                return int(exc.code)
            except (urllib.error.URLError, TimeoutError, ConnectionError):
                continue
        time.sleep(RETRY_BACKOFF * (attempt + 1))
    return 0


def fetch_text(url: str) -> tuple[str, str]:
    """Return (body, Last-Modified header) for *url*, or ("", "") if unreachable."""
    for attempt in range(RETRY_ATTEMPTS):
        try:
            with urllib.request.urlopen(url, timeout=REQUEST_TIMEOUT) as response:  # noqa: S310
                body = response.read().decode("utf-8")
                return body, response.headers.get("Last-Modified", "")
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            time.sleep(RETRY_BACKOFF * (attempt + 1))
    return "", ""


def stale_sections(
    section_urls: list[str], build_dir: Path, base_url: str
) -> list[tuple[str, int, int, str]]:
    """Return (url, missing, built, last_modified) for each outdated section.

    Mintlify serves the root llms.txt from its own route, which refreshes on
    every deploy, but serves nested llms.txt files as static files that it
    stopped refreshing: in September 2026 /langsmith/llms.txt still served an
    August copy with 271 of 465 pages. Every build-side check passes while
    that happens, so compare the served entries against the build.
    """
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        served = list(pool.map(fetch_text, section_urls))
    stale = []
    for url, (body, last_modified) in zip(section_urls, served, strict=True):
        local = build_dir / url.removeprefix(f"{base_url}/")
        built = set(MD_LINK.findall(local.read_text(encoding="utf-8")))
        missing = built - set(MD_LINK.findall(body))
        if missing:
            stale.append((url, len(missing), len(built), last_modified))
    return stale


def main() -> int:
    """Sample index URLs and report any that do not resolve."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-dir", type=Path, default=Path("build"))
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument(
        "--sample-derived",
        type=int,
        default=120,
        help="How many derived API URLs to check (these carry the real risk).",
    )
    parser.add_argument(
        "--sample-pages",
        type=int,
        default=40,
        help="How many ordinary page URLs to check.",
    )
    parser.add_argument("--all", action="store_true", help="Check every URL.")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    derived, pages = collect_urls(args.build_dir, args.base_url)
    print(f"index lists {len(derived):,} derived API URLs, {len(pages):,} page URLs")

    # Check the section indexes themselves first. Mintlify serves the exact
    # filename llms.txt at any path but 404s on anything else, so a rename or
    # a routing change makes whole sections invisible to coverage walkers
    # while every local check still passes.
    root = (args.build_dir / "llms.txt").read_text(encoding="utf-8")
    section_urls = sorted(
        u for u in set(TXT_LINK.findall(root)) if u.startswith(f"{args.base_url}/")
    )
    print(f"checking {len(section_urls)} section indexes are served\n")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        section_results = list(pool.map(status_of, section_urls))
    unserved = [
        (url, status)
        for url, status in zip(section_urls, section_results, strict=True)
        if status != 200
    ]
    if unserved:
        print(
            f"❌ {len(unserved)} of {len(section_urls)} section indexes are not served:\n"
        )
        for url, status in unserved[:20]:
            print(f"  {status or 'no response'}  {url}")
        print(
            "\nEvery section index must be named exactly llms.txt. Mintlify "
            "404s other .txt filenames, which hides those pages from coverage."
        )
        return 1
    print(f"✅ all {len(section_urls)} section indexes are served\n")

    stale = stale_sections(section_urls, args.build_dir, args.base_url)
    if stale:
        total = sum(missing for _, missing, _, _ in stale)
        print(
            f"❌ {len(stale)} served section indexes are missing {total:,} "
            "entries that the build lists:\n"
        )
        for url, missing, built, last_modified in stale:
            print(
                f"  {missing:>4} of {built:<4} missing  {url}"
                f"  (last-modified: {last_modified or 'unknown'})"
            )
        print(
            "\nMintlify is serving an old copy of these files. If the merge "
            "that added the pages deployed minutes ago, rerun the job. "
            "Otherwise report it to Mintlify with the last-modified dates "
            "above: the build output on the prod branch is correct."
        )
        return 1
    print(f"✅ all {len(section_urls)} served section indexes match the build\n")

    # Sampling picks which URLs to spot-check; nothing here is security-relevant.
    rng = random.Random(args.seed)  # noqa: S311
    if args.all:
        checking = derived + pages
    else:
        checking = rng.sample(derived, min(args.sample_derived, len(derived)))
        checking += rng.sample(pages, min(args.sample_pages, len(pages)))

    print(f"checking {len(checking):,} URLs against {args.base_url}\n")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        results = list(pool.map(status_of, checking))

    # A redirect still lands an agent on real content; only treat it as a note.
    reachable = (200, 301, 302, 307, 308)
    broken = [
        (url, status)
        for url, status in zip(checking, results, strict=True)
        if status not in reachable
    ]
    redirects = sum(1 for status in results if status in reachable[1:])

    if redirects:
        print(f"note: {redirects} URLs redirect (still reachable)")
    if broken:
        print(f"\n❌ {len(broken)} of {len(checking)} URLs do not resolve:\n")
        for url, status in sorted(broken)[:40]:
            label = status or "no response"
            print(f"  {label}  {url}")
        if DERIVED.search(broken[0][0]):
            print(
                "\nDerived API URLs are failing. Mintlify's slug rules for "
                "OpenAPI operations have most likely changed; compare against "
                "the live sitemap and update _tag_slug/_slugify in "
                "pipeline/core/builder.py."
            )
        return 1

    print(f"\n✅ all {len(checking):,} sampled URLs resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
