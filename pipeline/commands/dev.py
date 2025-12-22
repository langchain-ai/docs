"""Development command implementation.

This module provides the development command that combines building,
file watching, and live serving for an optimal development experience.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any

from pipeline.commands.build import build_command
from pipeline.core.watcher import FileWatcher

logger = logging.getLogger(__name__)


async def _forward_logs(stream: asyncio.StreamReader | None, source: str) -> None:
    """Forward logs from a subprocess stream to the logger.

    Args:
        stream: The subprocess stream to read from.
        source: The source identifier for logging (e.g., "mint-stdout").
    """
    if stream is None:
        return

    mint_logger = logging.getLogger(source)

    try:
        while True:
            line = await stream.readline()
            if not line:
                break

            # Decode and strip the line
            decoded_line = line.decode("utf-8").rstrip()
            if decoded_line:
                # Use info level for stdout, error level for stderr
                if "stderr" in source:
                    mint_logger.error(decoded_line)
                else:
                    mint_logger.info(decoded_line)
    except asyncio.CancelledError:
        # Task was cancelled during shutdown
        pass


async def dev_command(
    args: Any | None,  # noqa: ANN401
) -> int:
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
        build_result = build_command(args)
        if build_result != 0:
            logger.error("Initial build failed")
            sys.exit(1)

    # Start file watcher
    watcher = FileWatcher(src_dir, build_dir)

    # Start mint dev in background
    logger.info("Starting mint dev...")

    # Use shell on Windows for .CMD compatibility, keep exec on Unix
    if sys.platform == "win32":
        # Windows requires shell for .CMD files
        mint_process = await asyncio.create_subprocess_shell(
            "mint dev --port 3000",
            cwd=build_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    else:
        # Unix systems can use exec directly
        mint_process = await asyncio.create_subprocess_exec(
            "mint",
            "dev",
            "--port",
            "3000",
            cwd=build_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

    # Start log forwarding tasks
    stdout_task = asyncio.create_task(_forward_logs(mint_process.stdout, "mint-stdout"))
    stderr_task = asyncio.create_task(_forward_logs(mint_process.stderr, "mint-stderr"))

    try:
        # Start file watching
        logger.info("Watching for file changes...")
        await watcher.start()
    except KeyboardInterrupt:
        logger.info("\nShutting down...")
    finally:
        # Cleanup
        mint_process.terminate()

        # Cancel log forwarding tasks
        stdout_task.cancel()
        stderr_task.cancel()

        try:
            await asyncio.wait_for(mint_process.wait(), timeout=5)
        except TimeoutError:
            mint_process.kill()

        # Wait for log forwarding tasks to complete
        await asyncio.gather(stdout_task, stderr_task, return_exceptions=True)

    return 0
