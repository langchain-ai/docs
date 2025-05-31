"""CLI commands for the docs pipeline.

This module provides the main CLI interface for the documentation build
pipeline, including argument parsing and command routing.
"""

import argparse
import asyncio
import sys

from pipeline.commands.build import build_command
from pipeline.commands.dev import dev_command


def main() -> None:
    """Main CLI entry point.

    Parses command line arguments and routes to the appropriate command
    function. Supports both synchronous and asynchronous command functions.

    Commands:
        dev: Start development mode with file watching and live server.
        build: Build documentation files from source to build directory.

    Exits:
        With code 1 if no command is specified or if the initial build fails.
    """
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
