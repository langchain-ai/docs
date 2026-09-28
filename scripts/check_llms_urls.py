"""Verify that the served llms.txt index lists every page and its links resolve.

Mintlify generates llms.txt and splits it into nested indexes under ``/_llms/``
once it passes 100,000 characters. Nothing in this repo produces those files, so
the only way to know they are complete is to crawl what the site serves: start
at the root, follow every index link recursively, and compare the pages found
against the sitemap. A spot check that the listed pages resolve follows.

Runs against the deployed site, with no build needed:

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

MD_LINK = re.compile(r"\((https://[^\s)]+?\.md)\)")
SITEMAP_LOC = re.compile(r"<loc>\s*([^<\s]+)\s*</loc>")
# Nested index files, as opposed to documentation pages.
INDEX = re.compile(r"/_llms/")

DEFAULT_BASE_URL = "https://docs.langchain.com"
REQUEST_TIMEOUT = 30
MAX_WORKERS = 4
RETRY_ATTEMPTS = 3
RETRY_BACKOFF = 1.0
# Guards against an index that links to itself or a cycle between indexes.
MAX_INDEX_FILES = 500
# Cloudflare-fronted sites return 403 to urllib's default user agent.
HEADERS = {"User-Agent": "langchain-docs-llms-check"}


def fetch_text(url: str) -> str:
    """Return the body of *url*, raising once retries are exhausted."""
    for attempt in range(RETRY_ATTEMPTS):
        try:
            request = urllib.request.Request(url, headers=HEADERS)  # noqa: S310
            with urllib.request.urlopen(  # noqa: S310
                request, timeout=REQUEST_TIMEOUT
            ) as response:
                return response.read().decode("utf-8")
        except urllib.error.HTTPError:
            raise
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            time.sleep(RETRY_BACKOFF * (attempt + 1))
    msg = f"could not fetch {url}"
    raise SystemExit(msg)


def status_of(url: str) -> int:
    """Return the HTTP status for *url*, or 0 if it stayed unreachable.

    A connection that drops is retried, and HEAD is retried as GET: some CDNs
    answer HEAD unreliably under concurrency. Without this the job reports
    healthy pages as broken, and a check that cries wolf gets ignored.
    """
    for attempt in range(RETRY_ATTEMPTS):
        for method in ("HEAD", "GET"):
            request = urllib.request.Request(  # noqa: S310
                url, method=method, headers=HEADERS
            )
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


def normalize(url: str) -> str:
    """Reduce a page URL to the form the sitemap uses."""
    return url.removesuffix(".md").rstrip("/")


def crawl_index(base_url: str) -> tuple[set[str], int]:
    """Return (page URLs, index files read) reachable from the root llms.txt."""
    pending = [f"{base_url}/llms.txt"]
    seen: set[str] = set()
    pages: set[str] = set()
    while pending:
        url = pending.pop()
        if url in seen:
            continue
        if len(seen) >= MAX_INDEX_FILES:
            msg = f"stopped after {MAX_INDEX_FILES} index files; check for a cycle"
            raise SystemExit(msg)
        seen.add(url)
        for link in MD_LINK.findall(fetch_text(url)):
            if not link.startswith(f"{base_url}/"):
                continue
            if INDEX.search(link):
                pending.append(link)
            else:
                pages.add(link)
    return pages, len(seen)


def main() -> int:
    """Crawl the served index, compare it to the sitemap, then sample URLs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument(
        "--sample",
        type=int,
        default=120,
        help="How many listed page URLs to check resolve.",
    )
    parser.add_argument("--all", action="store_true", help="Check every URL.")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    pages, index_files = crawl_index(args.base_url)
    print(f"read {index_files} index files listing {len(pages):,} pages")

    sitemap = {
        normalize(u)
        for u in SITEMAP_LOC.findall(fetch_text(f"{args.base_url}/sitemap.xml"))
        if u.startswith(f"{args.base_url}/")
    }
    missing = sorted(sitemap - {normalize(u) for u in pages})
    if missing:
        print(
            f"\n❌ {len(missing):,} of {len(sitemap):,} sitemap pages are not "
            "reachable from llms.txt:\n"
        )
        for url in missing[:40]:
            print(f"  {url}")
        print(
            "\nMintlify generates these indexes, so a gap here is on their side. "
            "Check that no custom llms.txt has been added to the build, then "
            "report it to Mintlify."
        )
        return 1
    print(f"✅ all {len(sitemap):,} sitemap pages are reachable from llms.txt\n")

    # Sampling picks which URLs to spot-check; nothing here is security-relevant.
    rng = random.Random(args.seed)  # noqa: S311
    listed = sorted(pages)
    checking = listed if args.all else rng.sample(listed, min(args.sample, len(listed)))

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
            print(f"  {status or 'no response'}  {url}")
        return 1

    print(f"\n✅ all {len(checking):,} sampled URLs resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
