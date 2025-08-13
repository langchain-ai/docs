"""Documentation builder implementation."""

import json
import logging
import re
import shutil
from pathlib import Path

import yaml
from tqdm import tqdm

from pipeline.preprocessors import preprocess_markdown

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
            ".yml",
            ".yaml",
            ".css",
            ".js",
        }

        # Mapping of language codes to full names for URLs
        self.language_url_names = {
            "python": "python",
            "js": "javascript",
        }

    def build_all(self) -> None:
        """Build all documentation files from source to build directory.

        This method clears the build directory and creates version-specific builds
        for both Python and JavaScript documentation.

        The process includes:
        1. Clearing the existing build directory
        2. Building Python version with python/ prefix
        3. Building JavaScript version with javascript/ prefix
        4. Copying shared files (images, configs, etc.)

        Displays:
            Progress bars showing build progress for each version.
        """
        logger.info(
            "Building versioned documentation from %s to %s",
            self.src_dir,
            self.build_dir,
        )

        # Clear build directory
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        self.build_dir.mkdir(parents=True, exist_ok=True)

        # Build LangGraph versioned content (oss/ -> oss/python/ and oss/javascript/)
        logger.info("Building LangGraph Python version...")
        self._build_langgraph_version("oss/python", "python")

        logger.info("Building LangGraph JavaScript version...")
        self._build_langgraph_version("oss/javascript", "js")

        # Build unversioned content (same content regardless of version)
        logger.info("Building LangGraph Platform content...")
        self._build_unversioned_content("langgraph-platform", "langgraph-platform")

        logger.info("Building LangChain Labs content...")
        self._build_unversioned_content("labs", "labs")

        # Copy shared files (docs.json, images, etc.)
        logger.info("Copying shared files...")
        self._copy_shared_files()

        logger.info("✅ New structure build complete")

    def _convert_yaml_to_json(self, yaml_file_path: Path, output_path: Path) -> None:
        """Convert a YAML file to JSON format.

        This method loads a docs.yml file using YAML safe_load and writes
        the corresponding docs.json file to the build directory.

        Args:
            yaml_file_path: Path to the source YAML file.
            output_path: Path where the JSON file should be written.
        """
        try:
            # Load YAML content
            with yaml_file_path.open("r", encoding="utf-8") as yaml_file:
                yaml_content = yaml.safe_load(yaml_file)

            # Convert output path from .yml to .json
            json_output_path = output_path.with_suffix(".json")

            # Write JSON content
            with json_output_path.open("w", encoding="utf-8") as json_file:
                json.dump(yaml_content, json_file, indent=2, ensure_ascii=False)

        except yaml.YAMLError:
            logger.exception("Failed to parse YAML file %s", yaml_file_path)
            raise
        except Exception:
            logger.exception("Failed to convert %s to JSON", yaml_file_path)
            raise

    def _rewrite_oss_links(self, content: str, target_language: str | None) -> str:
        """Rewrite /oss/ links to include the target language.

        Args:
            content: The markdown content to process.
            target_language: Target language ("python" or "js") or None to skip rewriting.

        Returns:
            Content with rewritten links.
        """
        if not target_language:
            return content

        def rewrite_link(match: re.Match) -> str:
            """Rewrite a single link match."""
            pre = match.group(1)  # Everything before the URL
            url = match.group(2)  # The URL
            post = match.group(3)  # Everything after the URL

            # Only rewrite absolute /oss/ paths
            if url.startswith("/oss/"):
                parts = url.split("/")
                # Insert full language name after "oss"
                parts.insert(2, self.language_url_names[target_language])
                url = "/".join(parts)

            return f"{pre}{url}{post}"

        # Match markdown links and HTML links/anchors
        # This handles both [text](/oss/path) and <a href="/oss/path">
        pattern = r'(\[.*?\]\(|\bhref="|")(/oss/[^")\s]+)([")\s])'
        return re.sub(pattern, rewrite_link, content)

    def _process_markdown_content(
        self, content: str, file_path: Path, target_language: str | None = None
    ) -> str:
        """Process markdown content with preprocessing.

        This method applies preprocessing (cross-reference resolution and
        conditional blocks) to markdown content.

        Args:
            content: The markdown content to process.
            file_path: Path to the source file (for error reporting).
            target_language: Target language for conditional blocks ("python" or "js").

        Returns:
            The processed markdown content.
        """
        try:
            # First apply standard markdown preprocessing
            content = preprocess_markdown(
                content, file_path, target_language=target_language
            )

            # Then rewrite /oss/ links to include language
            content = self._rewrite_oss_links(content, target_language)

            return content
        except Exception:
            logger.exception("Failed to process markdown content from %s", file_path)
            raise

    def _process_markdown_file(
        self, input_path: Path, output_path: Path, target_language: str | None = None
    ) -> None:
        """Process a markdown file with preprocessing and copy to output.

        This method reads a markdown file, applies preprocessing (cross-reference
        resolution and conditional blocks), and writes the processed content to
        the output path.

        Args:
            input_path: Path to the source markdown file.
            output_path: Path where the processed file should be written.
            target_language: Target language for conditional blocks ("python" or "js").
        """
        try:
            # Read the source markdown content
            with input_path.open("r", encoding="utf-8") as f:
                content = f.read()

            # Apply markdown preprocessing
            processed_content = self._process_markdown_content(
                content, input_path, target_language
            )

            # Convert .md to .mdx if needed
            if input_path.suffix.lower() == ".md":
                output_path = output_path.with_suffix(".mdx")

            # Write the processed content
            with output_path.open("w", encoding="utf-8") as f:
                f.write(processed_content)

        except Exception:
            logger.exception("Failed to process markdown file %s", input_path)
            raise

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

        # Handle special case for docs.yml files
        if file_path.name == "docs.yml" and file_path.suffix.lower() in {
            ".yml",
            ".yaml",
        }:
            self._convert_yaml_to_json(file_path, output_path)
            logger.info("Converted YAML to JSON: %s", relative_path)
        # For other files, copy directly if supported
        elif file_path.suffix.lower() in self.copy_extensions:
            # Handle markdown files with preprocessing
            if file_path.suffix.lower() in {".md", ".mdx"}:
                self._process_markdown_file(file_path, output_path)
                logger.info("Processed markdown: %s", relative_path)
            else:
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

        # Handle special case for docs.yml files
        if file_path.name == "docs.yml" and file_path.suffix.lower() in {
            ".yml",
            ".yaml",
        }:
            self._convert_yaml_to_json(file_path, output_path)
            return True
        # Copy other supported files directly
        if file_path.suffix.lower() in self.copy_extensions:
            # Handle markdown files with preprocessing
            if file_path.suffix.lower() in {".md", ".mdx"}:
                self._process_markdown_file(file_path, output_path)
                return True
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

    def _build_langgraph_version(self, output_dir: str, target_language: str) -> None:
        """Build LangGraph (oss/) content for a specific version.

        Args:
            output_dir: Output directory (e.g., "langgraph/python", "langgraph/javascript").
            target_language: Target language for conditional blocks ("python" or "js").
        """
        # Only process files in the oss/ directory
        oss_dir = self.src_dir / "oss"
        if not oss_dir.exists():
            logger.warning("oss/ directory not found, skipping LangGraph build")
            return

        all_files = [
            file_path
            for file_path in oss_dir.rglob("*")
            if file_path.is_file() and not self._is_shared_file(file_path)
        ]

        if not all_files:
            logger.info("No files found in oss/ directory for %s", output_dir)
            return

        # Process files with progress bar
        copied_count: int = 0
        skipped_count: int = 0

        with tqdm(
            total=len(all_files),
            desc=f"Building {output_dir} files",
            unit="file",
            ncols=80,
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
        ) as pbar:
            for file_path in all_files:
                # Calculate relative path from oss/ directory
                relative_path = file_path.relative_to(oss_dir)
                # Build to output_dir/ (not output_dir/oss/)
                output_path = self.build_dir / output_dir / relative_path

                result = self._build_single_file(
                    file_path,
                    output_path,
                    target_language,
                    pbar,
                    f"{output_dir}/{relative_path}",
                )
                if result:
                    copied_count += 1
                else:
                    skipped_count += 1
                pbar.update(1)

        logger.info(
            "✅ %s complete: %d files copied, %d files skipped",
            output_dir,
            copied_count,
            skipped_count,
        )

    def _build_unversioned_content(self, source_dir: str, output_dir: str) -> None:
        """Build unversioned content (langgraph-platform/ or labs/).

        Args:
            source_dir: Source directory name (e.g., "langgraph-platform", "labs").
            output_dir: Output directory name (same as source_dir).
        """
        src_path = self.src_dir / source_dir
        if not src_path.exists():
            logger.warning("%s/ directory not found, skipping", source_dir)
            return

        all_files = [
            file_path
            for file_path in src_path.rglob("*")
            if file_path.is_file() and not self._is_shared_file(file_path)
        ]

        if not all_files:
            logger.info("No files found in %s/ directory", source_dir)
            return

        # Process files with progress bar
        copied_count: int = 0
        skipped_count: int = 0

        with tqdm(
            total=len(all_files),
            desc=f"Building {output_dir} files",
            unit="file",
            ncols=80,
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
        ) as pbar:
            for file_path in all_files:
                # Calculate relative path from source directory
                relative_path = file_path.relative_to(src_path)
                # Build directly to output_dir/
                output_path = self.build_dir / output_dir / relative_path

                result = self._build_single_file(
                    file_path,
                    output_path,
                    "python",
                    pbar,
                    f"{output_dir}/{relative_path}",
                )
                if result:
                    copied_count += 1
                else:
                    skipped_count += 1
                pbar.update(1)

        logger.info(
            "✅ %s complete: %d files copied, %d files skipped",
            output_dir,
            copied_count,
            skipped_count,
        )

    def _build_single_file(
        self,
        file_path: Path,
        output_path: Path,
        target_language: str,
        pbar: tqdm,
        display_path: str,
    ) -> bool:
        """Build a single file with progress bar integration.

        Args:
            file_path: Path to the source file to be built.
            output_path: Full output path for the file.
            target_language: Target language for conditional blocks ("python" or "js").
            pbar: tqdm progress bar instance for updating the description.
            display_path: Path to display in progress bar.

        Returns:
            True if the file was copied, False if it was skipped.
        """
        # Update progress bar description with current file
        pbar.set_postfix_str(display_path)

        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Handle special case for docs.yml files
        if file_path.name == "docs.yml" and file_path.suffix.lower() in {
            ".yml",
            ".yaml",
        }:
            self._convert_yaml_to_json(file_path, output_path)
            return True
        # Copy other supported files
        if file_path.suffix.lower() in self.copy_extensions:
            # Handle markdown files with preprocessing
            if file_path.suffix.lower() in {".md", ".mdx"}:
                self._process_markdown_file(file_path, output_path, target_language)
                return True
            shutil.copy2(file_path, output_path)
            return True
        return False

    def _build_version_file_with_progress(
        self, file_path: Path, version_dir: str, target_language: str, pbar: tqdm
    ) -> bool:
        """Build a single file for a specific version with progress bar integration.

        Args:
            file_path: Path to the source file to be built.
            version_dir: Directory name for this version (e.g., "python", "javascript").
            target_language: Target language for conditional blocks ("python" or "js").
            pbar: tqdm progress bar instance for updating the description.

        Returns:
            True if the file was copied, False if it was skipped.
        """
        relative_path = file_path.relative_to(self.src_dir)
        # Add version prefix to the output path
        output_path = self.build_dir / version_dir / relative_path

        # Update progress bar description with current file
        pbar.set_postfix_str(f"{version_dir}/{relative_path}")

        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Handle special case for docs.yml files
        if file_path.name == "docs.yml" and file_path.suffix.lower() in {
            ".yml",
            ".yaml",
        }:
            self._convert_yaml_to_json(file_path, output_path)
            return True
        # Copy other supported files
        if file_path.suffix.lower() in self.copy_extensions:
            # Handle markdown files with preprocessing
            if file_path.suffix.lower() in {".md", ".mdx"}:
                self._process_markdown_file(file_path, output_path, target_language)
                return True
            shutil.copy2(file_path, output_path)
            return True
        return False

    def _is_shared_file(self, file_path: Path) -> bool:
        """Check if a file should be shared between versions rather than duplicated.

        Args:
            file_path: Path to check.

        Returns:
            True if the file should be shared, False if it should be version-specific.
        """
        # Shared files: docs.json, images directory, JavaScript files, snippets
        relative_path = file_path.relative_to(self.src_dir)

        # docs.json should be shared
        if file_path.name == "docs.json":
            return True

        # Images directory should be shared
        if "images" in relative_path.parts:
            return True

        # Snippets directory should be shared
        if "snippets" in relative_path.parts:
            return True

        # JavaScript and CSS files should be shared (used for custom scripts/styles)
        if file_path.suffix.lower() in {".js", ".css"}:
            return True

        return False

    def _copy_shared_files(self) -> None:
        """Copy files that should be shared between versions."""
        # Collect shared files
        shared_files = [
            file_path
            for file_path in self.src_dir.rglob("*")
            if file_path.is_file() and self._is_shared_file(file_path)
        ]

        if not shared_files:
            logger.info("No shared files found")
            return

        copied_count = 0
        for file_path in shared_files:
            relative_path = file_path.relative_to(self.src_dir)
            output_path = self.build_dir / relative_path

            # Create output directory if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if file_path.suffix.lower() in self.copy_extensions:
                shutil.copy2(file_path, output_path)
                copied_count += 1

        logger.info("✅ Shared files copied: %d files", copied_count)