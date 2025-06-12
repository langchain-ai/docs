"""CLI commands for the docs pipeline.

This module provides the main CLI interface for the documentation build
pipeline, including argument parsing and command routing.
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from tqdm import tqdm

from pipeline.commands.build import build_command
from pipeline.commands.dev import dev_command
from pipeline.tools.links import drop_suffix_from_links, move_file_with_link_updates
from pipeline.tools.notebook.convert import convert_notebook
from pipeline.tools.parser import to_mint


def setup_logging() -> None:
    """Configure logging for the CLI application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


logger = logging.getLogger(__name__)


def mv_command(args) -> None:  # noqa: ANN001
    """Handle the mv command for moving files with link updates."""
    move_file_with_link_updates(args.old_path, args.new_path, dry_run=args.dry_run)


def _find_files_to_migrate(input_path: Path) -> list[Path]:
    """Find all .ipynb and .md files in the given path.

    Args:
        input_path: Path to file or directory to search

    Returns:
        List of Path objects for files to migrate
    """
    if input_path.is_file():
        return [input_path]

    # Recursively find all .ipynb and .md files
    files: list[Path] = []
    for pattern in ["**/*.ipynb", "**/*.md", "**/*.markdown"]:
        files.extend(input_path.glob(pattern))

    return sorted(files)


def _process_single_file(file_path: Path, output_path: Path, *, dry_run: bool) -> None:
    """Process a single file for migration.

    Args:
        file_path: Input file path
        output_path: Output file path
        dry_run: Whether to print to stdout instead of writing
    """
    extension = file_path.suffix.lower()
    content = file_path.read_text()

    if extension in {".md", ".markdown"}:
        mint_markdown = to_mint(content)
    elif extension == ".ipynb":
        markdown = convert_notebook(file_path)
        mint_markdown = to_mint(markdown)
    else:
        logger.warning(
            "Skipping unsupported file extension %s: %s", extension, file_path
        )
        return

    _, mint_markdown = drop_suffix_from_links(mint_markdown)

    if dry_run:
        # Print the converted markdown to stdout
        print(f"=== {file_path} ===")  # noqa: T201 (OK to use print)
        print(mint_markdown)  # noqa: T201 (OK to use print)
        print()  # noqa: T201 (OK to use print)
    else:
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the converted content
        with output_path.open("w", encoding="utf-8") as file:
            file.write(mint_markdown)

        logger.info("Converted %s -> %s", file_path, output_path)


def migrate_command(args) -> None:  # noqa: ANN001
    """Handle the migrate command for converting markdown to mintlify format."""
    input_path = args.path

    # Determine if the path is a file or a directory
    if not input_path.exists():
        logger.exception("Path %s does not exist", input_path)
        sys.exit(1)

    # Find all files to migrate
    files_to_migrate = _find_files_to_migrate(input_path)

    if not files_to_migrate:
        logger.info("No .ipynb or .md files found in %s", input_path)
        return

    if input_path.is_dir() and not args.output.exists():
        # Create output directory if it doesn't exist
        args.output.mkdir(parents=True, exist_ok=True)

    # Process multiple files with progress bar
    if len(files_to_migrate) > 1:
        logger.info("Processing %d files...", len(files_to_migrate))

    with tqdm(
        files_to_migrate, desc="Migrating files", disable=len(files_to_migrate) == 1
    ) as pbar:
        for file_path in pbar:
            pbar.set_description(f"Processing {file_path.name}")

            if args.output:
                # Calculate relative path from input to maintain directory structure
                if input_path.is_dir():
                    rel_path = file_path.relative_to(input_path)
                    output_path = args.output / rel_path
                    output_path = output_path.with_suffix(".md")
                else:
                    # Single file case
                    output_path = args.output
            # In-place update
            elif file_path.suffix.lower() == ".ipynb":
                # Convert .ipynb to .md
                output_path = file_path.with_suffix(".md")
            else:
                # Keep .md files as .md
                output_path = file_path

            _process_single_file(file_path, output_path, dry_run=args.dry_run)

            # Delete original file if needed (for .ipynb -> .md conversion)
            if (
                not args.dry_run
                and not args.output
                and file_path.suffix.lower() == ".ipynb"
            ):
                file_path.unlink(missing_ok=True)
                logger.info("Deleted original file %s", file_path)


def main() -> None:
    """Main CLI entry point.

    Parses command line arguments and routes to the appropriate command
    function. Supports both synchronous and asynchronous command functions.

    Commands:
        dev: Start development mode with file watching and live server.
        build: Build documentation files from source to build directory.
        mv: Move a file and update cross-references to maintain valid links.
        migrate: Convert markdown file to mintlify format.

    Exits:
        With code 1 if no command is specified or if the initial build fails.
    """
    setup_logging()
    parser = argparse.ArgumentParser(description="LangChain docs build pipeline")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Dev command
    dev_parser = subparsers.add_parser(
        "dev",
        help="Start development mode with file watching",
    )
    dev_parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Skip initial build and use existing build directory",
    )
    dev_parser.set_defaults(func=dev_command)

    # Build command
    build_parser = subparsers.add_parser("build", help="Build documentation")
    build_parser.add_argument(
        "--watch",
        action="store_true",
        help="Watch for file changes",
    )
    build_parser.set_defaults(func=build_command)

    # Move command
    mv_parser = subparsers.add_parser(
        "mv",
        help="Move a file and update cross-references",
    )
    mv_parser.add_argument(
        "old_path",
        type=Path,
        help="Path to the file being moved",
    )
    mv_parser.add_argument(
        "new_path",
        type=Path,
        help="Destination path for the file",
    )
    mv_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without rewriting files or moving the document",
    )
    mv_parser.set_defaults(func=mv_command)

    # Migrate command
    migrate_parser = subparsers.add_parser(
        "migrate",
        help="Convert markdown files or folders to mintlify format",
    )
    migrate_parser.add_argument(
        "path",
        type=Path,
        help="Path to the file or folder to convert",
    )
    migrate_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print converted markdown to stdout instead of writing to file",
    )
    migrate_parser.add_argument(
        "--output",
        type=Path,
        help="Output file or folder path (if not provided, updates files in place)",
    )
    migrate_parser.set_defaults(func=migrate_command)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    # Run the command
    if asyncio.iscoroutinefunction(args.func):
        asyncio.run(args.func(args))
    else:
        args.func(args)


if __name__ == "__main__":
    main()
