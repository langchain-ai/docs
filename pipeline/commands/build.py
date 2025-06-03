"""Build command implementation."""

import logging
from pathlib import Path
from typing import Any

from pipeline.core.builder import DocumentationBuilder

logger = logging.getLogger(__name__)


def build_command(
    args: Any,  # noqa: ARG001, ANN401
    src_dir: str = "src",
    build_dir: str = "build",
) -> int:
    """Build documentation from source to build directory.

    This function serves as the entry point for the build command, handling
    the process of building documentation from a source directory to a build
    directory. It validates inputs, creates necessary directories, and
    orchestrates the build process.

    Args:
        args: Command line arguments (not used in this function, but
            included for compatibility with other commands).
        src_dir: Path to the source directory containing documentation files.
            Defaults to "src".
        build_dir: Path to the build directory where files will be copied.
            Defaults to "build".

    Returns:
        Exit code: 0 for success, 1 for failure (e.g., source directory
        not found).

    Prints:
        Progress messages and error messages to stdout.
    """
    logger.info("Building documentation...")
    src_dir_path = Path(src_dir)
    build_dir_path = Path(build_dir)

    if not src_dir_path.exists():
        logger.error("Error: src directory not found")
        return 1

    # Create build directory
    build_dir_path.mkdir(exist_ok=True)

    # Initialize builder and build docs
    builder = DocumentationBuilder(src_dir_path, build_dir_path)
    builder.build_all()
    logger.info("Documentation built successfully in %s", build_dir_path)
    return 0
