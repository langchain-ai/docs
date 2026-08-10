"""Tests for docs_url scheme validation in refresh_integration_downloads."""

from __future__ import annotations

import pytest

from scripts.refresh_integration_downloads import (
    IntegrationRow,
    _escape_cell,
    _is_safe_docs_url,
    _model_link,
    _normalize_docs_url,
    _normalize_prose,
    _row_from_integration_dict,
    validate_external_docs_urls,
)


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://example.com/docs", True),
        ("http://example.com/docs", True),
        ("HTTPS://EXAMPLE.COM/DOCS", True),
        ("/oss/integrations/chat/openai", True),
        ("  https://example.com  ", True),
        ("javascript:alert(1)", False),
        ("JAVASCRIPT:alert(1)", False),
        ("data:text/html,<script>alert(1)</script>", False),
        ("//evil.example/path", False),
        ("vbscript:msgbox(1)", False),
        ("", False),
        ("   ", False),
    ],
)
def test_is_safe_docs_url(url: str, expected: bool) -> None:
    assert _is_safe_docs_url(url) is expected


def test_normalize_docs_url_rejects_unsafe() -> None:
    assert _normalize_docs_url("javascript:alert(1)", label="Evil") is None
    assert (
        _normalize_docs_url("https://docs.example.com/", label="Safe")
        == "https://docs.example.com/"
    )


def test_row_from_integration_dict_drops_unsafe_docs_url() -> None:
    row = _row_from_integration_dict(
        rel_path="chat/evil",
        integration={
            "name": "EvilIntegration",
            "docs_url": "javascript:alert(1)",
        },
        language="python",
        package_cache={},
    )
    assert row is not None
    assert row.docs_url is None


def test_model_link_never_emits_unsafe_href() -> None:
    row = IntegrationRow(
        rel_path="chat/evil",
        name="EvilIntegration",
        package=None,
        registry=None,
        downloads=None,
        featured=False,
        deprecated=False,
        stream=None,
        tool_calling=None,
        structured_output=None,
        multimodal=None,
        docs_url="javascript:alert(1)",
    )
    assert _model_link(row) == "[`EvilIntegration`](/oss/integrations/chat/evil)"


def test_validate_external_docs_urls_flags_unsafe() -> None:
    data = {
        "python": {
            "chat": [
                {
                    "name": "SafeChat",
                    "docs_url": "https://example.com/",
                },
                {
                    "name": "EvilChat",
                    "docs_url": "javascript:alert(1)",
                },
            ]
        }
    }
    errors = validate_external_docs_urls(data)
    assert len(errors) == 1
    assert "EvilChat" in errors[0]
    assert "javascript:alert(1)" in errors[0]


def test_validate_external_docs_urls_accepts_repo_yaml() -> None:
    assert validate_external_docs_urls() == []


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("guardrails — prompt", "guardrails—prompt"),
        ("use — the agent", "use—the agent"),
        ("a–b", "a–b"),
        ("plain text", "plain text"),
    ],
)
def test_normalize_prose_removes_dash_spaces(text: str, expected: str) -> None:
    assert _normalize_prose(text) == expected


def test_escape_cell_normalizes_dashes_and_pipes() -> None:
    assert _escape_cell("a — b | c") == "a—b \\| c"
