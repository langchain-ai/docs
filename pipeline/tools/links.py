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


logger = logging.getLogger(__name__)


def _find_git_root(start: Path) -> Path:
    """Return the repository root - the closest ancestor containing ``.git``.

    Args:
        start: A path *inside* the repository.

    Returns:
        The absolute path to the repo's root directory.

    Raises:
        RuntimeError: If no ``.git`` directory is found while traversing up the
            directory tree.
    """
    for candidate in (start, *start.parents):
        if (candidate / ".git").is_dir():
            return candidate
    msg = f"Could not locate Git repository root from {start}."
    raise RuntimeError(msg)


def _rel_to_docs_root(path: Path, docs_root: Path) -> Path:
    """Return *path* relative to *docs_root* resolving any symlinks.

    Args:
        path: The file path to normalise.
        docs_root: The root of the documentation tree (``<repo>/src``).

    Returns:
        A :class:`pathlib.Path` representing *path* relative to *docs_root*.
    """
    return path.resolve().relative_to(docs_root.resolve())


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
        A list of ``(old_url, new_url)`` tuples representing link changes.
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
        docs_root: The root of the documentation tree (``<repo>/src``).
        dry_run: Whether the operation is a preview (no disk writes).

    Returns:
        A list of ``(old_url, new_url)`` tuples representing link changes.
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


def _update_internal_links_in_moved_notebook(  # noqa: C901
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
        A list of ``(old_url, new_url)`` tuples representing link changes.
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


def _rewrite_links_in_notebook(  # noqa: C901
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
        A list of ``(old_url, new_url)`` tuples representing every link change
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

    return changes


def _write_changes_log(old_path: Path, new_path: Path, root: Path) -> None:
    """Append file move to ``link_changes.jsonl`` as a JSON array.

    Args:
        old_path: The original file path.
        new_path: The new file path.
        root: The directory where the log file will be written.
    """
    log_path = root / "link_changes.jsonl"
    with log_path.open("a", encoding=ENCODING) as fp:
        fp.write(json.dumps([str(old_path), str(new_path)]) + "\n")


def move_file_with_link_updates(  # noqa: C901, PLR0912
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


__all__ = ["move_file_with_link_updates", "drop_suffix_from_links"]
