"""Documentation builder implementation."""

import logging
import shutil
from pathlib import Path

from tqdm import tqdm

logger = logging.getLogger(__name__)


class DocumentationBuilder:
    """Builds documentation from source files to build directory.

    This class handles the process of copying supported documentation files
    from a source directory to a build directory, maintaining the directory
    structure and preserving file metadata.

    Attributes:
        src_dir: Path to the source directory containing documentation files.
        build_dir: Path to the build directory where files will be copied.
        copy_extensions: Set of file extensions that are supported for copying.
    """

    def __init__(self, src_dir: Path, build_dir: Path) -> None:
        """Initialize the DocumentationBuilder.

        Args:
            src_dir: Path to the source directory containing documentation files.
            build_dir: Path to the build directory where files will be copied.
        """
        self.src_dir = src_dir
        self.build_dir = build_dir

        # File extensions to copy directly
        self.copy_extensions: set[str] = {
            ".mdx",
            ".md",
            ".json",
            ".svg",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
        }

    def build_all(self) -> None:
        """Build all documentation files from source to build directory.

        This method clears the build directory and copies all supported files
        from the source directory, maintaining the directory structure.

        The process includes:
        1. Clearing the existing build directory
        2. Recreating the build directory
        3. Collecting all files to process
        4. Processing files with a progress bar
        5. Copying only files with supported extensions

        Displays:
            A progress bar showing build progress and file counts.
        """
        logger.info("Building from %s to %s", self.src_dir, self.build_dir)

        # Clear build directory
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        self.build_dir.mkdir(parents=True, exist_ok=True)

        # Collect all files to process
        all_files = [
            file_path for file_path in self.src_dir.rglob("*") if file_path.is_file()
        ]

        if not all_files:
            logger.info("No files found to build")
            return

        # Process files with progress bar
        copied_count: int = 0
        skipped_count: int = 0

        with tqdm(
            total=len(all_files),
            desc="Building files",
            unit="file",
            ncols=80,
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
        ) as pbar:
            for file_path in all_files:
                result = self._build_file_with_progress(file_path, pbar)
                if result:
                    copied_count += 1
                else:
                    skipped_count += 1
                pbar.update(1)

        logger.info(
            "✅ Build complete: %d files copied, %d files skipped",
            copied_count,
            skipped_count,
        )

    def build_file(self, file_path: Path) -> None:
        """Build a single file by copying it to the build directory.

        This method copies a single file from the source directory to the
        corresponding location in the build directory, but only if the file
        has a supported extension. The directory structure is preserved.

        Args:
            file_path: Path to the source file to be built. Must be within
                the source directory.

        Prints:
            A message indicating whether the file was copied or skipped.
        """
        if not file_path.is_file():
            msg = f"File does not exist: {file_path} this is likely a programming error"
            raise AssertionError(
                msg,
            )

        relative_path = file_path.relative_to(self.src_dir)
        output_path = self.build_dir / relative_path

        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # For now, just copy supported files directly
        if file_path.suffix.lower() in self.copy_extensions:
            shutil.copy2(file_path, output_path)
            logger.info("Copied: %s", relative_path)
        else:
            logger.info("Skipped: %s (unsupported extension)", relative_path)

    def _build_file_with_progress(self, file_path: Path, pbar: tqdm) -> bool:
        """Build a single file with progress bar integration.

        This method is similar to build_file but integrates with tqdm progress
        bar and returns a boolean result instead of printing messages.

        Args:
            file_path: Path to the source file to be built. Must be within
                the source directory.
            pbar: tqdm progress bar instance for updating the description.

        Returns:
            True if the file was copied, False if it was skipped.
        """
        relative_path = file_path.relative_to(self.src_dir)
        output_path = self.build_dir / relative_path

        # Update progress bar description with current file
        pbar.set_postfix_str(f"{relative_path}")

        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy supported files directly
        if file_path.suffix.lower() in self.copy_extensions:
            shutil.copy2(file_path, output_path)
            return True
        return False

    def build_files(self, file_paths: list[Path]) -> None:
        """Build specific files by copying them to the build directory.

        This method processes a list of specific files, building only those
        that exist. Shows a progress bar when processing multiple files.

        Args:
            file_paths: List of Path objects pointing to files to be built.
                Only existing files will be processed.
        """
        existing_files = list(file_paths)

        if not existing_files:
            logger.info("No files to build")
            return

        if len(existing_files) == 1:
            # For single file, just build directly without progress bar
            self.build_file(existing_files[0])
            return

        # For multiple files, show progress bar
        copied_count = 0
        skipped_count = 0

        with tqdm(
            total=len(existing_files),
            desc="Building files",
            unit="file",
            ncols=80,
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
        ) as pbar:
            for file_path in existing_files:
                result = self._build_file_with_progress(file_path, pbar)
                if result:
                    copied_count += 1
                else:
                    skipped_count += 1
                pbar.update(1)

        logger.info(
            "✅ Build complete: %d files copied, %d files skipped",
            copied_count,
            skipped_count,
        )
