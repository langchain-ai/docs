"""Documentation builder implementation."""

import copy
import json
import logging
import re
import shutil
from pathlib import Path
from typing import cast

import yaml
from tqdm import tqdm

from pipeline.preprocessors import has_conditional_blocks, preprocess_markdown
from pipeline.tools.mintlify import (
    MintlifyConfig,
    NavigationDropdown,
    NavigationGroup,
    NavigationTab,
    NavigationVersion,
)

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

        # Get all top-level directories in the source directory
        top_level_dirs = set()
        for item in self.src_dir.iterdir():
            if item.is_dir():
                top_level_dirs.add(item.name)

        # Get unique list of all conditional files and extract top-level directories
        conditional_dirs = set()
        for file_path in self._get_conditional_files():
            relative_path = file_path.relative_to(self.src_dir)
            if relative_path.parts:
                top_level_dir = relative_path.parts[0]
                conditional_dirs.add(top_level_dir)

        # Build versioned content for directories that contain conditional files
        for conditional_dir in conditional_dirs:
            self._build_conditional_docset(
                conditional_dir, f"{conditional_dir}/python", "python"
            )
            self._build_conditional_docset(
                conditional_dir, f"{conditional_dir}/javascript", "js"
            )

        # Build unversioned content for directories that don't contain conditional files
        for top_level_dir in top_level_dirs - conditional_dirs:
            self._build_docset(top_level_dir, top_level_dir)

        # Copy shared files (images, etc.)
        logger.info("Copying shared files...")
        self._copy_shared_files()

        # Build config files
        logger.info("Building config file...")
        config_file_path = self.src_dir / "docs.json"
        if config_file_path.exists():
            output_config_path = self.build_dir / "docs.json"
            self._build_config_file(
                config_file_path, output_config_path, conditional_dirs
            )

        logger.info("✅ New structure build complete")

    def _read_yaml_file(self, yaml_file_path: Path) -> dict:
        """Read a YAML file and return its content.

        Args:
            yaml_file_path: Path to the source YAML file.

        Returns:
            The content of the YAML file as a dictionary.
        """
        try:
            # Load YAML content
            with yaml_file_path.open("r", encoding="utf-8") as yaml_file:
                return yaml.safe_load(yaml_file)

        except yaml.YAMLError:
            logger.exception("Failed to parse YAML file %s", yaml_file_path)
            raise

    def _read_json_file(self, json_file_path: Path) -> dict:
        """Read a JSON file and return its content.

        Args:
            json_file_path: Path to the source JSON file.

        Returns:
            The content of the JSON file as a dictionary.
        """
        try:
            with json_file_path.open("r", encoding="utf-8") as json_file:
                return json.load(json_file)
        except json.JSONDecodeError:
            logger.exception("Failed to parse JSON file %s", json_file_path)
            raise

    def _rewrite_oss_links(self, content: str, target_language: str | None) -> str:
        """Rewrite /oss/ links to include the target language.

        Args:
            content: The markdown content to process.
            target_language: Target language ("python" or "js") or None to skip
                rewriting.

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

            # Only rewrite absolute /oss/ paths that don't contain 'images'
            if url.startswith("/oss/") and "images" not in url:
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
            return self._rewrite_oss_links(content, target_language)
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

        # Copy other supported files directly
        if file_path.suffix.lower() in self.copy_extensions:
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

    def _build_conditional_docset(
        self, source_dir: str, output_dir: str, target_language: str
    ) -> None:
        """Build a docset from a fenced directory.

        Args:
            source_dir: Source directory (e.g., "oss", "labs").
            output_dir: Output directory (e.g., "oss/python", "oss/javascript").
            target_language: Target language for conditional blocks ("python" or "js").
        """
        # Only process files in the oss/ directory
        src_path = self.src_dir / source_dir
        if not src_path.exists():
            logger.warning("%s directory not found, skipping build", src_path)
            return

        all_files = [
            file_path
            for file_path in src_path.rglob("*")
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
                relative_path = file_path.relative_to(src_path)
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

    def _build_docset(self, source_dir: str, output_dir: str) -> None:
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

        # Copy other supported files
        if file_path.suffix.lower() in self.copy_extensions:
            # Handle markdown files with preprocessing
            if file_path.suffix.lower() in {".md", ".mdx"}:
                self._process_markdown_file(file_path, output_path, target_language)
                return True
            shutil.copy2(file_path, output_path)
            return True
        return False

    def _build_config_file(
        self, file_path: Path, output_path: Path, conditional_dirs: set[str]
    ) -> None:
        """Build a docs.json file.

        Args:
            file_path: Path to the source file to be built.
            output_path: Full output path for the file.
            conditional_dirs: Set of conditional directories.
        """
        # Handle special case for docs.yml files
        if file_path.name == "docs.yml" and file_path.suffix.lower() in {
            ".yml",
            ".yaml",
        }:
            config = cast("MintlifyConfig", self._read_yaml_file(file_path))
        elif file_path.name == "docs.json" and file_path.suffix.lower() in {
            ".json",
        }:
            config = cast("MintlifyConfig", self._read_json_file(file_path))
        else:
            logger.warning("Unsupported config file: %s", file_path)
            return

        def crawl_versions(
            versions: list[NavigationVersion],
        ) -> list[NavigationVersion]:
            dropdown_mapping = [
                {
                    "title": "Python",
                    "icon": "python",
                    "version_path": "python",
                },
                {
                    "title": "JavaScript",
                    "icon": "square-js",
                    "version_path": "javascript",
                },
            ]
            for index, version in enumerate(versions):
                if self._config_version_has_conditional_pages(
                    version, conditional_dirs
                ):
                    tabs = version.get("tabs")
                    if tabs:
                        versions[index] = NavigationVersion(
                            version=version["version"],
                            dropdowns=self._expand_config_tabs(tabs, dropdown_mapping),
                        )
            return versions

        def crawl_config(config: MintlifyConfig) -> MintlifyConfig:
            navigation = config.get("navigation")
            if navigation and navigation.get("versions"):
                versions = navigation.get("versions")
                if versions is not None:
                    navigation["versions"] = crawl_versions(versions)
            return config

        output_config = crawl_config(copy.deepcopy(config))

        # Write the processed docs content
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(output_config, f, indent=2)

    def _config_version_has_conditional_pages(
        self, version: NavigationVersion, conditional_dirs: set[str]
    ) -> bool:
        """Check if a docs version has conditional pages.

        Args:
            version: The version dictionary to check.
            conditional_dirs: Set of conditional directories.
        """

        def crawl_group(group: NavigationGroup) -> bool:
            for page in group["pages"]:
                if isinstance(page, str) and "/" in page:
                    first_dir = page.split("/", 1)[0]
                    if first_dir in conditional_dirs:
                        return True
                elif isinstance(page, dict) and "group" in page:
                    if crawl_group(page):
                        return True
            return False

        def crawl_tabs(tabs: list[NavigationTab]) -> bool:
            for tab in tabs:
                groups = tab.get("groups")
                if groups:
                    for group in groups:
                        if crawl_group(group):
                            return True
            return False

        tabs = version.get("tabs")
        if tabs:
            return crawl_tabs(tabs)

        return False

    def _expand_config_tabs(
        self, tabs: list[NavigationTab], dropdown_mapping: list[dict]
    ) -> list[NavigationDropdown]:
        """Expand mintlify navigation tabs into dropdowns.

        Args:
            tabs: The tabs to expand.
            dropdown_mapping: A mapping of version names to their expanded versions.
        """

        def replace_page_version(page: str, version_path: str) -> str:
            if "/" in page:
                first_dir = page.split("/", 1)[0]
                rest_of_path = "/".join(page.split("/")[1:])
                return f"{first_dir}/{version_path}/{rest_of_path}"
            return f"{version_path}/{page}"

        def crawl_tabs(
            tabs: list[NavigationTab], *, version_path: str
        ) -> list[NavigationTab]:
            for index, tab in enumerate(tabs):
                tabs[index] = crawl_tab(tab, version_path=version_path)
            return tabs

        def crawl_tab(tab: NavigationTab, *, version_path: str) -> NavigationTab:
            groups = tab.get("groups")
            if groups:
                for index, group in enumerate(groups):
                    groups[index] = crawl_group(group, version_path=version_path)
            return tab

        def crawl_group(
            group: NavigationGroup, *, version_path: str
        ) -> NavigationGroup:
            for index, page in enumerate(group["pages"]):
                if isinstance(page, str) and "/" in page:
                    group["pages"][index] = replace_page_version(page, version_path)
                elif isinstance(page, dict) and "group" in page:
                    group["pages"][index] = crawl_group(page, version_path=version_path)
            return group

        return [
            NavigationDropdown(
                dropdown=mapping["title"],
                icon=mapping["icon"],
                tabs=crawl_tabs(
                    copy.deepcopy(tabs), version_path=mapping["version_path"]
                ),
            )
            for mapping in dropdown_mapping
        ]

    def _is_shared_file(self, file_path: Path) -> bool:
        """Check if a file should be shared between versions rather than duplicated.

        Args:
            file_path: Path to check.

        Returns:
            True if the file should be shared, False if it should be version-specific.
        """
        # Shared files: docs.json, images directory, JavaScript files, snippets
        relative_path = file_path.relative_to(self.src_dir)

        # Images directory should be shared
        if "images" in relative_path.parts:
            return True

        # Snippets directory should be shared
        if "snippets" in relative_path.parts:
            return True

        # JavaScript and CSS files should be shared (used for custom scripts/styles)
        return file_path.suffix.lower() in {".js", ".css"}

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

    def _is_conditional_file(self, file_path: Path) -> bool:
        """Check if a file is a code fenced file.

        Args:
            file_path: Path to check.

        Returns:
            True if the file is a code fenced file, False otherwise.
        """
        if file_path.suffix.lower() not in {".md", ".mdx"}:
            return False

        try:
            with file_path.open("r", encoding="utf-8") as f:
                content = f.read()
            return has_conditional_blocks(content)
        except Exception:
            logger.exception("Failed to read file %s", file_path)
            return False

    def _get_conditional_files(self) -> list[Path]:
        """Get all fenced files in the source directory.

        Returns:
            List of Path objects pointing to fenced files.
        """
        return [
            file_path
            for file_path in self.src_dir.rglob("*")
            if file_path.is_file() and self._is_conditional_file(file_path)
        ]
