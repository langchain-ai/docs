"""Tests for scripts/filter_mint_broken_links.py."""

from scripts.filter_mint_broken_links import filter_broken_links


def test_drops_snippet_sections_keeps_real_failures() -> None:
    raw = """found 3 broken links in 3 files

langsmith/api-ref-control-plane.mdx

snippets/javascript/oss/python-chat-downloads.mdx
 ⎿  /oss/javascript/integrations/chat/vllm

oss/python/langchain/frontend/time-travel.mdx
 ⎿  /oss/python/langgraph/missing-page
"""
    filtered = filter_broken_links(raw)
    assert "snippets/" not in filtered
    assert "/oss/javascript/integrations/chat/vllm" not in filtered
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
