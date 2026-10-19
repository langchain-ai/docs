"""Unit tests for evidence and surgical-edit validation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.docs_edit import (  # noqa: E402
    extract_language_fences,
    line_churn_ratio,
    validate_docs_edits,
)
from tools.evidence import (  # noqa: E402
    ensure_evidence_in_body,
    format_evidence_markdown,
    parse_evidence_json,
)
from tools.github_prs import (  # noqa: E402
    parse_files_json,
    verify_old_content_matches_base,
)
from tools.releases import summarize_compare_files  # noqa: E402
from tools.source import claim_appears_in_source  # noqa: E402


def test_parse_evidence_requires_items() -> None:
    with pytest.raises(ValueError, match="evidence_json is required"):
        parse_evidence_json("")
    with pytest.raises(ValueError, match="items"):
        parse_evidence_json(
            json.dumps(
                {
                    "source_repo": "langchain-ai/deepagents",
                    "source_tag": "deepagents==0.7.24",
                    "items": [],
                }
            )
        )


def test_parse_evidence_accepts_symbol_or_quote() -> None:
    with pytest.raises(ValueError, match="symbol or quote"):
        parse_evidence_json(
            json.dumps(
                {
                    "source_repo": "langchain-ai/deepagents",
                    "source_tag": "deepagents==0.7.24",
                    "items": [{"path": "libs/foo.py"}],
                }
            )
        )

    evidence = parse_evidence_json(
        json.dumps(
            {
                "source_repo": "langchain-ai/deepagentsjs",
                "source_tag": "deepagents@1.14.2",
                "items": [
                    {
                        "path": "libs/deepagents/src/middleware/foo.ts",
                        "symbol": "offloadBinaryContent",
                    }
                ],
            }
        )
    )
    assert evidence["source_repo"] == "langchain-ai/deepagentsjs"
    assert evidence["items"][0]["symbol"] == "offloadBinaryContent"


def test_format_and_ensure_evidence_section() -> None:
    evidence = parse_evidence_json(
        json.dumps(
            {
                "source_repo": "langchain-ai/openwiki",
                "source_tag": "v0.7.0",
                "items": [{"path": "src/cli.ts", "symbol": "--provider"}],
            }
        )
    )
    section = format_evidence_markdown(evidence)
    assert "## Source evidence" in section
    assert "langchain-ai/openwiki" in section

    body = ensure_evidence_in_body("## Summary\n- docs change", evidence)
    assert body.count("## Source evidence") == 1
    again = ensure_evidence_in_body(body, evidence)
    assert again.count("## Source evidence") == 1


def test_parse_files_json_requires_old_content() -> None:
    with pytest.raises(ValueError, match="old_content"):
        parse_files_json(
            json.dumps(
                [
                    {
                        "path": "src/oss/deepagents/customization.mdx",
                        "new_content": "updated",
                    }
                ]
            )
        )


def test_parse_files_json_rejects_noop() -> None:
    with pytest.raises(ValueError, match="identical"):
        parse_files_json(
            json.dumps(
                [
                    {
                        "path": "src/oss/deepagents/customization.mdx",
                        "old_content": "same",
                        "new_content": "same",
                    }
                ]
            )
        )


def test_verify_old_content_matches_base() -> None:
    verify_old_content_matches_base("new.mdx", "", None)
    with pytest.raises(ValueError, match="empty string"):
        verify_old_content_matches_base("new.mdx", "not empty", None)

    verify_old_content_matches_base("page.mdx", "current", "current")
    with pytest.raises(ValueError, match="does not match"):
        verify_old_content_matches_base("page.mdx", "invented", "current")
    with pytest.raises(ValueError, match="already exists"):
        verify_old_content_matches_base("page.mdx", "", "current")


def test_claim_appears_in_source() -> None:
    content = "export function offloadBinaryContent() {\n  return true;\n}\n"
    assert claim_appears_in_source(content, symbol="offloadBinaryContent")
    assert claim_appears_in_source(
        content, quote="export function offloadBinaryContent()"
    )
    assert not claim_appears_in_source(content, symbol="InventedMiddleware")
    assert not claim_appears_in_source(content, quote="does not exist")


def test_summarize_compare_files_filters_prefixes() -> None:
    files = [
        {
            "filename": "libs/deepagents/src/foo.ts",
            "status": "modified",
            "additions": 1,
            "deletions": 0,
            "changes": 1,
            "patch": "+export const foo = 1;",
        },
        {
            "filename": "libs/acp/src/bar.ts",
            "status": "modified",
            "additions": 1,
            "deletions": 0,
            "changes": 1,
            "patch": "+export const bar = 1;",
        },
    ]
    filtered, stats = summarize_compare_files(
        files, source_path_prefixes=["libs/deepagents/"]
    )
    assert len(filtered) == 1
    assert filtered[0]["filename"] == "libs/deepagents/src/foo.ts"
    assert stats["file_count_skipped_outside_prefix"] == 1


def test_line_churn_and_fence_validation() -> None:
    old = "\n".join(f"line {i}" for i in range(20))
    surgical = old.replace("line 5", "line 5 changed")
    assert line_churn_ratio(old, surgical) < 0.35
    validate_docs_edits(
        [{"path": "page.mdx", "old_content": old, "new_content": surgical}],
        language_scope="js",
    )

    rewrite = "\n".join(f"new {i}" for i in range(20))
    with pytest.raises(ValueError, match="surgical-edit limit"):
        validate_docs_edits(
            [{"path": "page.mdx", "old_content": old, "new_content": rewrite}],
            language_scope="js",
        )

    page = (
        "intro\n"
        ":::python\n"
        "x = 1\n"
        ":::\n"
        ":::js\n"
        "const x = 1;\n"
        ":::\n"
    )
    bad_js_edit = page.replace("x = 1", "x = 2", 1)  # changes python fence first
    fences = extract_language_fences(page)
    assert fences["python"] == ["x = 1"]
    assert fences["js"] == ["const x = 1;"]
    with pytest.raises(ValueError, match=":::python"):
        validate_docs_edits(
            [{"path": "page.mdx", "old_content": page, "new_content": bad_js_edit}],
            language_scope="js",
        )
