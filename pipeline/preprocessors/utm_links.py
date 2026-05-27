"""Add UTM tracking to LangSmith CTA links at build time.

Tags conversion-oriented links (signup, Fleet onboarding) with UTM parameters.
Functional links (settings, hub, projects, traces) are left untouched.
"""

import re
from pathlib import Path
from urllib.parse import urlencode, urlparse, urlunparse

# Paths treated as CTAs. Everything else on smith.langchain.com is functional.
_CTA_PATHS = {"", "/", "/agents", "/agents/"}

_UTM_BASE = {
    "utm_source": "docs",
    "utm_medium": "cta",
    "utm_campaign": "langsmith-signup",
}

# Markdown links to smith.langchain.com: [text](url) or [text](url "title")
_MD_LINK_RE = re.compile(
    r"\[(?P<text>[^\]]*)\]"
    r"\((?P<url>https://smith\.langchain\.com[^)\s]*)(?:\s+\"[^\"]*\")?\)"
)

_CODE_FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")


def _file_path_to_utm_content(file_path: Path) -> str:
    """Derive utm_content from file path (e.g. src/langsmith/home.mdx -> langsmith-home)."""
    parts = file_path.with_suffix("").parts
    try:
        parts = parts[parts.index("src") + 1 :]
    except ValueError:
        pass
    return "-".join(parts) or "home"


def _is_cta_url(url: str) -> bool:
    """Return True if the URL is a signup/onboarding CTA."""
    return urlparse(url).path in _CTA_PATHS


def _add_utm(url: str, utm_content: str) -> str:
    """Append UTM query parameters, preserving existing params."""
    parsed = urlparse(url)
    sep = "&" if parsed.query else ""
    new_query = (
        parsed.query + sep + urlencode({**_UTM_BASE, "utm_content": utm_content})
    )
    return urlunparse(parsed._replace(query=new_query))


def add_utm_to_cta_links(content: str, file_path: Path) -> str:
    """Add UTM parameters to LangSmith CTA links, skipping code blocks."""
    utm_content = _file_path_to_utm_content(file_path)

    def _replace(match: re.Match[str]) -> str:
        url = match.group("url")
        if not _is_cta_url(url):
            return match.group(0)
        return match.group(0).replace(url, _add_utm(url, utm_content), 1)

    lines = content.splitlines(keepends=True)
    result: list[str] = []
    in_code_block = False

    for line in lines:
        if _CODE_FENCE_RE.match(line.strip()):
            in_code_block = not in_code_block
        result.append(line if in_code_block else _MD_LINK_RE.sub(_replace, line))

    return "".join(result)
