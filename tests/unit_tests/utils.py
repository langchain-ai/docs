"""Test utilities for the documentation build pipeline.

This module provides test utilities including context managers for setting up
temporary file systems with source and build directories.
"""

import shutil
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import NotRequired

from typing_extensions import TypedDict


class File(TypedDict):
    """Represents a file in the test file system."""

    path: str
    """Relative path of the file within the source directory."""
    bytes: NotRequired[bytes]
    """File as bytes, if applicable."""
    content: NotRequired[str]
    """File content as string, if applicable. Assumes utf-8 encoding."""


class FileSystem:
    """Represents a test file system with source and build directories.

    This class provides methods for interacting with a test file system,
    including listing files, checking existence, and reading file contents.

    Attributes:
        temp_dir: Path to the temporary directory.
        src_dir: Path to the source directory (temp_dir/src).
        build_dir: Path to the build directory (temp_dir/build).
    """

    def __init__(self, temp_dir: Path, src_dir: Path, build_dir: Path) -> None:
        """Initialize the file system with directory paths.

        Args:
            temp_dir: Path to the temporary directory.
            src_dir: Path to the source directory.
            build_dir: Path to the build directory.
        """
        self.temp_dir = temp_dir
        self.src_dir = src_dir
        self.build_dir = build_dir

    def list_build_files(self) -> list[Path]:
        """List all files in the build directory.

        Returns:
            List of Path objects for files in the build directory,
            relative to the build directory.
        """
        if not self.build_dir.exists():
            return []

        files = [
            file_path.relative_to(self.build_dir)
            for file_path in self.build_dir.rglob("*")
            if file_path.is_file()
        ]
        return sorted(files)

    def build_file_exists(self, path: str) -> bool:
        """Check if a file exists in the build directory.

        Args:
            path: Relative path to the file within the build directory.

        Returns:
            True if the file exists, False otherwise.
        """
        return (self.build_dir / path).exists()


@contextmanager
def file_system(files: list[File]) -> Iterator[FileSystem]:
    """Create a temporary test file system with the given files.

    This context manager creates a temporary directory structure with src/ and build/
    subdirectories. The src/ directory is populated with the provided test files.
    The temporary directory is automatically cleaned up when exiting the context.

    Args:
        files: List of File objects to create in the source directory.

    Yields:
        A FileSystem instance with initialized directories.

    Example:
        ```python
        with test_file_system([
            {"path": "index.md", "content": "# Hello"},
            {"path": "image.png", "bytes": b"PNG_DATA"}
        ]) as fs:
            # Use fs to interact with the test file system
            assert fs.build_file_exists("index.md")
        ```
    """
    temp_dir = Path(tempfile.mkdtemp())
    src_dir = temp_dir / "src"
    build_dir = temp_dir / "build"

    try:
        # Create src and build directories
        src_dir.mkdir()
        build_dir.mkdir()

        # Create test files in src directory
        for file in files:
            file_path = src_dir / file["path"]

            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file content
            if file.get("bytes") is not None:
                file_path.write_bytes(file["bytes"])
            elif file.get("content") is not None:
                file_path.write_text(file["content"], encoding="utf-8")
            else:
                msg = "File must have either 'bytes' or 'content' defined"
                raise ValueError(msg)
        # Yield the file system
        yield FileSystem(temp_dir, src_dir, build_dir)
    finally:
        # Clean up the temporary directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


@contextmanager
def temp_directory(files: list[File]) -> Iterator[Path]:
    """Create a temporary directory with the given files.

    This context manager creates a temporary directory and populates it with
    the provided test files. The temporary directory is automatically cleaned
    up when exiting the context.

    Args:
        files: List of File objects to create in the directory.

    Yields:
        Path to the temporary directory.

    Example:
        ```python
        with temp_directory([
            {"path": "index.md", "content": "# Hello"},
            {"path": "subdir/image.png", "bytes": b"PNG_DATA"}
        ]) as temp_dir:
            # Use temp_dir to interact with the test directory
            assert (temp_dir / "index.md").exists()
        ```
    """
    temp_dir = Path(tempfile.mkdtemp()).resolve()

    try:
        # Create test files in temp directory
        for file in files:
            file_path = temp_dir / file["path"]

            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file content
            if file.get("bytes") is not None:
                file_path.write_bytes(file["bytes"])
            elif file.get("content") is not None:
                file_path.write_text(file["content"], encoding="utf-8")
            else:
                msg = "File must have either 'bytes' or 'content' defined"
                raise ValueError(msg)

        # Yield the temp directory path
        yield temp_dir
    finally:
        # Clean up the temporary directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
