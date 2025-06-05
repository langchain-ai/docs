"""Move documentation files while automatically updating references.

This module provides functionality to move files within a documentation tree and
simultaneously update all relative links that point to the moved file. It scans
all Markdown files in the documentation root and rewrites any links that reference
the old file location to point to the new location, ensuring no links break.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import shutil
from pathlib import Path

import nbformat

__all__ = ["cli"]  # only the entry-point is considered public

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


def _rewrite_links(  # noqa: PLR0913
    md_file: Path,
    old_abs: Path,
    new_abs: Path,
    docs_root: Path,
    *,
    changes: list[_LinkChange],
    dry_run: bool,
) -> None:
    """Rewrite links in *md_file* that point to *old_abs*.

    Args:
        md_file: The Markdown file whose links are scanned.
        old_abs: Absolute path of the file being moved.
        new_abs: Absolute path where the file will be moved to.
        docs_root: The root of the documentation tree (``<repo>/src``).
        changes: Accumulator list that will be extended with every link change
            as ``(old_url, new_url)``.
        dry_run: Whether the operation is a preview (no disk writes).
    """
    src: str = md_file.read_text(encoding=ENCODING)
    modified: bool = False

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


def _rewrite_links_in_notebook(  # noqa: PLR0913, C901
    notebook_file: Path,
    old_abs: Path,
    new_abs: Path,
    docs_root: Path,
    *,
    changes: list[_LinkChange],
    dry_run: bool,
) -> None:
    """Rewrite links in markdown cells of a Jupyter notebook.

    Args:
        notebook_file: The Jupyter notebook file to process.
        old_abs: Absolute path of the file being moved.
        new_abs: Absolute path where the file will be moved to.
        docs_root: The root of the documentation tree.
        changes: Accumulator list that will be extended with every link change.
        dry_run: Whether the operation is a preview (no disk writes).
    """
    notebook = nbformat.read(notebook_file, as_version=nbformat.NO_CONVERT)

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
            _rewrite_links(
                md_file, old_abs, new_abs, docs_root, changes=changes, dry_run=dry_run
            )

    # Process Jupyter notebooks
    for notebook_file in docs_root.rglob("*.ipynb"):
        _rewrite_links_in_notebook(
            notebook_file, old_abs, new_abs, docs_root, changes=changes, dry_run=dry_run
        )

    return changes


def _write_changes_log(changes: list[_LinkChange], root: Path) -> None:
    """Append link changes to ``link_changes.jsonl`` one JSON array per line.

    Args:
        changes: An iterable of ``(old_url, new_url)`` pairs.
        root: The directory where the log file will be written.
    """
    if not changes:
        return
    log_path = root / "link_changes.jsonl"
    with log_path.open("a", encoding=ENCODING) as fp:
        for old, new in changes:
            fp.write(json.dumps([old, new]) + "\n")


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
        _write_changes_log(changes, git_root)
    else:
        logger.info("No links needed updating.")

    if dry_run:
        logger.info("Dry-run complete - no files were moved.")
        return changes

    # Move the file on disk.
    new_abs.parent.mkdir(parents=True, exist_ok=True)
    logger.info("🚚  Moving %s → %s", old_abs, new_abs)
    shutil.move(str(old_abs), str(new_abs))
    logger.info("Done! ✨")

    return changes


def cli() -> None:
    """Entry-point for the *meowz* command-line interface."""
    parser = argparse.ArgumentParser(
        prog="lmv",
        description=(
            "Move a page and update cross-references under the "
            "docs tree so that links remain valid."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("old", type=Path, help="Path to the file being moved.")
    parser.add_argument("new", type=Path, help="Destination path for the file.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without rewriting files or moving the document.",
    )

    args = parser.parse_args()
    move_file_with_link_updates(args.old, args.new, dry_run=args.dry_run)


def entrypoint() -> None:
    """Main entry point for the script."""
    # Configure logging *once* here so imported usage (e.g. tests) is not noisy.
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    cli()


if __name__ == "__main__":
    entrypoint()
