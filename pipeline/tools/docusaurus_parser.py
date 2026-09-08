"""Docusaurus to Mintlify migration parser.

This module provides functionality to parse Docusaurus-specific markdown
syntax and convert it to Mintlify format. It handles Docusaurus MDX
components, frontmatter, and other Docusaurus-specific features.
"""

from __future__ import annotations

import json
import re
import typing
from dataclasses import dataclass

import yaml

if typing.TYPE_CHECKING:
    from pathlib import Path


@dataclass
class DocusaurusConfig:
    """Configuration extracted from Docusaurus site."""

    title: str = ""
    tagline: str = ""
    url: str = ""
    base_url: str = "/"
    navbar: dict[str, typing.Any] | None = None
    sidebar: dict[str, typing.Any] | None = None


class DocusaurusParser:
    """Parser for Docusaurus markdown files."""

    def __init__(self, content: str, file_path: Path | None = None) -> None:
        """Initialize the parser.

        Args:
            content: The markdown content to parse
            file_path: Optional path to the source file for context
        """
        self.content = content
        self.file_path = file_path
        self.frontmatter: dict[str, typing.Any] = {}
        self.body = ""
        self._parse_frontmatter()

    def _parse_frontmatter(self) -> None:
        """Extract and parse YAML frontmatter from the content."""
        frontmatter_pattern = r"^---\s*\n(.*?)\n---\s*\n"
        match = re.match(frontmatter_pattern, self.content, re.DOTALL)

        if match:
            frontmatter_text = match.group(1)
            try:
                self.frontmatter = yaml.safe_load(frontmatter_text) or {}
            except yaml.YAMLError:
                self.frontmatter = {}
            self.body = self.content[match.end() :]
        else:
            self.body = self.content

    def to_mintlify(self) -> str:
        """Convert Docusaurus markdown to Mintlify format.

        Returns:
            Converted markdown content suitable for Mintlify
        """
        # Start with the body content
        result = self.body

        # Convert Docusaurus components to Mintlify equivalents
        result = self._convert_admonitions(result)
        result = self._convert_tabs(result)
        result = self._convert_code_blocks(result)
        result = self._convert_imports(result)
        result = self._convert_links(result)
        result = self._convert_assets(result)

        # Generate Mintlify frontmatter
        mintlify_frontmatter = self._generate_mintlify_frontmatter()

        if mintlify_frontmatter:
            result = f"---\n{mintlify_frontmatter}---\n\n{result}"

        return result.strip() + "\n"

    def _generate_mintlify_frontmatter(self) -> str:
        """Generate Mintlify-compatible frontmatter from Docusaurus frontmatter.

        Returns:
            YAML frontmatter string for Mintlify
        """
        mintlify_fm = {}

        # Map common Docusaurus frontmatter fields to Mintlify
        if "title" in self.frontmatter:
            mintlify_fm["title"] = self.frontmatter["title"]

        if "description" in self.frontmatter:
            mintlify_fm["description"] = self.frontmatter["description"]

        # Handle sidebar position/label
        if "sidebar_position" in self.frontmatter:
            mintlify_fm["sidebar_position"] = self.frontmatter["sidebar_position"]

        if "sidebar_label" in self.frontmatter:
            mintlify_fm["sidebar_label"] = self.frontmatter["sidebar_label"]

        # Convert custom IDs
        if "id" in self.frontmatter:
            mintlify_fm["id"] = self.frontmatter["id"]

        # Handle tags
        if "tags" in self.frontmatter:
            mintlify_fm["tags"] = self.frontmatter["tags"]

        if mintlify_fm:
            return yaml.dump(mintlify_fm, default_flow_style=False)
        return ""

    def _convert_admonitions(self, content: str) -> str:
        """Convert Docusaurus admonitions to Mintlify callouts.

        Converts from:
        :::note
        Content here
        :::

        To:
        <Note>
        Content here
        </Note>
        """
        # Pattern to match Docusaurus admonitions
        admonition_pattern = r":::(\w+)(?:\s+(.+?))?\n(.*?)\n:::"

        def replace_admonition(match: re.Match[str]) -> str:
            admonition_type = match.group(1).lower()
            title = match.group(2)
            content = match.group(3)

            # Map Docusaurus admonition types to Mintlify
            type_mapping = {
                "note": "Note",
                "tip": "Tip",
                "info": "Info",
                "caution": "Warning",
                "warning": "Warning",
                "danger": "Warning",
                "important": "Warning",
            }

            mintlify_type = type_mapping.get(admonition_type, "Note")

            result = f"<{mintlify_type}>"
            if title:
                result += f"\n**{title}**\n"
            result += f"\n{content}\n</{mintlify_type}>"

            return result

        return re.sub(admonition_pattern, replace_admonition, content, flags=re.DOTALL)

    def _convert_tabs(self, content: str) -> str:
        """Convert Docusaurus Tabs to Mintlify Tabs.

        Converts from:
        import Tabs from '@theme/Tabs';
        import TabItem from '@theme/TabItem';

        <Tabs>
        <TabItem value="js" label="JavaScript">
        Content here
        </TabItem>
        </Tabs>

        To:
        <Tabs>
        <Tab title="JavaScript">
        Content here
        </Tab>
        </Tabs>
        """
        # Remove import statements for Tabs
        content = re.sub(
            r"import\s+Tabs\s+from\s+['\"]@theme/Tabs['\"];\s*\n?", "", content
        )
        content = re.sub(
            r"import\s+TabItem\s+from\s+['\"]@theme/TabItem['\"];\s*\n?", "", content
        )

        # Convert TabItem to Tab with title attribute
        def replace_tab_item(match: re.Match[str]) -> str:
            attributes = match.group(1)
            content_match = match.group(2)

            # Extract label from attributes
            label_match = re.search(r'label=["\']([^"\']*)["\']', attributes)
            title = label_match.group(1) if label_match else "Tab"

            return f'<Tab title="{title}">{content_match}</Tab>'

        # Replace TabItem tags
        tab_item_pattern = r"<TabItem\s+([^>]*)>(.*?)</TabItem>"
        return re.sub(tab_item_pattern, replace_tab_item, content, flags=re.DOTALL)

    def _convert_code_blocks(self, content: str) -> str:
        """Convert Docusaurus code blocks with special syntax.

        Handles title attributes and other Docusaurus-specific code block features.
        """

        # Convert code blocks with title attribute
        def replace_code_block(match: re.Match[str]) -> str:
            lang = match.group(1) or ""
            title_match = match.group(2)
            code_content = match.group(3)

            if title_match:
                title = title_match.strip()
                return f'```{lang} title="{title}"\n{code_content}\n```'

            return f"```{lang}\n{code_content}\n```"

        # Pattern for code blocks with title
        code_pattern = r'```(\w+)?(?:\s+title=["\']([^"\']*)["\'])?\s*\n(.*?)\n```'
        return re.sub(code_pattern, replace_code_block, content, flags=re.DOTALL)

    def _convert_imports(self, content: str) -> str:
        """Remove or convert Docusaurus import statements."""
        # Remove common Docusaurus imports that don't have Mintlify equivalents
        imports_to_remove = [
            r"import\s+.*?\s+from\s+['\"]@docusaurus/.*?['\"];\s*\n?",
            r"import\s+.*?\s+from\s+['\"]@theme/.*?['\"];\s*\n?",
            r"import\s+.*?\s+from\s+['\"]@site/.*?['\"];\s*\n?",
        ]

        for pattern in imports_to_remove:
            content = re.sub(pattern, "", content, flags=re.MULTILINE)

        return content

    def _convert_links(self, content: str) -> str:
        """Convert Docusaurus-style links to work with new directory structure.

        This converts internal documentation links to work with the new Mintlify
        structure while preserving external links unchanged.
        """

        def replace_link(match: re.Match[str]) -> str:
            link_text = match.group(1)
            link_url = match.group(2)

            # Skip external links (http/https)
            if link_url.startswith(("http://", "https://")):
                return match.group(0)  # Return unchanged

            # Skip anchor-only links
            if link_url.startswith("#"):
                return match.group(0)  # Return unchanged

            # Convert Docusaurus doc references to new structure
            if link_url.startswith("/docs/"):
                # Map common Docusaurus paths to new Mintlify structure
                path_mappings = {
                    "/docs/tutorials/": "/oss/tutorials/",
                    "/docs/how_to/": "/oss/how-to/",
                    "/docs/concepts/": "/oss/concepts/",
                    "/docs/integrations/": "/oss/integrations/",
                    "/docs/guides/": "/oss/guides/",
                }

                # Apply path mappings
                new_url = link_url
                for old_path, new_path in path_mappings.items():
                    if link_url.startswith(old_path):
                        new_url = link_url.replace(old_path, new_path, 1)
                        break

                return f"{link_text}({new_url})"

            # Handle relative links (/oss/file or ../category/file)
            if link_url.startswith(("./", "../")) and link_url.endswith(".md"):
                # Remove .md extension if present
                new_url = link_url[:-3]  # Remove .md
                return f"{link_text}({new_url})"

            # For other relative links, just remove .md extension if present
            if link_url.endswith(".md"):
                new_url = link_url[:-3]  # Remove .md
                return f"{link_text}({new_url})"

            return match.group(0)  # Return unchanged if no conversion needed

        # Pattern to match markdown links [text](url)
        link_pattern = r"(\[[^\]]+\])\(([^)]+)\)"
        return re.sub(link_pattern, replace_link, content)

    def _convert_assets(self, content: str) -> str:
        """Convert asset references (images, etc.) to Mintlify format."""

        # Convert require() style asset imports to simple paths
        def replace_require(match: re.Match[str]) -> str:
            asset_path = match.group(1)
            # Remove @site prefix and convert to relative path
            asset_path = asset_path.removeprefix("@site/")  # Remove '@site/'
            return f'"{asset_path}"'

        # Pattern for require('@site/static/img/...')
        require_pattern = r'require\(["\'](@site/[^"\']*)["\']\)'
        return re.sub(require_pattern, replace_require, content)


def parse_docusaurus_config(config_path: Path) -> DocusaurusConfig:
    """Parse Docusaurus configuration file.

    Args:
        config_path: Path to docusaurus.config.js or similar config file

    Returns:
        DocusaurusConfig object with parsed configuration
    """
    if not config_path.exists():
        return DocusaurusConfig()

    # This is a simplified parser - a full implementation would need
    # to handle JavaScript parsing for docusaurus.config.js
    config = DocusaurusConfig()

    if config_path.suffix == ".json":
        try:
            with config_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                config.title = data.get("title", "")
                config.tagline = data.get("tagline", "")
                config.url = data.get("url", "")
                config.base_url = data.get("baseUrl", "/")
                config.navbar = data.get("navbar")
                config.sidebar = data.get("sidebar")
        except (OSError, json.JSONDecodeError):
            pass

    return config


def convert_docusaurus_to_mintlify(content: str, file_path: Path | None = None) -> str:
    """Convert Docusaurus markdown content to Mintlify format.

    Args:
        content: The markdown content to convert
        file_path: Optional path to the source file for context

    Returns:
        Converted markdown content suitable for Mintlify
    """
    parser = DocusaurusParser(content, file_path)
    return parser.to_mintlify()
