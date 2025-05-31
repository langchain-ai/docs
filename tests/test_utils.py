"""Test utilities for the documentation build pipeline.

This module provides test utilities including context managers for setting up
temporary file systems with source and build directories.
"""

import shutil
import tempfile
from pathlib import Path
from typing import Any, List, Union
from typing import TypedDict


class File(TypedDict):
    """Represents a file in the test file system."""

    path: str
    """Relative path of the file within the source directory."""
    bytes: bytes | None
    """File as bytes, if applicable."""
    content: str | None
    """File content as string, if applicable. Assumes utf-8 encoding."""


class TestFileSystem:
    """Context manager for creating temporary test file systems.

    Creates a temporary directory structure with src/ and build/ subdirectories.
    The src/ directory is populated with the provided test files.

    Attributes:
        temp_dir: Path to the temporary directory.
        src_dir: Path to the source directory (temp_dir/src).
        build_dir: Path to the build directory (temp_dir/build).
    """

    def __init__(self, files: List[File]) -> None:
        """Initialize the test file system.

        Args:
            files: List of TestFile objects to create in the source directory.
        """
        self.files = files
        self.temp_dir: Path | None = None
        self.src_dir: Path | None = None
        self.build_dir: Path | None = None

    def __enter__(self) -> "TestFileSystem":
        """Enter the context manager and create the temporary file system.

        Returns:
            Self for method chaining.
        """
        # Create temporary directory
        self.temp_dir = Path(tempfile.mkdtemp())
        self.src_dir = self.temp_dir / "src"
        self.build_dir = self.temp_dir / "build"

        # Create src and build directories
        self.src_dir.mkdir()
        self.build_dir.mkdir()

        # Create test files in src directory
        for file in self.files:
            file_path = self.src_dir / file["path"]

            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file content
            if file["bytes"] is not None:
                file_path.write_bytes(file["bytes"])
            elif file["content"] is not None:
                file_path.write_text(file["content"], encoding="utf-8")
            else:
                raise ValueError("File must have either 'bytes' or 'content' defined")
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the context manager and clean up the temporary directory.

        Args:
            exc_type: Exception type (if any).
            exc_val: Exception value (if any).
            exc_tb: Exception traceback (if any).
        """
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def list_build_files(self) -> List[Path]:
        """List all files in the build directory.

        Returns:
            List of Path objects for files in the build directory,
            relative to the build directory.
        """
        if not self.build_dir.exists():
            return []

        files = []
        for file_path in self.build_dir.rglob("*"):
            if file_path.is_file():
                files.append(file_path.relative_to(self.build_dir))

        return sorted(files)

    def get_build_file(self, path: str) -> Union[str, bytes]:
        """Get the content of a file in the build directory.

        Args:
            path: Relative path to the file within the build directory.

        Returns:
            File content as string (for text files) or bytes (for binary files).

        Raises:
            FileNotFoundError: If the file doesn't exist.
        """
        file_path = self.build_dir / path

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        # Try to read as text first, fall back to bytes if it fails
        try:
            return file_path.read_text()
        except UnicodeDecodeError:
            return file_path.read_bytes()

    def build_file_exists(self, path: str) -> bool:
        """Check if a file exists in the build directory.

        Args:
            path: Relative path to the file within the build directory.

        Returns:
            True if the file exists, False otherwise.
        """
        return (self.build_dir / path).exists()
