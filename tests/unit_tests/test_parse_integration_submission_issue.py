"""Tests for scripts/parse_integration_submission_issue.py."""

from __future__ import annotations

from scripts.parse_integration_submission_issue import parse_issue_body

SAMPLE_BODY = """\
### Display or class name

ChatAcme

### Language

Python

### Component type

chat

### PyPI package name

langchain-acme

### npm package name

_No response_

### Docs URL

https://docs.acme.example/langchain

### Source repository

acme/langchain-acme

### Short provider description

Chat models for Acme.

### Capability flags (optional)

stream: true
tool_calling: true

### Confirmations

- [x] The package is already published on PyPI and/or npm.
"""


def test_parse_issue_body_success() -> None:
    result = parse_issue_body(SAMPLE_BODY)
    assert result["ok"] is True
    assert result["errors"] == []
    fields = result["fields"]
    assert fields["display_name"] == "ChatAcme"
    assert fields["language"] == "Python"
    assert fields["component"] == "chat"
    assert fields["pypi_package"] == "langchain-acme"
    assert fields["npm_package"] is None
    assert fields["docs_url"] == "https://docs.acme.example/langchain"
    assert fields["github_repo"] == "acme/langchain-acme"
    assert fields["provider_description"] == "Chat models for Acme."
    assert "stream: true" in (fields["capability_notes"] or "")
    assert fields["confirmations"] == [
        "The package is already published on PyPI and/or npm."
    ]


def test_parse_issue_body_requires_pypi_for_python() -> None:
    body = SAMPLE_BODY.replace("langchain-acme", "_No response_")
    result = parse_issue_body(body)
    assert result["ok"] is False
    assert any("PyPI package name" in error for error in result["errors"])
