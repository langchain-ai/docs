"""Populates the Python integrations landing page.

Results in `oss/python/integrations/providers/index.mdx`

Usage (from repo root):
```
uv sync --group test

uv run python pipeline/tools/partner_pkg_table.py
```
"""

from pathlib import Path

import yaml

# Packages to exclude from the table
IGNORE_PKG = {
    "langchain-cli",
    "langchain-core",
    "langchain-classic",
    "langchain",
    "langchain-tests",
    "langchain-text-splitters",
    "langchain-community",
    "langchain-experimental",
    "langchain-mcp-adapters",
}


DOCS_DIR = Path(__file__).parents[2]
PROVIDERS_PATH = Path() / "src" / "oss" / "python" / "integrations" / "providers"
PACKAGE_YML = Path() / "reference" / "packages.yml"

# Load package registry
with PACKAGE_YML.open() as f:
    PACKAGE_YML = yaml.safe_load(f)


# For now, only include packages that are in the langchain-ai org
# because we don't have a policy for inclusion in this table yet,
# and including all packages will make the list too long


def _get_type(package: dict) -> str:
    """Determine the type of package for categorization.

    Args:
        package: Package metadata dictionary.

    Returns:
        Type category as a string. One of "monorepo", "langchain-org",
        "third-party", or "ignore".
    """
    if package["name"] in IGNORE_PKG:
        return "ignore"
    if package["repo"] == "langchain-ai/langchain":
        return "monorepo"
    if package["repo"].startswith("langchain-ai/"):
        return "langchain-org"
    return "third-party"


def _enrich_package(p: dict) -> dict | None:
    """Enrich package metadata with additional fields.

    Args:
        p: Package metadata dictionary.

    Returns:
        Enriched package metadata dictionary or None if to be ignored.
    """
    # We assume the package name starts or ends with "langchain-"
    p["name_short"] = p["name"].removeprefix("langchain-")
    p["name_short"] = p["name_short"].removesuffix("-langchain")

    # If a title is not provided, use the short name with title case and
    # special handling for common terms/acronyms
    p["name_title"] = p.get("name_title") or p["name_short"].title().replace(
        "-", " "
    ).replace("db", "DB").replace("Db", "DB").replace("ai", "AI").replace("Ai", "AI")

    # Determine package type based on repo and name
    p["type"] = _get_type(p)
    if p["type"] == "ignore":  # Package in IGNORE_PKG
        # Exclude this package from the final list
        return None

    # Check if JS package exists (indicating JS support)
    p["js_exists"] = bool(p.get("js"))

    # Determine provider page URL
    default_provider_page = f"/oss/integrations/providers/{p['name_short']}/"
    default_provider_page_exists = any(
        (DOCS_DIR / PROVIDERS_PATH).glob(f"{p['name_short']}.*")
    )

    if custom_provider_page := p.get("provider_page"):
        # First priority: custom provider page specified in YAML
        p["provider_page"] = f"/oss/integrations/providers/{custom_provider_page}"
    elif default_provider_page_exists:
        # Second priority: default provider page based on naming convention
        p["provider_page"] = default_provider_page
    else:
        # If no provider page found, raise an error to prompt creation
        msg = (
            f"Provider page not found for {p['name_short']}. "
            "Please add one at oss/integrations/providers/"
            f"{p['name_short']}.mdx"
        )
        raise ValueError(msg)

    # Handling for package URLs
    if p["type"] in ("monorepo", "langchain-org"):
        if p.get("integration") == "false":
            p["package_url"] = (
                f"https://reference.langchain.com/python/{p['name_short']}/"
            )
        else:
            # Integration
            p["package_url"] = (
                "https://reference.langchain.com/python/integrations"
                f"/{p['name_short'].replace('-', '_')}/"
            )
    else:  # Third-party
        p["package_url"] = f"https://pypi.org/project/{p['name']}/"

    return p


PACKAGES_N = [_enrich_package(p) for p in PACKAGE_YML["packages"]]
PACKAGES = [p for p in PACKAGES_N if p is not None]

# Sort by downloads
PACKAGES_SORTED = sorted(PACKAGES, key=lambda p: p.get("downloads", 0), reverse=True)

# Truncate to top 50 by total downloads
PACKAGES_SORTED = PACKAGES_SORTED[:50]


def package_row(p: dict) -> str:
    """Generate a markdown table row for a package."""
    js = (
        f"✅ [(npm)](https://www.npmjs.com/package/{p['js']})"
        if p["js_exists"]
        else "❌"
    )
    link = p["provider_page"]
    title = p["name_title"]
    provider = f"[{title}]({link})" if link else title
    return (
        f"| {provider} "
        f"| [{p['name']}]({p['package_url']}) "
        f'| <a href="https://pypi.org/project/{p["name"]}/" target="_blank"><img src="https://static.pepy.tech/badge/{p["name"]}/month" alt="Downloads per month" noZoom height="100" class="rounded" /></a> '  # noqa: E501
        f'| <a href="https://pypi.org/project/{p["name"]}/" target="_blank"><img src="https://img.shields.io/pypi/v/{p["name"]}?style=flat-square&label=%20&color=orange" alt="PyPI - Latest version" noZoom height="100" class="rounded" /></a> '  # noqa: E501
        f"| {js} |"
    )


def table() -> str:
    """Generate the full markdown table for all packages."""
    header = """| Provider Overview | Package API Reference | Downloads | Latest Version | JS/TS Support |
| :--- | :--- | :--- | :--- | :--- |
"""  # noqa: E501
    return header + "\n".join(package_row(p) for p in PACKAGES_SORTED)


def doc() -> str:
    return f"""\
---
title: Integration packages
mode: wide
---

These providers have standalone `langchain-{{provider}}` packages for improved versioning, dependency management, and testing.

{table()}

## All providers

[See all providers](/oss/integrations/providers/all_providers) or search for a provider using the search field.

<Info>
    If you'd like to contribute an integration, see [our contributing guide](/oss/contributing).
</Info>

"""  # noqa: E501


if __name__ == "__main__":
    output_dir = Path() / "src" / "oss" / "python" / "integrations" / "providers"
    with (output_dir / "index.mdx").open("w") as f:
        f.write(doc())
