"""Development command implementation.

This module provides the development command that combines building,
file watching, and live serving for an optimal development experience.
"""

import asyncio
import contextlib
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
    """
    logger.info("Starting development mode... (press Ctrl+C to stop)")

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
        logger.debug("Performing initial build...")
        build_result = build_command(args)
        if build_result != 0:
            logger.error("Initial build failed")
            return 1

    # Start file watcher
    watcher = FileWatcher(src_dir, build_dir)

    # Start mint dev in background
    logger.debug("Starting mint dev...")

    try:
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
    except FileNotFoundError:
        logger.exception(
            "Could not find `mint`. Run `make install` and retry "
            "(or install Mintlify CLI directly with `npm install -g mint@latest`)."
        )
        return 1

    # Start log forwarding tasks
    stdout_task = asyncio.create_task(_forward_logs(mint_process.stdout, "mint-stdout"))
    stderr_task = asyncio.create_task(_forward_logs(mint_process.stderr, "mint-stderr"))
    watcher_task = asyncio.create_task(watcher.start())
    mint_wait_task = asyncio.create_task(mint_process.wait())
    exit_code = 0

    try:
        logger.info("Watching for file changes...")
        done, _ = await asyncio.wait(
            {watcher_task, mint_wait_task},
            return_when=asyncio.FIRST_COMPLETED,
        )

        if mint_wait_task in done:
            exit_code = mint_wait_task.result()
            if exit_code != 0:
                logger.error("mint dev exited with code %d", exit_code)
        elif watcher_task.cancelled():
            logger.error("File watcher stopped unexpectedly")
            exit_code = 1
        else:
            watcher_error = watcher_task.exception()
            if watcher_error is not None:
                raise watcher_error
            logger.error("File watcher stopped unexpectedly")
            exit_code = 1
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("\nShutting down...")
    finally:
        if not watcher_task.done():
            await watcher.shutdown()
            watcher_task.cancel()

        if mint_process.returncode is None:
            with contextlib.suppress(ProcessLookupError):
                mint_process.terminate()

        if not mint_wait_task.done():
            try:
                await asyncio.wait_for(mint_wait_task, timeout=5)
            except TimeoutError:
                with contextlib.suppress(ProcessLookupError):
                    mint_process.kill()
                await mint_process.wait()

        stdout_task.cancel()
        stderr_task.cancel()

        # Wait for log forwarding tasks to complete
        await asyncio.gather(
            watcher_task,
            mint_wait_task,
            stdout_task,
            stderr_task,
            return_exceptions=True,
        )

    return exit_code
