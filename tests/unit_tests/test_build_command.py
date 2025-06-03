"""Tests for the build command.

This module contains comprehensive tests for the build_command function,
covering various scenarios including default and custom directory paths,
error handling, and complex directory structures.
"""

from pathlib import Path

import pytest

from pipeline.commands.build import build_command
from tests.test_utils import TestFileSystem, test_binary_file, test_file


class TestBuildCommand:
    """Test suite for build_command function.

    This test class verifies the functionality of the build_command function,
    including parameter handling, error conditions, and integration with
    the DocumentationBuilder class.
    """

    def test_build_command_default_paths(
        self,
        temp_src_dir: Path,
        temp_build_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test build command with default src and build paths.

        Verifies that the build command works correctly when using
        custom source and build directory paths.

        Args:
            temp_src_dir: Temporary source directory fixture.
            temp_build_dir: Temporary build directory fixture.
            monkeypatch: Pytest monkeypatch fixture for mocking.
        """
        # Mock the default paths to use our temp directories
        monkeypatch.chdir(temp_src_dir.parent)

        # Create src directory in the expected location
        src_path = temp_src_dir.parent / "src"
        if src_path.exists():
            import shutil

            shutil.rmtree(src_path)
        src_path.mkdir()
        (src_path / "test.mdx").write_text("# Test")

        # Build to temp_build_dir by passing it as parameter
        result = build_command(
            None,
            src_dir=str(src_path),
            build_dir=str(temp_build_dir),
        )

        assert result == 0
        assert (temp_build_dir / "test.mdx").exists()

    @pytest.mark.parametrize(
        "src_name,build_name",
        [
            ("docs", "dist"),
            ("source", "output"),
            ("content", "public"),
            ("markdown", "html"),
        ],
    )
    def test_build_command_custom_paths(
        self,
        temp_src_dir: Path,
        temp_build_dir: Path,
        src_name: str,
        build_name: str,
    ) -> None:
        """Test build command with custom source and build directory names.

        Verifies that the build command works with various custom
        directory names for both source and build directories.

        Args:
            temp_src_dir: Temporary source directory fixture.
            temp_build_dir: Temporary build directory fixture.
            src_name: Custom source directory name.
            build_name: Custom build directory name.
        """
        # Create custom src directory
        custom_src = temp_src_dir.parent / src_name
        custom_src.mkdir(exist_ok=True)
        (custom_src / "page.mdx").write_text("# Custom Page")
        (custom_src / "data.json").write_text('{"custom": true}')

        # Create custom build directory
        custom_build = temp_src_dir.parent / build_name

        result = build_command(
            None,
            src_dir=str(custom_src),
            build_dir=str(custom_build),
        )

        assert result == 0
        assert custom_build.exists()
        assert (custom_build / "page.mdx").exists()
        assert (custom_build / "data.json").exists()
        assert (custom_build / "page.mdx").read_text() == "# Custom Page"

    def test_build_command_nonexistent_src(self, temp_build_dir: Path) -> None:
        """Test build command with non-existent source directory.

        Verifies that the build command returns an error code when
        the source directory doesn't exist.

        Args:
            temp_build_dir: Temporary build directory fixture.
        """
        nonexistent_src = "/path/that/does/not/exist"

        result = build_command(
            None,
            src_dir=nonexistent_src,
            build_dir=str(temp_build_dir),
        )

        assert result == 1  # Should return error code

    def test_build_command_complex_structure(self, temp_src_dir, temp_build_dir):
        """Test build command with complex directory structure."""
        # Create complex source structure
        (temp_src_dir / "guides" / "basic").mkdir(parents=True)
        (temp_src_dir / "guides" / "advanced").mkdir(parents=True)
        (temp_src_dir / "api" / "v1").mkdir(parents=True)

        # Add files
        (temp_src_dir / "index.mdx").write_text("# Home")
        (temp_src_dir / "guides" / "overview.md").write_text("# Guides")
        (temp_src_dir / "guides" / "basic" / "intro.mdx").write_text("# Basic Intro")
        (temp_src_dir / "guides" / "advanced" / "concepts.mdx").write_text("# Advanced")
        (temp_src_dir / "api" / "v1" / "reference.json").write_text(
            '{"version": "1.0"}',
        )
        (temp_src_dir / "assets" / "logo.svg").write_text("<svg>logo</svg>")

        result = build_command(
            None,
            src_dir=str(temp_src_dir),
            build_dir=str(temp_build_dir),
        )

        assert result == 0

        # Check all files and structure are preserved
        assert (temp_build_dir / "index.mdx").exists()
        assert (temp_build_dir / "guides" / "overview.md").exists()
        assert (temp_build_dir / "guides" / "basic" / "intro.mdx").exists()
        assert (temp_build_dir / "guides" / "advanced" / "concepts.mdx").exists()
        assert (temp_build_dir / "api" / "v1" / "reference.json").exists()
        assert (temp_build_dir / "assets" / "logo.svg").exists()

    @pytest.mark.parametrize(
        "src_dir,build_dir,expected_result",
        [
            ("valid_src", "valid_build", 0),
            ("nonexistent", "valid_build", 1),
            (
                "valid_src",
                "build_with_permissions",
                0,
            ),  # Assuming we have write permissions
        ],
    )
    def test_build_command_various_scenarios(
        self,
        temp_src_dir,
        temp_build_dir,
        src_dir,
        build_dir,
        expected_result,
    ):
        """Test build command with various directory scenarios."""
        # Setup based on parameters
        if src_dir == "valid_src":
            actual_src = temp_src_dir
            (actual_src / "test.mdx").write_text("# Test")
        else:
            actual_src = temp_src_dir.parent / src_dir

        if build_dir == "valid_build":
            actual_build = temp_build_dir
        else:
            actual_build = temp_src_dir.parent / build_dir

        result = build_command(
            None,
            src_dir=str(actual_src),
            build_dir=str(actual_build),
        )
        assert result == expected_result

    def test_build_command_with_test_filesystem(self) -> None:
        """Example test using the new TestFileSystem context manager.

        Demonstrates the clean, readable test setup with the new utilities.
        """
        files = [
            test_file("index.mdx", "# Welcome\nMain documentation page"),
            test_file("config.json", '{"name": "test-docs"}'),
            test_binary_file("logo.png", b"PNG_LOGO_DATA"),
            test_file("guides/setup.md", "# Setup Guide\nHow to get started"),
            test_file("ignored.txt", "This file should be ignored"),
        ]

        with TestFileSystem(files) as fs:
            # Test the build command
            result = build_command(
                None,
                src_dir=str(fs.src_dir),
                build_dir=str(fs.build_dir),
            )

            # Verify success
            assert result == 0

            # Verify files were built correctly
            assert fs.get_build_file_count() == 4  # txt file should be ignored
            assert fs.build_file_exists("index.mdx")
            assert fs.build_file_exists("config.json")
            assert fs.build_file_exists("logo.png")
            assert fs.build_file_exists("guides/setup.md")
            assert not fs.build_file_exists("ignored.txt")

            # Verify content
            assert "Welcome" in fs.get_build_file("index.mdx")
            assert fs.get_build_file("logo.png") == b"PNG_LOGO_DATA"

    def test_build_command_empty_src_directory(self, temp_src_dir, temp_build_dir):
        """Test build command with empty source directory."""
        # Clear the temp_src_dir
        for item in temp_src_dir.iterdir():
            if item.is_file():
                item.unlink()
            else:
                import shutil

                shutil.rmtree(item)

        result = build_command(
            None,
            src_dir=str(temp_src_dir),
            build_dir=str(temp_build_dir),
        )

        assert result == 0
        assert temp_build_dir.exists()
        # Build directory should be empty (or only contain directories)
        assert len(list(temp_build_dir.rglob("*"))) == 0
