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
    "langchain-model-profiles",
}

# Minimum downloads threshold for inclusion (bypassed for highlighted packages)
MIN_DOWNLOADS = 100_000

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
    p["js_exists"] = bool(p.get("js")) and p.get("js") != "n/a"

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
            # I don't think we'll hit this case since we filter them out?
            p["package_url"] = f"https://reference.langchain.com/python/{p['name']}/"
        else:
            # Integration
            p["package_url"] = (
                "https://reference.langchain.com/python/integrations"
                f"/{p['name'].replace('-', '_')}/"
            )
    else:  # Third-party
        p["package_url"] = f"https://pypi.org/project/{p['name']}/"

    return p


PACKAGES_N = [_enrich_package(p) for p in PACKAGE_YML["packages"]]
PACKAGES = [p for p in PACKAGES_N if p is not None]

# Filter out packages with downloads less than MIN_DOWNLOADS
# unless they are highlighted (bypass filter for highlighted packages)
PACKAGES = [
    p
    for p in PACKAGES
    if p.get("highlight", False) or p.get("downloads", 0) >= MIN_DOWNLOADS
]

# Sort by highlight status (highlighted first), then by downloads
PACKAGES_SORTED = sorted(
    PACKAGES,
    key=lambda p: (not p.get("highlight", False), -p.get("downloads", 0)),
)

# Truncate to top 50 by total downloads
PACKAGES_SORTED = PACKAGES_SORTED[:50]


def package_row(p: dict) -> str:
    """Generate a markdown table row for a package."""
    js_value = p.get("js")
    if js_value and js_value != "n/a":
        js = f"[✅](https://www.npmjs.com/package/{js_value})"
    elif js_value == "n/a":
        js = "N/A"
    else:
        js = "❌"
    link = p["provider_page"]
    title = p["name_title"]
    provider = f"[{title}]({link})" if link else title
    return (
        f"| {provider} "
        f"| [`{p['name']}`]({p['package_url']}) "
        f'| <a href="https://pypi.org/project/{p["name"]}/" target="_blank"><img src="https://static.pepy.tech/badge/{p["name"]}/month" alt="Downloads per month" noZoom class="rounded not-prose" /></a> '  # noqa: E501
        f'| <a href="https://pypi.org/project/{p["name"]}/" target="_blank"><img src="https://img.shields.io/pypi/v/{p["name"]}?style=flat-square&label=%20" alt="PyPI - Latest version" noZoom class="rounded not-prose" /></a> '  # noqa: E501
        f"| {js} |"
    )


def table() -> str:
    """Generate the full markdown table for all packages."""
    header = """| Provider | Package | Downloads | Latest version | <Tooltip tip="Whether an equivalent version exists in the TypeScript version of LangChain. Click the checkmark to visit the respective package.">JS/TS support</Tooltip> |
| :--- | :--- | :--- | :--- | :--- |
"""  # noqa: E501
    return header + "\n".join(package_row(p) for p in PACKAGES_SORTED)


def doc() -> str:
    return f"""\
---
title: LangChain integrations packages
sidebarTitle: LangChain integrations
mode: "wide"
---
{{/* File generated automatically by pipeline/tools/partner_pkg_table.py */}}
{{/* Do not manually edit */}}

LangChain offers an extensive ecosystem with 1000+ integrations across chat & embedding models, tools & toolkits, document loaders, vector stores, and more.

A **provider** is a third-party service or platform that LangChain integrates with to access AI capabilities like chat models, embeddings, and vector stores. These providers have standalone `langchain-provider` packages for improved versioning, dependency management, and testing.

<Columns cols={{3}}>
    <Card title="Chat models" icon="message" href="/oss/integrations/chat" arrow />
    <Card title="Embedding models" icon="layer-group" href="/oss/integrations/text_embedding" arrow />
    <Card title="Tools and toolkits" icon="screwdriver-wrench" href="/oss/integrations/tools" arrow />
</Columns>

To see a full list of integrations by component type, refer to the categories in the sidebar.

## Popular providers

{table()}

## All providers

[See all providers](/oss/integrations/providers/all_providers) or search for a provider using the search field.

Community integrations can be found in [`langchain-community`](https://github.com/langchain-ai/langchain-community).

<Info>
    If you'd like to contribute an integration, see the [contributing guide](/oss/contributing).
</Info>

"""  # noqa: E501


if __name__ == "__main__":
    output_dir = Path() / "src" / "oss" / "python" / "integrations" / "providers"
    with (output_dir / "overview.mdx").open("w") as f:
        f.write(doc())
