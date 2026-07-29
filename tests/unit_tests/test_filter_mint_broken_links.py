"""Tests for scripts/filter_mint_broken_links.py."""

from scripts.filter_mint_broken_links import (
    filter_broken_links,
    is_cross_language_snippet,
)


def test_is_cross_language_snippet() -> None:
    assert is_cross_language_snippet(
        "snippets/javascript/oss/python-chat-downloads.mdx"
    )
    assert is_cross_language_snippet(
        "snippets/python/oss/javascript-chat-downloads.mdx"
    )
    assert is_cross_language_snippet("snippets/oss/javascript-chat-downloads.mdx")
    assert not is_cross_language_snippet(
        "snippets/python/oss/python-chat-downloads.mdx"
    )
    assert not is_cross_language_snippet(
        "snippets/javascript/oss/javascript-chat-downloads.mdx"
    )
    assert not is_cross_language_snippet(
        "snippets/python/oss/requires-langgraph-server.mdx"
    )
    assert not is_cross_language_snippet(
        "snippets/javascript/oss/requires-langgraph-server.mdx"
    )
    assert not is_cross_language_snippet("oss/python/langchain/frontend/time-travel.mdx")


def test_drops_cross_language_snippets_keeps_matching_and_real_failures() -> None:
    raw = """found 4 broken links in 4 files

langsmith/api-ref-control-plane.mdx

snippets/javascript/oss/python-chat-downloads.mdx
 ⎿  /oss/javascript/integrations/chat/vllm

snippets/python/oss/python-chat-downloads.mdx
 ⎿  /oss/python/integrations/chat/typo-missing

oss/python/langchain/frontend/time-travel.mdx
 ⎿  /oss/python/langgraph/missing-page
"""
    filtered = filter_broken_links(raw)
    assert "snippets/javascript/oss/python-chat-downloads.mdx" not in filtered
    assert "/oss/javascript/integrations/chat/vllm" not in filtered
    assert "snippets/python/oss/python-chat-downloads.mdx" in filtered
    assert "/oss/python/integrations/chat/typo-missing" in filtered
    assert "langsmith/api-ref-control-plane.mdx" in filtered
    assert "/oss/python/langgraph/missing-page" in filtered


def test_check_anchors_filters_smithdb_false_positives() -> None:
    raw = """page.mdx
 ⎿  /langsmith/smithdb-sdk-migration#traces-query
 ⎿  /langsmith/smithdb-sdk-migration#real-anchor
"""
    filtered = filter_broken_links(raw, check_anchors=True)
    assert "traces-query" not in filtered
    assert "real-anchor" in filtered


def test_excludes_openapi_and_legacy_relative_paths() -> None:
    raw = """page.mdx
 ⎿  /langsmith/agent-server-api/foo
 ⎿  ../integrations/chat/openai
 ⎿  /oss/python/langchain/tools
"""
    filtered = filter_broken_links(raw)
    assert "agent-server-api" not in filtered
    assert "../integrations/" not in filtered
    assert "/oss/python/langchain/tools" in filtered
