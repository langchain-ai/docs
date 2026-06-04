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
PACKAGE_YML = Path() / "packages.yml"

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


def _is_integration(p: dict) -> bool:
    return p.get("integration", True) not in (False, "false", "False")


def pypi_url(package_name: str) -> str:
    return f"https://pypi.org/project/{package_name}/"


def reference_url(p: dict) -> str | None:
    if p["type"] not in ("monorepo", "langchain-org") and not p.get(
        "has_reference_docs"
    ):
        return None

    if not _is_integration(p):
        return f"https://reference.langchain.com/python/{p['name']}/"

    ref_doc_name = p["name"].replace("-", "_")
    return f"https://reference.langchain.com/python/integrations/{ref_doc_name}/"


def package_url(p: dict) -> str:
    return reference_url(p) or pypi_url(p["name"])


def npm_url(p: dict) -> str | None:
    js_package = p.get("js")
    if js_package and js_package != "n/a":
        return f"https://www.npmjs.com/package/{js_package}"
    return None


def downloads_badge(package_name: str) -> str:
    url = pypi_url(package_name)
    img = f"https://static.pepy.tech/badge/{package_name}/month"
    return (
        f'<a href="{url}" target="_blank"><img src="{img}" '
        'alt="Downloads per month" noZoom class="rounded not-prose" /></a>'
    )


def version_badge(package_name: str) -> str:
    url = pypi_url(package_name)
    img = f"https://img.shields.io/pypi/v/{package_name}?style=flat-square&label=%20"
    return (
        f'<a href="{url}" target="_blank"><img src="{img}" '
        'alt="PyPI - Latest version" noZoom class="rounded not-prose" /></a>'
    )


def js_support(p: dict) -> str:
    js_value = p.get("js")
    if url := npm_url(p):
        return f"[✅]({url})"
    if js_value == "n/a":
        return "N/A"
    return "❌"


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

    if p.get("has_reference_docs") and not _is_integration(p):
        msg = (
            f"{p['name']}: has_reference_docs=true and integration=false "
            "is not a supported combination"
        )
        raise ValueError(msg)

    p["package_url"] = package_url(p)

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
    link = p["provider_page"]
    title = p["name_title"]
    provider = f"[{title}]({link})" if link else title
    package_name = p["name"]
    return (
        f"| {provider} "
        f"| [`{package_name}`]({p['package_url']}) "
        f"| {downloads_badge(package_name)} "
        f"| {version_badge(package_name)} "
        f"| {js_support(p)} |"
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
title: "LangChain Python integrations"
sidebarTitle: "LangChain integrations"
mode: "wide"
description: "Integrate with providers using LangChain Python."
---
{{/* File generated automatically by pipeline/tools/partner_pkg_table.py */}}
{{/* Do not manually edit */}}

LangChain offers an extensive ecosystem with 1000+ integrations across chat & embedding models, tools & toolkits, document loaders, vector stores, and more.

A **provider** is a company or platform that hosts AI models and exposes them through an API (e.g., OpenAI, Anthropic, Google). Many providers have a dedicated `langchain-<provider>` package that implements one or more of LangChain's standard interfaces—chat models, embedding models, vector stores, and more—giving you a consistent API regardless of the underlying provider. Install the package, pick a model name, and swap providers without changing your code.

<Columns cols={{3}}>
    <Card title="Chat models" icon="message" href="/oss/integrations/chat" arrow />
    <Card title="Embedding models" icon="layers-difference" href="/oss/integrations/embeddings" arrow />
    <Card title="Tools and toolkits" icon="tool" href="/oss/integrations/tools" arrow />
    <Card title="Middleware" icon="arrows-shuffle" href="/oss/integrations/middleware" arrow />
    <Card title="Checkpointers" icon="database" href="/oss/integrations/checkpointers" arrow />
    <Card title="Sandboxes" icon="cube" href="/oss/integrations/sandboxes" arrow />
</Columns>

To see a full list of integrations by component type, refer to the categories in the sidebar.

<Tip>
    For a conceptual overview of how providers and models work in LangChain, including how to find model names, use new models immediately, and work with routers—see [Providers and models](/oss/concepts/providers-and-models).
</Tip>

## Popular providers

{table()}

## All providers

[See all providers](/oss/integrations/providers/all_providers) or search for a provider using the search field.

<Info>
    If you'd like to contribute an integration, see the [contributing guide](/oss/contributing).
</Info>

"""  # noqa: E501


if __name__ == "__main__":
    output_dir = Path() / "src" / "oss" / "python" / "integrations" / "providers"
    with (output_dir / "overview.mdx").open("w") as f:
        f.write(doc())
