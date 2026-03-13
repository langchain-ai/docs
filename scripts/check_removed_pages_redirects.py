#!/usr/bin/env python3
"""Check docs.json: removed pages have redirects (when source is deleted), and all pages exist as source files.

1. Redirect check: When a page is removed from the navigation and its source
   file no longer exists, existing links and bookmarks will break unless a
   redirect is added. If the source file still exists, no redirect is required.
   Compares docs.json between the base branch and the PR branch.

2. Pages exist check: All page paths in docs.json must correspond to existing
   .mdx or .md files in src/. Handles special cases like oss/python/reference/*
   and oss/javascript/reference/* which map to oss/reference/*.
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
    - Wildcards: "/path/:path*" matches /path, /path/index, /path/anything, etc.
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

        # Support :path* wildcard (Vercel/Next.js style) - matches prefix and any suffix
        if ":path*" in source_normalized:
            prefix = source_normalized.replace(":path*", "").rstrip("/")
            if page_normalized == prefix or page_normalized.startswith(prefix + "/"):
                return True

    return False


def page_to_source_paths(page_path: str, src_dir: Path) -> list[Path]:
    """Return possible source file paths for a docs.json page path.

    Page paths like "langsmith/home" map to src/langsmith/home.mdx.

    OSS shared content: Many oss/python/* and oss/javascript/* paths map to
    shared files under oss/ (e.g. oss/deepagents/, oss/langchain/, oss/concepts/)
    because the build outputs them for both language dropdowns.
    """
    path = page_path.lstrip("/").removesuffix(".mdx").removesuffix(".md")
    if path == "":
        path = "index"

    candidates: list[Path] = []
    # Direct mapping: src/{path}.mdx or src/{path}.md
    candidates.append(src_dir / f"{path}.mdx")
    candidates.append(src_dir / f"{path}.md")

    # oss/python/X and oss/javascript/X may map to shared oss/X (e.g. oss/deepagents,
    # oss/langchain, oss/reference, oss/concepts - built for both language dropdowns)
    if path.startswith("oss/python/"):
        rest = path[len("oss/python/") :]
        candidates.append(src_dir / "oss" / f"{rest}.mdx")
        candidates.append(src_dir / "oss" / f"{rest}.md")
    elif path.startswith("oss/javascript/"):
        rest = path[len("oss/javascript/") :]
        candidates.append(src_dir / "oss" / f"{rest}.mdx")
        candidates.append(src_dir / "oss" / f"{rest}.md")

    return candidates


def check_pages_exist(docs: dict, src_dir: Path) -> list[str]:
    """Check that all page paths in docs.json have corresponding source files.

    Returns a list of page paths that do not have an existing .mdx or .md file.
    """
    pages = extract_all_pages(docs)
    missing: list[str] = []

    for page in sorted(pages):
        candidates = page_to_source_paths(page, src_dir)
        if not any(p.exists() for p in candidates):
            missing.append(page)

    return missing


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

    # src_dir: parent of docs.json (e.g. src/ when head_path is src/docs.json)
    src_dir = head_path.parent

    with open(base_path) as f:
        base_docs = json.load(f)
    with open(head_path) as f:
        head_docs = json.load(f)

    exit_code = 0

    # Check 1: All pages in docs.json must exist as source files
    missing_pages = check_pages_exist(head_docs, src_dir)
    if missing_pages:
        exit_code = 1
        print(
            "❌ The following pages in docs.json do not have corresponding source files:",
            file=sys.stderr,
        )
        for page in missing_pages:
            print(f"  - {page}", file=sys.stderr)
        print(
            "\nEach page path must resolve to an existing .mdx or .md file in src/.",
            file=sys.stderr,
        )

    # Check 2: Removed pages must have redirects (only if source file no longer exists)
    base_pages = extract_all_pages(base_docs)
    head_pages = extract_all_pages(head_docs)
    head_redirects = head_docs.get("redirects", [])

    removed_pages = base_pages - head_pages
    if removed_pages:
        doc_redirects = [
            r
            for r in head_redirects
            if isinstance(r, dict) and "source" in r and "destination" in r
        ]

        pages_without_redirect: list[str] = []
        for page in sorted(removed_pages):
            # Skip if source file still exists - page is reachable, no redirect needed
            candidates = page_to_source_paths(page, src_dir)
            if any(p.exists() for p in candidates):
                continue
            if not has_redirect_for_page(page, doc_redirects):
                pages_without_redirect.append(page)

        if pages_without_redirect:
            exit_code = 1
            if missing_pages:
                print(file=sys.stderr)
            print(
                "❌ The following pages were removed from docs.json without adding redirects:",
                file=sys.stderr,
            )
            for page in pages_without_redirect:
                print(f"  - {page}", file=sys.stderr)
            print(
                "\nPlease add a redirect for each removed page to the `redirects` array in docs.json.",
                file=sys.stderr,
            )
            print(
                'Example: {"source": "/path/to/removed-page", "destination": "/path/to/new-location"}',
                file=sys.stderr,
            )
        elif not missing_pages:
            print(
                "✅ All removed page(s) either have redirects or source files still exist. All pages exist. Check passed."
            )
    elif not missing_pages:
        print("✅ No pages removed from docs.json. All pages exist. Check passed.")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
