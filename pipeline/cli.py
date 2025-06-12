"""CLI commands for the docs pipeline.

This module provides the main CLI interface for the documentation build
pipeline, including argument parsing and command routing.
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

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


def migrate_command(args) -> None:  # noqa: ANN001
    """Handle the migrate command for converting markdown to mintlify format."""
    logger.info("Converting %s to mintlify format...", args.path)

    # Determine if the path is a file or a directory
    if not args.path.exists():
        logger.exception("Path %s does not exist", args.path)
        sys.exit(1)

    if not args.path.is_file():
        logger.exception("Path %s is not a file", args.path)
        sys.exit(1)

    # Check the file extension to see if it's a markdown file

    extension = args.path.suffix.lower()

    content = Path(args.path).read_text()

    if extension in {".md", ".markdown"}:
        mint_markdown = to_mint(content)
    elif extension == ".ipynb":
        markdown = convert_notebook(args.path)
        mint_markdown = to_mint(markdown)
    else:
        logger.exception("Unsupported file extension %s", extension)
        sys.exit(1)

    _, mint_markdown = drop_suffix_from_links(mint_markdown)

    if args.dry_run:
        # Print the converted markdown to stdout
        print(mint_markdown)  # noqa: T201 (OK to use print)
    elif args.output_file:
        # Using open instead of Pathlib
        with Path(args.output_file).open("w", encoding="utf-8") as file:
            file.write(mint_markdown)
        logger.info("Output written to %s", args.output_file)
    else:
        # New output path should have an `.mdx` extension.
        # If extension is different, we delete the old file
        if extension != ".mdx":
            args.path.unlink(missing_ok=True)
            logger.info("Deleted old file %s", args.path)

        # Change extension to .mdx
        new_path = args.path.with_suffix(".mdx")

        with new_path.open("w", encoding="utf-8") as file:
            file.write(mint_markdown)

        logger.info("File %s updated", new_path)


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
        help="Convert markdown file to mintlify format",
    )
    migrate_parser.add_argument(
        "path",
        type=Path,
        help="Path to the markdown file to convert",
    )
    migrate_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print converted markdown to stdout instead of writing to file",
    )
    migrate_parser.add_argument(
        "--output-file",
        type=Path,
        help="Output file path (if not provided, updates file in place)",
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
