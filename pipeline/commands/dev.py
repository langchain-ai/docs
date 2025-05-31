"""Development command implementation.

This module provides the development command that combines building,
file watching, and live serving for an optimal development experience.
"""

import subprocess
import sys
from pathlib import Path
from typing import Any

from pipeline.commands.build import build_command
from pipeline.core.watcher import FileWatcher


async def dev_command(args: Any | None) -> int:
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
    print("Starting development mode...")

    # Check if we should skip the initial build
    skip_build = getattr(args, "skip_build", False) if args else False

    src_dir = Path("src")
    build_dir = Path("build")

    if skip_build:
        print("Skipping initial build (using existing build directory)")
        if not build_dir.exists():
            print(
                f"Warning: Build directory '{build_dir}' does not exist. You may want to run a build first."
            )
    else:
        # Perform a full build
        print("Performing initial build...")
        build_result = build_command(args)
        if build_result != 0:
            print("Initial build failed")
            sys.exit(1)

    # Start file watcher
    watcher = FileWatcher(src_dir, build_dir)

    # Start mint dev in background
    print("Starting mint dev...")
    mint_process = subprocess.Popen(
        ["mint", "dev", "--port", "3000"],
        cwd=build_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        # Start file watching
        print("Watching for file changes...")
        await watcher.start()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        # Cleanup
        mint_process.terminate()
        try:
            mint_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            mint_process.kill()

    return 0
