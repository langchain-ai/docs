"""Verify that the served llms.txt index lists every page in the sitemap.

Mintlify generates llms.txt and splits it into nested indexes under ``/_llms/``
once it passes 100,000 characters. Nothing in this repo produces those files, so
the only way to know they are complete is to crawl what the site serves: start
at the root, follow every index link, and compare the pages found against the
sitemap.

Runs against the deployed site, with no build needed:

    python3 scripts/check_llms_urls.py
    python3 scripts/check_llms_urls.py --base-url https://www.mintlify.com/docs
"""

from __future__ import annotations

import argparse
import re
import sys
import time
import urllib.error
import urllib.request

MD_LINK = re.compile(r"\((https://[^\s)]+?\.md)\)")
SITEMAP_LOC = re.compile(r"<loc>\s*([^<\s]+)\s*</loc>")

DEFAULT_BASE_URL = "https://docs.langchain.com"
REQUEST_TIMEOUT = 30
RETRY_ATTEMPTS = 3
# Cloudflare-fronted sites return 403 to urllib's default user agent.
HEADERS = {"User-Agent": "langchain-docs-llms-check"}


def fetch_text(url: str) -> str:
    """Return the body of *url*, retrying dropped connections but not HTTP errors."""
    request = urllib.request.Request(url, headers=HEADERS)  # noqa: S310
    for attempt in range(RETRY_ATTEMPTS):
        try:
            with urllib.request.urlopen(  # noqa: S310
                request, timeout=REQUEST_TIMEOUT
            ) as response:
                return response.read().decode("utf-8")
        except urllib.error.HTTPError:
            raise
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            time.sleep(attempt + 1)
    msg = f"could not fetch {url}"
    raise SystemExit(msg)


def crawl_index(base_url: str) -> tuple[set[str], int]:
    """Return (page URLs, index files read) reachable from the root llms.txt."""
    pending = [f"{base_url}/llms.txt"]
    seen: set[str] = set()
    pages: set[str] = set()
    while pending:
        url = pending.pop()
        if url in seen:
            continue
        seen.add(url)
        for link in MD_LINK.findall(fetch_text(url)):
            if not link.startswith(f"{base_url}/"):
                continue
            if "/_llms/" in link:
                pending.append(link)
            else:
                pages.add(link.removesuffix(".md"))
    return pages, len(seen)


def main() -> int:
    """Crawl the served index and report sitemap pages it does not reach."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    args = parser.parse_args()

    pages, index_files = crawl_index(args.base_url)
    print(f"read {index_files} index files listing {len(pages):,} pages")

    sitemap = {
        u.rstrip("/")
        for u in SITEMAP_LOC.findall(fetch_text(f"{args.base_url}/sitemap.xml"))
        if u.startswith(f"{args.base_url}/")
    }
    missing = sorted(sitemap - pages)
    if not missing:
        print(f"✅ all {len(sitemap):,} sitemap pages are reachable from llms.txt")
        return 0

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


if __name__ == "__main__":
    sys.exit(main())
