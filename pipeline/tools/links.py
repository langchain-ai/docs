"""Move documentation files while automatically updating references.

This module provides functionality to move files within a documentation tree and
simultaneously update all relative links that point to the moved file. It scans
all Markdown files in the documentation root and rewrites any links that reference
the old file location to point to the new location, ensuring no links break.
"""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
from pathlib import Path

import nbformat

ENCODING: str = "utf-8"

# Pattern to match Markdown links in the form of `[label](url)`
# or `[label](url#anchor)`.
_LINK_PATTERN: re.Pattern[str] = re.compile(r"(\[[^\]]+\])\(([^)\s#]+)(#[^)\s]*)?\)")
_LinkChange = tuple[str, str]  # (old_url, new_url)

# Pattern to match site-absolute links in Markdown (`[label](/route)`) and in
# component attributes (`href="/route"`). Only the route is captured; anchors,
# query strings, and link titles stay in place.
_ROUTE_LINK_PATTERN: re.Pattern[str] = re.compile(r'(\]\(|\bhref=")(/[^\s)"#?]*)')

# Pattern to match a string value in `docs.json`, except a redirect `source`,
# which names a URL that no longer exists rather than a page.
_DOCS_JSON_ROUTE_PATTERN: re.Pattern[str] = re.compile(
    r'(?<!"source": )"(/?)([^"#\s]+)(#[^"]*)?"'
)

# Language directory names in `src/oss/` and in built URLs.
_LANGUAGES: tuple[str, ...] = ("python", "javascript")

# OSS products built once, without a python/javascript split. Mirrors the
# exclusions in `DocumentationBuilder._rewrite_oss_links`.
_UNVERSIONED_OSS: tuple[str, ...] = ("oss/deepagents/code", "oss/openwiki")

_DOC_SUFFIXES: tuple[str, ...] = (".md", ".mdx", ".ipynb")


logger = logging.getLogger(__name__)


def _find_git_root(start: Path) -> Path:
    """Return the repository root - the closest ancestor containing `.git`.

    `.git` is a directory in a regular checkout and a file in a worktree or
    submodule, so either form marks the root.

    Args:
        start: A path *inside* the repository.

    Returns:
        The absolute path to the repo's root directory.

    Raises:
        RuntimeError: If no `.git` entry is found while traversing up the
            directory tree.
    """
    for candidate in (start, *start.parents):
        if (candidate / ".git").exists():
            return candidate
    msg = f"Could not locate Git repository root from {start}."
    raise RuntimeError(msg)


def _rel_to_docs_root(path: Path, docs_root: Path) -> Path:
    """Return *path* relative to *docs_root* resolving any symlinks.

    Args:
        path: The file path to normalise.
        docs_root: The root of the documentation tree (`<repo>/src`).

    Returns:
        A :class:`pathlib.Path` representing *path* relative to *docs_root*.
    """
    return path.resolve().relative_to(docs_root.resolve())


def _route_forms(rel_path: Path) -> dict[str, str]:
    """Return every site-absolute URL form that reaches a source file.

    Internal links are written as routes (`/langsmith/page`), not file paths.
    The build serves one source file at several routes, so a link to it can
    take several forms:

    - Shared OSS pages (`oss/langchain/x`) are reached by the unversioned
      `/oss/langchain/x`, which the build expands per language, and by the
      explicit `/oss/python/langchain/x` and `/oss/javascript/langchain/x`.
    - Language-specific OSS pages (`oss/python/x`) are reached by
      `/oss/python/x` and, in the Python build, by the unversioned `/oss/x`.
    - Managed Deep Agents pages are reached by `/langsmith/managed-deep-agents*`
      and by their `/langsmith/{python,javascript}/...` routes.
    - Everything else, including Deep Agents Code and OpenWiki, is reached by
      its path alone.

    Args:
        rel_path: The source file, relative to the docs root.

    Returns:
        A mapping of form name (`"unversioned"`, `"python"`, or `"javascript"`)
        to route. A route keeps a trailing `/index`; see `_normalize_route`.
    """
    route = rel_path.with_suffix("").as_posix()
    if route.startswith("oss/") and not any(
        route == prefix or route.startswith(f"{prefix}/") for prefix in _UNVERSIONED_OSS
    ):
        rest = route.removeprefix("oss/")
        language, _, sub = rest.partition("/")
        if language in _LANGUAGES:
            return {language: f"/{route}", "unversioned": f"/oss/{sub}"}
        return {
            "unversioned": f"/{route}",
            **{lang: f"/oss/{lang}/{rest}" for lang in _LANGUAGES},
        }
    if rel_path.parent.as_posix() == "langsmith" and rel_path.name.startswith(
        "managed-deep-agents"
    ):
        sub = route.removeprefix("langsmith/")
        return {
            "unversioned": f"/{route}",
            **{lang: f"/langsmith/{lang}/{sub}" for lang in _LANGUAGES},
        }
    return {"unversioned": f"/{route}"}


def _normalize_route(route: str) -> str:
    """Return *route* without a trailing slash or `/index`, as the site serves it."""
    route = route.rstrip("/")
    route = route.removesuffix("/index")
    return route or "/"


def _has_doc_file(docs_root: Path, rel_stem: str) -> bool:
    """Return whether a documentation source file exists at *rel_stem*."""
    return any(
        (docs_root / f"{rel_stem}{suffix}").is_file() for suffix in _DOC_SUFFIXES
    )


def _build_route_map(old_rel: Path, new_rel: Path, docs_root: Path) -> dict[str, str]:
    """Map each route that reaches *old_rel* to the matching route for *new_rel*.

    A link keeps its form: an unversioned link stays unversioned and a
    `/oss/python/...` link stays explicit. Forms that cannot be rewritten
    safely are logged and left out of the map, so links using them are left
    unchanged:

    - An unversioned link to a language-specific page also reaches its
      counterpart in the other language, or a shared page, when one exists.
    - A form with no equivalent at the destination, such as a
      `/oss/javascript/...` link to a page moved into `oss/python/`.

    Args:
        old_rel: The file being moved, relative to the docs root.
        new_rel: The destination, relative to the docs root.
        docs_root: The root of the documentation tree.

    Returns:
        A mapping of old route to new route, both as written in `docs.json`
        (keeping any trailing `/index`).
    """
    old_forms = _route_forms(old_rel)
    new_forms = _route_forms(new_rel)
    new_is_versioned = any(lang in new_forms for lang in _LANGUAGES)

    old_language = next(
        (lang for lang in _LANGUAGES if old_rel.parts[:2] == ("oss", lang)), None
    )
    route_map: dict[str, str] = {}
    for form, old_route in old_forms.items():
        if form == "unversioned" and old_language is not None:
            sub = old_route.removeprefix("/oss/")
            others = [
                f"oss/{lang}/{sub}" for lang in _LANGUAGES if lang != old_language
            ]
            shadowing = [
                s for s in [*others, f"oss/{sub}"] if _has_doc_file(docs_root, s)
            ]
            if shadowing:
                logger.warning(
                    "Left %s links unchanged: they also reach %s.",
                    old_route,
                    ", ".join(shadowing),
                )
                continue

        new_route = new_forms.get(form)
        if new_route is None and not new_is_versioned:
            new_route = new_forms["unversioned"]
        if new_route is None:
            logger.warning(
                "Left %s links unchanged: %s has no %s route.", old_route, new_rel, form
            )
            continue
        if new_route != old_route:
            route_map[old_route] = new_route
    return route_map


def _rewrite_route_links(
    text: str, route_map: dict[str, str]
) -> tuple[str, list[_LinkChange]]:
    """Rewrite site-absolute links in *text* according to *route_map*.

    Args:
        text: Markdown or MDX source.
        route_map: Old route to new route, from `_build_route_map`.

    Returns:
        The rewritten text and the `(old_url, new_url)` changes made.
    """
    normalized = {_normalize_route(old): new for old, new in route_map.items()}
    changes: list[_LinkChange] = []

    def _replacer(match: re.Match[str]) -> str:
        prefix, url = match.groups()
        new_route = normalized.get(_normalize_route(url))
        if new_route is None:
            return match.group(0)
        new_url = _normalize_route(new_route)
        if url.endswith("/") and not new_url.endswith("/"):
            new_url += "/"
        changes.append((url, new_url))
        return f"{prefix}{new_url}"

    return _ROUTE_LINK_PATTERN.sub(_replacer, text), changes


def _rewrite_route_links_in_file(
    doc_file: Path, route_map: dict[str, str], docs_root: Path, *, dry_run: bool
) -> list[_LinkChange]:
    """Rewrite site-absolute links in one Markdown, MDX, or notebook file.

    Args:
        doc_file: The file to scan. Notebooks are scanned in markdown cells only.
        route_map: Old route to new route, from `_build_route_map`.
        docs_root: The root of the documentation tree.
        dry_run: Whether the operation is a preview (no disk writes).

    Returns:
        The `(old_url, new_url)` changes made.
    """
    changes: list[_LinkChange] = []
    if doc_file.suffix.lower() == ".ipynb":
        notebook = nbformat.read(doc_file, as_version=nbformat.NO_CONVERT)
        for cell in notebook.cells:
            if cell.cell_type != "markdown" or "source" not in cell:
                continue
            source = cell.source
            text = "".join(source) if isinstance(source, list) else source
            new_text, cell_changes = _rewrite_route_links(text, route_map)
            if cell_changes:
                cell.source = new_text
                changes.extend(cell_changes)
        if changes and not dry_run:
            nbformat.write(notebook, doc_file)
    else:
        text = doc_file.read_text(encoding=ENCODING)
        new_text, changes = _rewrite_route_links(text, route_map)
        if changes and not dry_run:
            doc_file.write_text(new_text, encoding=ENCODING)

    if dry_run:
        for old_url, new_url in changes:
            logger.info(
                "Would update link in %s: %s -> %s",
                doc_file.relative_to(docs_root),
                old_url,
                new_url,
            )
    return changes


def _rewrite_docs_json(
    docs_root: Path, route_map: dict[str, str], *, dry_run: bool
) -> list[_LinkChange]:
    """Rewrite navigation entries and redirect destinations in `docs.json`.

    Navigation entries name pages without a leading slash
    (`"langsmith/page"`); redirect destinations use one. Redirect sources are
    left alone, because they name URLs that should keep redirecting.

    Args:
        docs_root: The root of the documentation tree.
        route_map: Old route to new route, from `_build_route_map`.
        dry_run: Whether the operation is a preview (no disk writes).

    Returns:
        The `(old_value, new_value)` changes made.
    """
    docs_json = docs_root / "docs.json"
    if not route_map or not docs_json.is_file():
        return []

    src = docs_json.read_text(encoding=ENCODING)
    normalized = {_normalize_route(old): new for old, new in route_map.items()}
    changes: list[_LinkChange] = []

    def _replacer(match: re.Match[str]) -> str:
        slash, value, anchor = match.groups()
        new_route = route_map.get(f"/{value}")
        if new_route is None:
            # A redirect destination can name an index page by its folder.
            folder_route = normalized.get(_normalize_route(f"/{value}"))
            if folder_route is None:
                return match.group(0)
            new_route = _normalize_route(folder_route)
        new_value = slash + new_route.removeprefix("/")
        changes.append((slash + value, new_value))
        if dry_run:
            logger.info("Would update docs.json: %s -> %s", slash + value, new_value)
        return f'"{new_value}{anchor or ""}"'

    new_src = _DOCS_JSON_ROUTE_PATTERN.sub(_replacer, src)
    if changes and not dry_run:
        docs_json.write_text(new_src, encoding=ENCODING)
    return changes


def _update_internal_links_in_moved_file(
    file_path: Path,
    old_parent: Path,
    new_parent: Path,
    docs_root: Path,
    *,
    dry_run: bool,
) -> list[_LinkChange]:
    """Update internal relative links within a file that's being moved.

    Args:
        file_path: The file being moved (at its new location).
        old_parent: The directory the file was moved from.
        new_parent: The directory the file was moved to.
        docs_root: The root of the documentation tree.
        dry_run: Whether the operation is a preview (no disk writes).

    Returns:
        A list of `(old_url, new_url)` tuples representing link changes.
    """
    if not file_path.exists():
        return []

    src: str = file_path.read_text(encoding=ENCODING)
    modified: bool = False
    changes: list[_LinkChange] = []

    def _replacer(match: re.Match[str]) -> str:
        nonlocal modified
        label, url, anchor = match.groups()

        # Handle case where anchor is None
        anchor = anchor or ""
        full_url = url + anchor

        # Skip external links, mailto, absolute paths, or in-page anchors
        if url.startswith(("http://", "https://", "mailto:", "/")) or (
            not url and anchor
        ):
            return match.group(0)

        # This is a relative link - we need to update it
        try:
            # Calculate what the link was pointing to from the old location
            old_target = (old_parent / url).resolve()

            # Check if the target exists and is within docs_root
            if old_target.exists() and old_target.is_relative_to(docs_root.resolve()):
                # Calculate new relative path from new location
                new_rel = os.path.relpath(old_target, new_parent)
                new_rel_posix = Path(new_rel).as_posix()
                new_full_url = new_rel_posix + anchor

                # Only update if the path actually changed
                if new_full_url != full_url:
                    changes.append((full_url, new_full_url))

                    if dry_run:
                        logger.info(
                            "Would update internal link in moved file %s: %s -> %s",
                            file_path.relative_to(docs_root),
                            full_url,
                            new_full_url,
                        )
                    modified = True
                    return f"{label}({new_full_url})"
        except (ValueError, OSError):
            # Path resolution failed or target outside docs_root - leave unchanged
            pass
        return match.group(0)

    new_src: str = _LINK_PATTERN.sub(_replacer, src)
    if modified and not dry_run:
        file_path.write_text(new_src, encoding=ENCODING)

    return changes


def _rewrite_links(
    md_file: Path,
    old_abs: Path,
    new_abs: Path,
    docs_root: Path,
    *,
    dry_run: bool,
) -> list[_LinkChange]:
    """Rewrite links in *md_file* that point to *old_abs*.

    Args:
        md_file: The Markdown file whose links are scanned.
        old_abs: Absolute path of the file being moved.
        new_abs: Absolute path where the file will be moved to.
        docs_root: The root of the documentation tree (`<repo>/src`).
        dry_run: Whether the operation is a preview (no disk writes).

    Returns:
        A list of `(old_url, new_url)` tuples representing link changes.
    """
    src: str = md_file.read_text(encoding=ENCODING)
    modified: bool = False
    changes: list[_LinkChange] = []

    def _replacer(match: re.Match[str]) -> str:
        nonlocal modified
        label, url, anchor = match.groups()

        # Handle case where anchor is None
        anchor = anchor or ""
        full_url = url + anchor

        # Skip external links, mailto, or in-page anchors.
        if url.startswith(("http://", "https://", "mailto:")) or (not url and anchor):
            return match.group(0)

        resolved = (md_file.parent / url).resolve()
        try:
            if _rel_to_docs_root(resolved, docs_root) == _rel_to_docs_root(
                old_abs, docs_root
            ):
                new_rel = os.path.relpath(new_abs, md_file.parent)
                new_rel_posix = Path(new_rel).as_posix()
                new_full_url = new_rel_posix + anchor

                changes.append((full_url, new_full_url))

                if dry_run:
                    logger.info(
                        "Would update link in %s: %s -> %s",
                        md_file.relative_to(docs_root),
                        full_url,
                        new_full_url,
                    )
                modified = True
                return f"{label}({new_full_url})"
        except ValueError:
            # Path is outside docs_root - ignore.
            pass
        return match.group(0)

    new_src: str = _LINK_PATTERN.sub(_replacer, src)
    if modified and not dry_run:
        md_file.write_text(new_src, encoding=ENCODING)

    return changes


def _update_internal_links_in_moved_notebook(
    file_path: Path,
    old_parent: Path,
    new_parent: Path,
    docs_root: Path,
    *,
    dry_run: bool,
) -> list[_LinkChange]:
    """Update internal relative links within a notebook that's being moved.

    Args:
        file_path: The notebook being moved (at its new location).
        old_parent: The directory the notebook was moved from.
        new_parent: The directory the notebook was moved to.
        docs_root: The root of the documentation tree.
        dry_run: Whether the operation is a preview (no disk writes).

    Returns:
        A list of `(old_url, new_url)` tuples representing link changes.
    """
    if not file_path.exists():
        return []

    notebook = nbformat.read(file_path, as_version=nbformat.NO_CONVERT)
    changes: list[_LinkChange] = []
    modified = False

    def _replacer(match: re.Match[str]) -> str:
        nonlocal modified
        label, url, anchor = match.groups()

        # Handle case where anchor is None
        anchor = anchor or ""
        full_url = url + anchor

        # Skip external links, mailto, absolute paths, or in-page anchors
        if url.startswith(("http://", "https://", "mailto:", "/")) or (
            not url and anchor
        ):
            return match.group(0)

        # This is a relative link - we need to update it
        try:
            # Calculate what the link was pointing to from the old location
            old_target = (old_parent / url).resolve()

            # Check if the target exists and is within docs_root
            if old_target.exists() and old_target.is_relative_to(docs_root.resolve()):
                # Calculate new relative path from new location
                new_rel = os.path.relpath(old_target, new_parent)
                new_rel_posix = Path(new_rel).as_posix()
                new_full_url = new_rel_posix + anchor

                # Only update if the path actually changed
                if new_full_url != full_url:
                    changes.append((full_url, new_full_url))

                    if dry_run:
                        logger.info(
                            "Would update internal link in moved notebook %s: %s -> %s",
                            file_path.relative_to(docs_root),
                            full_url,
                            new_full_url,
                        )
                    modified = True
                    return f"{label}({new_full_url})"
        except (ValueError, OSError):
            # Path resolution failed or target outside docs_root - leave unchanged
            pass
        return match.group(0)

    # Process all cells in the notebook
    for cell in notebook.cells:
        if cell.cell_type == "markdown" and "source" in cell:
            # Handle both string and list sources
            if isinstance(cell.source, list):
                source_text = "".join(cell.source)
            else:
                source_text = cell.source

            new_source = _LINK_PATTERN.sub(_replacer, source_text)

            if new_source != source_text:
                cell.source = new_source

    if modified and not dry_run:
        nbformat.write(notebook, file_path)

    return changes


def _rewrite_links_in_notebook(
    notebook_file: Path,
    old_abs: Path,
    new_abs: Path,
    docs_root: Path,
    *,
    dry_run: bool,
) -> list[_LinkChange]:
    """Rewrite links in markdown cells of a Jupyter notebook.

    Args:
        notebook_file: The Jupyter notebook file to process.
        old_abs: Absolute path of the file being moved.
        new_abs: Absolute path where the file will be moved to.
        docs_root: The root of the documentation tree.
        dry_run: Whether the operation is a preview (no disk writes).
    """
    notebook = nbformat.read(notebook_file, as_version=nbformat.NO_CONVERT)
    changes: list[_LinkChange] = []

    modified = False

    def _replacer(match: re.Match[str]) -> str:
        nonlocal modified
        label, url, anchor = match.groups()

        # Handle case where anchor is None
        anchor = anchor or ""
        full_url = url + anchor

        # Skip external links, mailto, or in-page anchors.
        if url.startswith(("http://", "https://", "mailto:")) or (not url and anchor):
            return match.group(0)

        resolved = (notebook_file.parent / url).resolve()
        try:
            if _rel_to_docs_root(resolved, docs_root) == _rel_to_docs_root(
                old_abs, docs_root
            ):
                new_rel = os.path.relpath(new_abs, notebook_file.parent)
                new_rel_posix = Path(new_rel).as_posix()
                new_full_url = new_rel_posix + anchor

                changes.append((full_url, new_full_url))

                if dry_run:
                    logger.info(
                        "Would update link in %s: %s -> %s",
                        notebook_file.relative_to(docs_root),
                        full_url,
                        new_full_url,
                    )
                modified = True
                return f"{label}({new_full_url})"
        except ValueError:
            # Path is outside docs_root - ignore.
            pass
        return match.group(0)

    # Process all cells in the notebook
    for cell in notebook.cells:
        if cell.cell_type == "markdown" and "source" in cell:
            # Handle both string and list sources
            if isinstance(cell.source, list):
                source_text = "".join(cell.source)
            else:
                source_text = cell.source

            new_source = _LINK_PATTERN.sub(_replacer, source_text)

            if new_source != source_text:
                cell.source = new_source

    if modified and not dry_run:
        nbformat.write(notebook, notebook_file)

    return changes


def _scan_and_rewrite(
    docs_root: Path,
    old_abs: Path,
    new_abs: Path,
    *,
    dry_run: bool,
) -> list[_LinkChange]:
    """Recursively scan *docs_root* and rewrite links in every documentation file.

    Args:
        docs_root: The root of the documentation tree.
        old_abs: Absolute path of the file being moved.
        new_abs: Absolute path where the file will be moved to.
        dry_run: Whether the operation is a preview (no disk writes).

    Returns:
        A list of `(old_url, new_url)` tuples representing every link change
        performed (or that *would* be performed in dry-run mode).
    """
    changes: list[_LinkChange] = []
    for pattern in ["*.md", "*.mdx"]:
        for md_file in docs_root.rglob(pattern):
            file_changes = _rewrite_links(
                md_file, old_abs, new_abs, docs_root, dry_run=dry_run
            )
            changes.extend(file_changes)

    # Process Jupyter notebooks
    for notebook_file in docs_root.rglob("*.ipynb"):
        changes.extend(
            _rewrite_links_in_notebook(
                notebook_file, old_abs, new_abs, docs_root, dry_run=dry_run
            )
        )

    # Rewrite site-absolute links (`/langsmith/page`), the form internal links
    # actually use. The passes above handle relative file links only.
    try:
        route_map = _build_route_map(
            _rel_to_docs_root(old_abs, docs_root),
            _rel_to_docs_root(new_abs, docs_root),
            docs_root,
        )
    except ValueError:
        logger.warning("Skipped site-absolute links: a path is outside %s.", docs_root)
        route_map = {}
    if route_map:
        for doc_file in sorted(docs_root.rglob("*")):
            if doc_file.suffix.lower() in _DOC_SUFFIXES and doc_file.is_file():
                changes.extend(
                    _rewrite_route_links_in_file(
                        doc_file, route_map, docs_root, dry_run=dry_run
                    )
                )
        changes.extend(_rewrite_docs_json(docs_root, route_map, dry_run=dry_run))

    return changes


def _write_changes_log(old_path: Path, new_path: Path, root: Path) -> None:
    """Append file move to `link_changes.jsonl` as a JSON array.

    Args:
        old_path: The original file path.
        new_path: The new file path.
        root: The directory where the log file will be written.
    """
    log_path = root / "link_changes.jsonl"
    with log_path.open("a", encoding=ENCODING) as fp:
        fp.write(json.dumps([str(old_path), str(new_path)]) + "\n")


def move_file_with_link_updates(
    old_path: Path,
    new_path: Path,
    *,
    dry_run: bool = False,
    git_root: Path | None = None,
    docs_root: Path | None = None,
) -> list[_LinkChange]:
    """Move a file and update links in the documentation tree.

    Args:
        old_path: Path to the file being moved.
        new_path: Destination path for the file.
        dry_run: Whether to preview changes without rewriting files or moving.
        git_root: Custom git root path. If None, will auto-detect from cwd.
        docs_root: Custom docs root path. If None, will use git_root/src.

    Returns:
        A list of (old_url, new_url) tuples representing link changes.

    Raises:
        RuntimeError: If git_root or docs_root cannot be determined or don't exist.
    """
    old_abs: Path = old_path.expanduser().resolve()
    new_abs: Path = new_path.expanduser().resolve()

    if git_root is None:
        git_root = _find_git_root(Path.cwd())

    if docs_root is None:
        docs_root = git_root / "src"

    if not docs_root.is_dir():
        msg = (
            f"Expected docs root at {docs_root}, but it does not exist "
            "or is not a directory."
        )
        raise RuntimeError(msg)

    logger.info("Documentation root: %s", docs_root)
    logger.info("Scanning for links to %s…", old_abs.relative_to(docs_root))

    changes: list[_LinkChange] = _scan_and_rewrite(
        docs_root, old_abs, new_abs, dry_run=dry_run
    )

    if changes:
        logger.info("🏷️  Rewrote %d link(s).", len(changes))
    else:
        logger.info("No links needed updating.")

    if dry_run:
        # Also preview internal link updates that would happen in the moved file
        logger.info("🔗  Previewing internal link updates in file to be moved...")
        if old_abs.suffix.lower() in [".md", ".mdx"]:
            internal_changes = _update_internal_links_in_moved_file(
                old_abs, old_abs.parent, new_abs.parent, docs_root, dry_run=True
            )
        elif old_abs.suffix.lower() == ".ipynb":
            internal_changes = _update_internal_links_in_moved_notebook(
                old_abs, old_abs.parent, new_abs.parent, docs_root, dry_run=True
            )
        else:
            internal_changes = []

        if internal_changes:
            logger.info(
                "Would update %d internal link(s) within moved file.",
                len(internal_changes),
            )
            changes.extend(internal_changes)
        else:
            logger.info("No internal links would need updating in moved file.")

        logger.info("Dry-run complete - no files were moved.")
        return changes

    _write_changes_log(old_abs, new_abs, git_root)
    # Move the file on disk.
    new_abs.parent.mkdir(parents=True, exist_ok=True)
    logger.info("🚚  Moving %s → %s", old_abs, new_abs)
    shutil.move(str(old_abs), str(new_abs))

    # Update internal links within the moved file
    logger.info("🔗  Updating internal links in moved file...")
    if new_abs.suffix.lower() in [".md", ".mdx"]:
        internal_changes = _update_internal_links_in_moved_file(
            new_abs, old_abs.parent, new_abs.parent, docs_root, dry_run=False
        )
    elif new_abs.suffix.lower() == ".ipynb":
        internal_changes = _update_internal_links_in_moved_notebook(
            new_abs, old_abs.parent, new_abs.parent, docs_root, dry_run=False
        )
    else:
        internal_changes = []

    if internal_changes:
        logger.info(
            "🔧  Updated %d internal link(s) within moved file.", len(internal_changes)
        )
        changes.extend(internal_changes)
    else:
        logger.info("No internal links needed updating in moved file.")

    logger.info("Done! ✨")

    return changes


def drop_suffix_from_links(
    md_source: str,
    *,
    strip_suffixes: tuple[str, ...] = (".md", ".mdx"),
) -> tuple[bool, str]:
    """Drop specific suffixes from relative links in Markdown text.

    Args:
        md_source: The Markdown source text to process.
        strip_suffixes: A tuple of suffixes to remove from links.

    Returns:
        2-tuple (was_modified, new_source)
    """
    changes: list[tuple[str, str]] = []
    modified = False

    def _replacer(match: re.Match[str]) -> str:
        nonlocal modified
        label, url, anchor = match.groups()
        anchor = anchor or ""

        # Ignore absolute, external, mailto, or in-page-anchor links
        if url.startswith(("http://", "https://", "mailto:", "/")) or (
            not url and anchor
        ):
            return match.group(0)

        # Remove any recognised suffix found at the *end* of the URL
        for suffix in strip_suffixes:
            if url.endswith(suffix):
                new_url = url[: -len(suffix)]
                old_full, new_full = url + anchor, new_url + anchor
                changes.append((old_full, new_full))
                modified = True
                return f"{label}({new_full})"

        return match.group(0)

    new_source = _LINK_PATTERN.sub(_replacer, md_source)
    return (modified, new_source) if modified else (False, md_source)


__all__ = ["drop_suffix_from_links", "move_file_with_link_updates"]
