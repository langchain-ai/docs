"""Development command implementation.

This module provides the development command that combines building,
file watching, and live serving for an optimal development experience.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from argparse import Namespace

from pipeline.commands.build import build_command
from pipeline.core.watcher import FileWatcher

logger = logging.getLogger(__name__)


async def dev_command(args: "Namespace | None") -> int:
    """Start development mode with file watching and mint dev.

    This function orchestrates the development workflow by:
    1. Optionally performing an initial build of all documentation
    2. Starting a file watcher for automatic rebuilds
    3. Starting the Mint development server
    4. Managing cleanup when interrupted

    Args:
        args: Command line arguments containing options like --skip-build.

    Returns:
        Exit code: 0 for success, 1 for failure.

    Raises:
        KeyboardInterrupt: When the user interrupts the development server.
    """
    logger.info("Starting development mode...")

    # Check if we should skip the initial build
    skip_build = getattr(args, "skip_build", False) if args else False

    src_dir = Path("src")
    build_dir = Path("build")

    if skip_build:
        logger.info("Skipping initial build (using existing build directory)")
        if not build_dir.exists():
            logger.warning(
                "Build directory '%s' does not exist. "
                "You may want to run a build first.",
                build_dir,
            )
    else:
        # Perform a full build
        logger.info("Performing initial build...")
        build_result = build_command()
        if build_result != 0:
            logger.error("Initial build failed")
            sys.exit(1)

    # Start file watcher
    watcher = FileWatcher(src_dir, build_dir)

    # Start mint dev in background
    logger.info("Starting mint dev...")
    mint_process = await asyncio.create_subprocess_exec(
        "mint",
        "dev",
        "--port",
        "3000",
        cwd=build_dir,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        # Start file watching
        logger.info("Watching for file changes...")
        await watcher.start()
    except KeyboardInterrupt:
        logger.info("\nShutting down...")
    finally:
        # Cleanup
        mint_process.terminate()
        try:
            await asyncio.wait_for(mint_process.wait(), timeout=5)
        except asyncio.TimeoutError:
            mint_process.kill()

    return 0
