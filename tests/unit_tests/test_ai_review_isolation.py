"""Tests for the pieces that keep credentials away from the AI review agent."""

import base64
import binascii
import json
from pathlib import Path

import pytest

from scripts.ai_review_gh_read import main as gh_read_main
from scripts.ai_review_gh_read import validate
from scripts.ai_review_post import find_secret, main
from scripts.ai_review_proxy import make_handler, outbound_headers, parse_headers

FAKE_TOKEN = "ghp_" + "FAKEfake" * 4 + "1234"  # built, so scanners do not flag the file
PLAIN = "a8f3k2m9q7w1z5x0c4v6b2n8"  # no token shape, so only value matching finds it


@pytest.mark.parametrize(
    "path",
    [
        "repos/langchain-ai/langchain/git/trees/HEAD?recursive=1",
        "/repos/langchain-ai/langchainplus/contents/smith-backend/app/config.py?ref=main",
        "repos/langchain-ai/deepagents/compare/deepagents==0.7.29...deepagents==0.7.30",
        "repos/langchain-ai/helm/releases/latest",
        "repos/langchain-ai/docs/pulls/6973/files",
        "repos/langchain-ai/langgraph-api/commits?path=api/x.py&per_page=5",
    ],
)
def test_gh_read_allows_source_reads(path: str) -> None:
    """Reads of langchain-ai repository source are allowed."""
    assert validate(path) is not None


@pytest.mark.parametrize(
    "path",
    [
        "user",
        "repos/evil/langchain/contents/x",
        "repos/langchain-ai/docs/actions/secrets",
        "repos/langchain-ai/docs/contents/../../user",
        "https://evil.example/repos/langchain-ai/docs",
        "//evil.example/repos/langchain-ai/docs/tags",
        "repos/langchain-ai/docs/tags --hostname evil.example",
        "repos/langchain-ai/docs/issues/1/comments",
        "graphql",
        "",
    ],
)
def test_gh_read_blocks_everything_else(path: str) -> None:
    """Other hosts, other owners, writes, traversal, and flags are refused."""
    assert validate(path) is None


def test_gh_read_main_rejects_extra_arguments(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Only one path and --raw are accepted, so no flag reaches the request."""
    assert gh_read_main(["repos/langchain-ai/docs/tags", "--hostname", "evil"]) == 2
    assert "usage" in capsys.readouterr().err


def test_proxy_replaces_client_auth_with_real_key() -> None:
    """The placeholder key never reaches the gateway; the real one is added."""
    custom = parse_headers("X-Gateway-Tenant: docs\nX-Other: 1\nnot a header")
    out = outbound_headers(
        {
            "x-api-key": "held-by-proxy",
            "Authorization": "Bearer x",
            "Host": "127.0.0.1",
            "anthropic-version": "1",
        },
        api_key="real",
        custom=custom,
    )
    assert out["x-api-key"] == "real"
    assert "Authorization" not in out
    assert "Host" not in out
    assert out["X-Gateway-Tenant"] == "docs"
    assert out["anthropic-version"] == "1"


def test_proxy_requires_https_upstream() -> None:
    """The proxy refuses to send credentials over plain HTTP."""
    with pytest.raises(ValueError, match="https"):
        make_handler("http://gateway.example", "k", {})


@pytest.mark.parametrize(
    "encode",
    [
        lambda s: s,
        lambda s: s[::-1],
        lambda s: binascii.hexlify(s.encode()).decode(),
        lambda s: base64.b64encode(s.encode()).decode(),
        lambda s: base64.b64encode(b"x" + s.encode() + b"yz").decode(),
        lambda s: base64.urlsafe_b64encode(b"ab" + s.encode()).decode(),
        lambda s: " ".join(s[i : i + 4] for i in range(0, len(s), 4)),
    ],
)
def test_find_secret_sees_common_encodings(encode) -> None:  # noqa: ANN001
    """A secret is found literal, reversed, hex, spaced, or base64 at any offset."""
    assert find_secret(f"summary: {encode(PLAIN)} end", [PLAIN])


def test_find_secret_sees_token_shapes_without_values() -> None:
    """Credential shapes are caught even when the value is not known."""
    assert find_secret(f"leaked {FAKE_TOKEN}", [])
    assert not find_secret("The default is `zstandard`, not `gzip`.", [PLAIN])


def test_sanitize_withholds_everything_on_a_hit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """One leaked value withholds all three passes and fails the step."""
    raw, out = tmp_path / "raw", tmp_path / "out"
    raw.mkdir()
    finding = {
        "file": "src/a.mdx",
        "line": 1,
        "severity": "minor",
        "fix_class": "suggest",
    }
    (raw / "docs-review.json").write_text(
        json.dumps({"findings": [{**finding, "summary": "ok"}]})
    )
    (raw / "docs-team-voice.json").write_text(
        json.dumps(
            {
                "findings": [
                    {**finding, "summary": base64.b64encode(PLAIN.encode()).decode()}
                ]
            }
        )
    )
    monkeypatch.setenv("AI_REVIEW_SECRETS", f"X-Gateway-Key: {PLAIN}\n")
    monkeypatch.setattr(
        "scripts.ai_review_post.read_diff",
        lambda base, head: None,
    )
    code = main(
        [
            "sanitize",
            "--input",
            str(raw),
            "--output",
            str(out),
            "--base",
            "a" * 40,
            "--head",
            "b" * 40,
        ]
    )
    assert code == 1
    for name in ("docs-review", "verify-against-source", "docs-team-voice"):
        data = json.loads((out / f"{name}.json").read_text())
        assert data["withheld"] is True
        assert data["findings"] == []
