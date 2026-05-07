"""Tests for the UTM link preprocessor."""

from pathlib import Path

import pytest

from pipeline.preprocessors.utm_links import (
    _file_path_to_utm_content,
    _is_cta_url,
    add_utm_to_cta_links,
)


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://smith.langchain.com", True),
        ("https://smith.langchain.com/", True),
        ("https://smith.langchain.com/agents", True),
        ("https://smith.langchain.com/agents?skipOnboarding=true", True),
        ("https://smith.langchain.com/settings", False),
        ("https://smith.langchain.com/hub", False),
        ("https://smith.langchain.com/projects", False),
        ("https://smith.langchain.com/public/abc123/r", False),
        ("https://smith.langchain.com/studio", False),
    ],
)
def test_is_cta_url(url: str, expected: bool) -> None:
    assert _is_cta_url(url) is expected


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("src/langsmith/home.mdx", "langsmith-home"),
        ("src/index.mdx", "index"),
        ("src/oss/langgraph/overview.mdx", "oss-langgraph-overview"),
        ("src/snippets/oss/studio-py.mdx", "snippets-oss-studio-py"),
        ("src/langsmith/fleet/index.mdx", "langsmith-fleet-index"),
    ],
)
def test_file_path_to_utm_content(path: str, expected: str) -> None:
    assert _file_path_to_utm_content(Path(path)) == expected


class TestAddUtmToCTALinks:
    fp = Path("src/langsmith/home.mdx")

    def test_bare_cta_gets_utm(self) -> None:
        result = add_utm_to_cta_links("[LS](https://smith.langchain.com)\n", self.fp)
        assert "utm_source=docs" in result
        assert "utm_content=langsmith-home" in result

    def test_trailing_slash_gets_utm(self) -> None:
        result = add_utm_to_cta_links("[LS](https://smith.langchain.com/)\n", self.fp)
        assert "utm_source=docs" in result

    def test_agents_gets_utm(self) -> None:
        result = add_utm_to_cta_links("[Fleet](https://smith.langchain.com/agents)\n", self.fp)
        assert "utm_source=docs" in result

    def test_existing_query_preserved(self) -> None:
        result = add_utm_to_cta_links(
            "[LS](https://smith.langchain.com/agents?skipOnboarding=true)\n", self.fp
        )
        assert "skipOnboarding=true" in result
        assert "utm_source=docs" in result

    def test_functional_link_untouched(self) -> None:
        md = "[Settings](https://smith.langchain.com/settings)\n"
        assert add_utm_to_cta_links(md, self.fp) == md

    def test_deep_link_untouched(self) -> None:
        md = "[Trace](https://smith.langchain.com/public/abc/r)\n"
        assert add_utm_to_cta_links(md, self.fp) == md

    def test_code_block_skipped(self) -> None:
        md = "```\n[LS](https://smith.langchain.com)\n```\n"
        assert "utm_source" not in add_utm_to_cta_links(md, self.fp)

    def test_tilde_fence_skipped(self) -> None:
        md = "~~~\n[LS](https://smith.langchain.com)\n~~~\n"
        assert "utm_source" not in add_utm_to_cta_links(md, self.fp)

    def test_non_smith_link_untouched(self) -> None:
        md = "[Google](https://google.com)\n"
        assert add_utm_to_cta_links(md, self.fp) == md

    def test_api_domain_untouched(self) -> None:
        md = "[API](https://api.smith.langchain.com/redoc)\n"
        assert add_utm_to_cta_links(md, self.fp) == md

    def test_mixed_links_only_cta_tagged(self) -> None:
        md = "[A](https://smith.langchain.com) and [B](https://smith.langchain.com/settings)\n"
        result = add_utm_to_cta_links(md, self.fp)
        assert result.count("utm_source") == 1

    def test_no_links_unchanged(self) -> None:
        md = "# Heading\n\nSome text.\n"
        assert add_utm_to_cta_links(md, self.fp) == md
