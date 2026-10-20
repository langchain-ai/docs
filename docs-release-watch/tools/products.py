"""Product registry for release-watch coverage.

Add a new product here and a matching skill under ``skills/<name>/`` when
extending coverage. For monorepo release feeds that publish several packages,
set ``release_tag_prefix`` so the agent only considers that package's tags.
"""

from __future__ import annotations

from typing import Any

PRODUCTS: dict[str, dict[str, Any]] = {
    "openwiki": {
        "display_name": "OpenWiki",
        "github_repo": "langchain-ai/openwiki",
        "docs_repo": "langchain-ai/docs",
        "docs_paths": ["src/oss/openwiki/"],
        "skill": "openwiki",
        "changelog_url": "https://github.com/langchain-ai/openwiki/releases",
        "release_tag_prefix": "",
        # Empty means include every path in get_release_diff.
        "source_path_prefixes": [],
        # Docs language fence scope for surgical PR validation.
        "language_scope": "shared",
        "memory_file": "/memories/agent/openwiki-releases.md",
    },
    "deepagents": {
        "display_name": "Deep Agents",
        "github_repo": "langchain-ai/deepagents",
        "docs_repo": "langchain-ai/docs",
        # Library docs only. Deep Agents Code is a separate product/package.
        "docs_paths": [
            "src/oss/deepagents/",
        ],
        "docs_path_exclude_prefixes": [
            "src/oss/deepagents/code/",
        ],
        "skill": "deepagents",
        "changelog_url": "https://github.com/langchain-ai/deepagents/releases",
        # Shared release feed also publishes deepagents-code, deepagents-acp, etc.
        "release_tag_prefix": "deepagents==",
        "source_path_prefixes": ["libs/deepagents/"],
        "language_scope": "python",
        "memory_file": "/memories/agent/deepagents-releases.md",
    },
    "deepagents-code": {
        "display_name": "Deep Agents Code",
        "github_repo": "langchain-ai/deepagents",
        "docs_repo": "langchain-ai/docs",
        "docs_paths": [
            "src/oss/deepagents/code/",
        ],
        "docs_path_exclude_prefixes": [],
        "skill": "deepagents-code",
        "changelog_url": "https://github.com/langchain-ai/deepagents/blob/main/libs/code/CHANGELOG.md",
        "release_tag_prefix": "deepagents-code==",
        "source_path_prefixes": ["libs/code/"],
        "language_scope": "shared",
        "memory_file": "/memories/agent/deepagents-code-releases.md",
    },
    "deepagentsjs": {
        "display_name": "Deep Agents JS",
        "github_repo": "langchain-ai/deepagentsjs",
        "docs_repo": "langchain-ai/docs",
        # Same library docs as Python Deep Agents; prefer :::js fences.
        "docs_paths": [
            "src/oss/deepagents/",
        ],
        "docs_path_exclude_prefixes": [
            "src/oss/deepagents/code/",
        ],
        "skill": "deepagentsjs",
        "changelog_url": "https://github.com/langchain-ai/deepagentsjs/releases",
        # Shared JS monorepo feed also publishes deepagents-acp@, @langchain/quickjs@, etc.
        "release_tag_prefix": "deepagents@",
        "source_path_prefixes": ["libs/deepagents/"],
        "language_scope": "js",
        "memory_file": "/memories/agent/deepagentsjs-releases.md",
    },
}


def list_products() -> list[str]:
    return sorted(PRODUCTS)


def get_product(product: str) -> dict[str, Any]:
    """Return the product config or raise a clear error."""
    key = product.strip().lower()
    if key not in PRODUCTS:
        known = ", ".join(list_products())
        raise ValueError(f"Unknown product {product!r}. Known products: {known}.")
    return PRODUCTS[key]
