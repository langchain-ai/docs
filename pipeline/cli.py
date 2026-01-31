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
from pipeline.tools.docusaurus_parser import convert_docusaurus_to_mintlify
from pipeline.tools.links import drop_suffix_from_links, move_file_with_link_updates
from pipeline.tools.notebook.convert import convert_notebook
from pipeline.tools.parser import ParseError, to_mint


def setup_logging() -> None:
    """Configure logging for the CLI application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )


logger = logging.getLogger(__name__)


def mv_command(args) -> None:  # noqa: ANN001
    """Handle the mv command for moving files with link updates."""
    move_file_with_link_updates(args.old_path, args.new_path, dry_run=args.dry_run)


def _find_files_to_migrate(
    input_path: Path, migration_type: str = "mkdocs"
) -> list[Path]:
    """Find all files to migrate in the given path.

    Args:
        input_path: Path to file or directory to search
        migration_type: Type of migration ("mkdocs" or "docusaurus")

    Returns:
        List of Path objects for files to migrate
    """
    if input_path.is_file():
        return [input_path]

    # File patterns based on migration type
    if migration_type == "docusaurus":
        patterns = ["**/*.ipynb", "**/*.md", "**/*.markdown", "**/*.mdx"]
    else:
        patterns = ["**/*.ipynb", "**/*.md", "**/*.markdown"]

    # Recursively find all relevant files
    files: list[Path] = []
    for pattern in patterns:
        files.extend(input_path.glob(pattern))

    return sorted(files)


def _process_single_file(
    file_path: Path, output_path: Path, *, dry_run: bool, migration_type: str = "mkdocs"
) -> bool:
    """Process a single file for migration.

    Args:
        file_path: Input file path
        output_path: Output file path
        dry_run: Whether to print to stdout instead of writing
        migration_type: Type of migration ("mkdocs" or "docusaurus")

    Returns:
        True if processing was successful, False if there was an error
    """
    try:
        extension = file_path.suffix.lower()
        content = file_path.read_text()

        if extension in {".md", ".markdown", ".mdx"}:
            if migration_type == "docusaurus":
                mint_markdown = convert_docusaurus_to_mintlify(content, file_path)
            else:
                mint_markdown = to_mint(content, str(file_path))
        elif extension == ".ipynb":
            markdown = convert_notebook(file_path)
            if migration_type == "docusaurus":
                mint_markdown = convert_docusaurus_to_mintlify(markdown, file_path)
            else:
                mint_markdown = to_mint(markdown, str(file_path))
        else:
            logger.warning(
                "Skipping unsupported file extension %s: %s", extension, file_path
            )
            return True  # Not an error, just unsupported

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
    except ParseError as e:
        # We want to use logger.error rather than exception here. We do not need the
        # full stack trace! ParseError should have a nice message.
        logger.error("Parse error while processing file: %s", str(e))  # noqa: TRY400
        return False
    except Exception:
        logger.exception("Unexpected error while processing file %s", file_path)
        return False

    return True


def _determine_output_path(
    input_path: Path, file_path: Path, args: argparse.Namespace, migration_type: str
) -> Path:
    """Determine the output path for a single file during migration."""
    if args.output:
        # Calculate relative path from input to maintain directory structure
        if input_path.is_dir():
            rel_path = file_path.relative_to(input_path)
            output_path = args.output / rel_path
            # For Docusaurus, preserve .mdx extension, otherwise convert to .md
            if migration_type == "docusaurus" and file_path.suffix.lower() == ".mdx":
                return output_path.with_suffix(".mdx")
            return output_path.with_suffix(".md")
        # Single file case
        return args.output
    # In-place update
    if file_path.suffix.lower() == ".ipynb":
        # Convert .ipynb to .md
        return file_path.with_suffix(".md")
    # Keep original extension for in-place updates
    return file_path


def _cleanup_original_file(
    file_path: Path, args: argparse.Namespace, *, dry_run: bool
) -> None:
    """Delete original file if needed (for .ipynb -> .md conversion)."""
    if not dry_run and not args.output and file_path.suffix.lower() == ".ipynb":
        file_path.unlink(missing_ok=True)
        logger.info("Deleted original file %s", file_path)


def migrate_command(args) -> None:  # noqa: ANN001
    """Handle the migrate command for converting markdown to mintlify format."""
    input_path = args.path
    migration_type = getattr(args, "migration_type", "mkdocs")

    # Determine if the path is a file or a directory
    if not input_path.exists():
        logger.exception("Path %s does not exist", input_path)
        sys.exit(1)

    # Find all files to migrate
    files_to_migrate = _find_files_to_migrate(input_path, migration_type)

    if not files_to_migrate:
        file_types = (
            ".ipynb, .md, .mdx" if migration_type == "docusaurus" else ".ipynb, .md"
        )
        logger.info("No %s files found in %s", file_types, input_path)
        return

    logger.info("Found %d files to migrate", len(files_to_migrate))

    if input_path.is_dir() and args.output and not args.output.exists():
        # Create output directory if it doesn't exist
        args.output.mkdir(parents=True, exist_ok=True)

    # Process multiple files with progress bar
    if len(files_to_migrate) > 1:
        logger.info("Processing %d files...", len(files_to_migrate))

    successful_files = 0
    failed_files = 0

    for file_path in files_to_migrate:
        logger.info("Processing %s", file_path.name)

        output_path = _determine_output_path(
            input_path, file_path, args, migration_type
        )

        success = _process_single_file(
            file_path,
            output_path,
            dry_run=args.dry_run,
            migration_type=migration_type,
        )

        if success:
            successful_files += 1
            _cleanup_original_file(file_path, args, dry_run=args.dry_run)
        else:
            failed_files += 1

    # Report final results
    if len(files_to_migrate) > 1:
        logger.info(
            "Migration completed: %d successful, %d failed out of %d total files",
            successful_files,
            failed_files,
            len(files_to_migrate),
        )
        if failed_files > 0:
            logger.warning(
                "%d files failed to migrate. Check the error messages above for "
                "details.",
                failed_files,
            )


def main() -> None:
    """Main CLI entry point.

    Parses command line arguments and routes to the appropriate command
    function. Supports both synchronous and asynchronous command functions.

    Commands:
        dev: Start development mode with file watching and live server.
        build: Build documentation files from source to build directory.
        mv: Move a file and update cross-references to maintain valid links.
        migrate: Convert MkDocs markdown files to mintlify format.
        migrate-docusaurus: Convert Docusaurus markdown files to mintlify format.

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

    # Migrate command (MkDocs to Mintlify)
    migrate_parser = subparsers.add_parser(
        "migrate",
        help="Convert MkDocs markdown files or folders to mintlify format",
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
    migrate_parser.set_defaults(func=migrate_command, migration_type="mkdocs")

    # Migrate Docusaurus command
    migrate_docusaurus_parser = subparsers.add_parser(
        "migrate-docusaurus",
        help="Convert Docusaurus markdown files or folders to mintlify format",
    )
    migrate_docusaurus_parser.add_argument(
        "path",
        type=Path,
        help="Path to the file or folder to convert",
    )
    migrate_docusaurus_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print converted markdown to stdout instead of writing to file",
    )
    migrate_docusaurus_parser.add_argument(
        "--output",
        type=Path,
        help="Output file or folder path (if not provided, updates files in place)",
    )
    migrate_docusaurus_parser.set_defaults(
        func=migrate_command, migration_type="docusaurus"
    )

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
