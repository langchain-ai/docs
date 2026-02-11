#!/usr/bin/env python3
"""Check that pages removed from docs.json navigation have corresponding redirects.

When a page is removed from the navigation, existing links and bookmarks will break
unless a redirect is added. This script compares docs.json between the base branch
(upstream/main) and the PR branch, and fails if any removed pages don't have
a matching entry in the redirects array.
"""

import json
import sys
from pathlib import Path


def extract_pages_from_pages_array(items: list) -> set[str]:
    """Recursively extract page paths from a pages array."""
    result: set[str] = set()

    for item in items:
        if isinstance(item, str):
            result.add(item)
        elif isinstance(item, dict):
            if "pages" in item:
                result.update(extract_pages_from_pages_array(item["pages"]))
            # Some items have "group" and "pages" - "pages" key handles both

    return result


def extract_all_pages(docs: dict) -> set[str]:
    """Extract all page paths from docs.json navigation structure."""
    pages: set[str] = set()
    navigation = docs.get("navigation", {})
    products = navigation.get("products", [])

    for product in products:
        if isinstance(product, dict):
            # Direct pages
            if "pages" in product:
                pages.update(extract_pages_from_pages_array(product["pages"]))

            # Tabs (used by LangSmith, etc.)
            if "tabs" in product:
                for tab in product["tabs"]:
                    if isinstance(tab, dict):
                        if "pages" in tab:
                            pages.update(extract_pages_from_pages_array(tab["pages"]))
                        # Platform setup tab uses "groups" instead of "pages"
                        elif "groups" in tab:
                            for group in tab["groups"]:
                                if isinstance(group, dict) and "pages" in group:
                                    pages.update(
                                        extract_pages_from_pages_array(group["pages"])
                                    )

            # Dropdowns (used by Open source Python/TypeScript)
            if "dropdowns" in product:
                for dropdown in product["dropdowns"]:
                    if isinstance(dropdown, dict) and "tabs" in dropdown:
                        for tab in dropdown["tabs"]:
                            if isinstance(tab, dict) and "pages" in tab:
                                pages.update(
                                    extract_pages_from_pages_array(tab["pages"])
                                )

            # Groups (used by Platform setup)
            if "groups" in product:
                for group in product["groups"]:
                    if isinstance(group, dict) and "pages" in group:
                        pages.update(extract_pages_from_pages_array(group["pages"]))

    return pages


def normalize_page_for_comparison(path: str) -> str:
    """Normalize a page path for comparison (strip / and .mdx)."""
    return path.lstrip("/").removesuffix(".mdx")


def has_redirect_for_page(page_path: str, redirects: list[dict]) -> bool:
    """Check if any redirect has a source that matches the given page path.

    Redirects in docs.json can use various formats:
    - "langsmith/home" or "/langsmith/home"
    - "langsmith/home.mdx" or "/langsmith/home.mdx"
    """
    page_normalized = normalize_page_for_comparison(page_path)
    if page_normalized == "":
        page_normalized = "index"  # Root page

    for redirect in redirects:
        source = redirect.get("source", "")
        source_normalized = normalize_page_for_comparison(source)
        if source_normalized == "":
            source_normalized = "index"

        if source_normalized == page_normalized:
            return True

    return False


def main() -> int:
    if len(sys.argv) != 3:
        print(
            "Usage: check_removed_pages_redirects.py <base_docs.json> <head_docs.json>",
            file=sys.stderr,
        )
        return 2

    base_path = Path(sys.argv[1])
    head_path = Path(sys.argv[2])

    if not base_path.exists():
        print(f"Error: Base docs.json not found at {base_path}", file=sys.stderr)
        return 2

    if not head_path.exists():
        print(f"Error: Head docs.json not found at {head_path}", file=sys.stderr)
        return 2

    with open(base_path) as f:
        base_docs = json.load(f)
    with open(head_path) as f:
        head_docs = json.load(f)

    base_pages = extract_all_pages(base_docs)
    head_pages = extract_all_pages(head_docs)
    head_redirects = head_docs.get("redirects", [])

    removed_pages = base_pages - head_pages
    if not removed_pages:
        print("✅ No pages removed from docs.json. Check passed.")
        return 0

    # Filter redirects - only consider entries that redirect doc pages (have "source" and "destination")
    # Exclude openapi source entries which use "source" for a different purpose
    doc_redirects = [
        r
        for r in head_redirects
        if isinstance(r, dict) and "source" in r and "destination" in r
    ]

    pages_without_redirect: list[str] = []
    for page in sorted(removed_pages):
        if not has_redirect_for_page(page, doc_redirects):
            pages_without_redirect.append(page)

    if not pages_without_redirect:
        print(
            f"✅ All {len(removed_pages)} removed page(s) have corresponding redirects. Check passed."
        )
        return 0

    # Failure: output for GitHub Actions and PR comment
    print(
        "❌ The following pages were removed from docs.json without adding redirects:",
        file=sys.stderr,
    )
    for page in pages_without_redirect:
        print(f"  - {page}", file=sys.stderr)

    print(file=sys.stderr)
    print(
        "Please add a redirect for each removed page to the `redirects` array in docs.json.",
        file=sys.stderr,
    )
    print(
        'Example: {"source": "/path/to/removed-page", "destination": "/path/to/new-location"}',
        file=sys.stderr,
    )
    print(
        "Add these to the `redirects` array in src/docs.json.",
        file=sys.stderr,
    )

    return 1


if __name__ == "__main__":
    sys.exit(main())
