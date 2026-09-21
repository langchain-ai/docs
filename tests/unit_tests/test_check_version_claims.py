"""Tests for the package version-claim checker.

The value of this checker rests entirely on routing a specifier to the right
registry, so most of these cases are drawn from real lines in `src/` that an
earlier, naiver version of the parser got wrong.
"""

from pathlib import Path

import pytest

from scripts import check_version_claims as checker


def only_claim(text: str, path: Path | None = None) -> checker.Claim:
    """Parse `text` and assert it holds exactly one specifier."""
    claims = checker.claims_in_text(text, path)
    assert len(claims) == 1, f"expected one claim, got {sorted(c.spec for c in claims)}"
    return next(iter(claims))


def test_scope_prefix_routes_to_npm() -> None:
    """An `@scope/` prefix is npm-only syntax."""
    claim = only_claim("Requires `@langchain/langgraph>=1.4.0`.")
    assert claim.ecosystem == checker.NPM
    assert claim.package == "@langchain/langgraph"
    assert claim.version == "1.4.0"


def test_extras_bracket_routes_to_pypi() -> None:
    """An extras bracket is PyPI-only syntax and outranks anything else."""
    claim = only_claim("This setup requires `langsmith[livekit]>=0.11.2`.")
    assert claim.ecosystem == checker.PYPI
    assert claim.package == "langsmith"


def test_trailing_sentence_period_is_not_part_of_the_version() -> None:
    """A specifier ending a sentence must not capture the period."""
    claim = only_claim("The MCP endpoint requires `langgraph-api>=0.2.3`.")
    assert claim.version == "0.2.3"


def test_fence_routes_bare_name() -> None:
    """`deepagents` is on both registries with divergent version lines."""
    python_side = only_claim(":::python\nRequires `deepagents>=0.5.0`.\n:::")
    js_side = only_claim(":::js\nRequires `deepagents>=1.9.0`.\n:::")
    assert python_side.ecosystem == checker.PYPI
    assert js_side.ecosystem == checker.NPM


def test_fence_closes_back_to_the_default() -> None:
    """A closing fence restores the page default for later specifiers."""
    text = ":::js\nRequires `deepagents>=1.9.0`.\n:::\nRequires `langchain>=1.1`."
    claims = {claim.spec: claim.ecosystem for claim in checker.claims_in_text(text)}
    assert claims == {
        "deepagents>=1.9.0": checker.NPM,
        "langchain>=1.1": checker.PYPI,
    }


def test_inline_labels_split_one_unfenced_line() -> None:
    """Pages name both SDKs on a single line outside any fence."""
    text = (
        "In `deepagents>=0.5.2` (Python) and `deepagents>=1.9.1` (TypeScript), "
        "namespace factories receive a Runtime directly."
    )
    claims = {claim.spec: claim.ecosystem for claim in checker.claims_in_text(text)}
    assert claims == {
        "deepagents>=0.5.2": checker.PYPI,
        "deepagents>=1.9.1": checker.NPM,
    }


def test_label_before_the_specifier_is_honored() -> None:
    """From src/langsmith/trace-with-openai-agents-sdk.mdx."""
    claim = only_claim("Requires JS SDK version `langsmith>=0.5.25`.")
    assert claim.ecosystem == checker.NPM


def test_the_nearest_label_wins_over_a_further_one() -> None:
    """A trailing label beats a leading one that sits further away."""
    text = "The JS SDK is separate; this needs `langsmith>=0.7.35` (Python)"
    assert only_claim(text).ecosystem == checker.PYPI


def test_a_label_beyond_the_window_is_a_different_clause() -> None:
    """A label far from the specifier belongs to another clause, so it is ignored."""
    text = "Use the JS SDK for browsers. " + "Filler text. " * 4 + "`langchain>=1.1`"
    assert only_claim(text).ecosystem == checker.PYPI


def test_path_routes_when_nothing_else_does() -> None:
    """A language directory in the path settles an otherwise bare specifier."""
    js_page = Path("src/oss/javascript/integrations/chat/openai.mdx")
    py_page = Path("src/oss/python/integrations/chat/openai.mdx")
    assert only_claim("Requires `langchain>=1.1`.", js_page).ecosystem == checker.NPM
    assert only_claim("Requires `langchain>=1.1`.", py_page).ecosystem == checker.PYPI


def test_js_only_page_override() -> None:
    """A flat page documenting a JS-only SDK is routed by the override set."""
    page = Path("src/langsmith/trace-with-vercel-ai-sdk.mdx")
    assert only_claim("`wrapAISDK` requires `langsmith>=0.3.63`.", page).ecosystem == (
        checker.NPM
    )


def test_fence_outranks_the_page_path() -> None:
    """An explicit fence beats the directory a page happens to sit in."""
    page = Path("src/oss/javascript/integrations/chat/openai.mdx")
    claim = only_claim(":::python\nRequires `deepagents>=0.5.0`.\n:::", page)
    assert claim.ecosystem == checker.PYPI


def test_placeholder_examples_are_covered_by_the_ignore_file() -> None:
    """The "use your own package" example in local-dev-testing.mdx is exempted."""
    claim = only_claim('"dependencies": ["my-package==1.0.0"]')
    assert claim.spec in checker.load_ignores(checker.IGNORE_FILE)


def test_exact_pins_are_collected() -> None:
    """Exact `==` pins are checked too, not just floors."""
    claim = only_claim("for example `'[\"deepagents==0.1.5\"]'`.")
    assert claim.operator == "=="
    assert claim.spec == "deepagents==0.1.5"


def test_line_numbers_are_recorded_for_every_occurrence() -> None:
    """One specifier repeated on a page reports every line it appears on."""
    text = "Requires `langchain>=1.1`.\nfiller\nStill requires `langchain>=1.1`."
    claims = checker.claims_in_text(text)
    assert list(claims.values()) == [[1, 3]]


@pytest.mark.parametrize(
    ("version", "published", "expected"),
    [
        ("1.3.2", {"1.3.2", "1.4.0"}, True),
        ("1.5.9", {"1.3.2", "1.4.0"}, False),
        # Floors are often truncated to a series.
        ("0.7", {"0.7.14", "0.6.1"}, True),
        ("1.1", {"1.1.5"}, True),
        # A truncated floor must not match a longer number that merely starts
        # with the same digits.
        ("1.1", {"1.14.0"}, False),
    ],
)
def test_version_exists(version: str, published: set[str], *, expected: bool) -> None:
    """A version resolves only against a real release or its series."""
    assert checker.version_exists(version, published) is expected


def test_load_ignores_strips_comments(tmp_path: Path) -> None:
    """Comments and blank lines are stripped from the ignore file."""
    ignore = tmp_path / "ignore.txt"
    ignore.write_text(
        "# a heading\nopentelemetry-api>=0.0.1\n\nlangchain>=1.1  # trailing reason\n",
        encoding="utf-8",
    )
    assert checker.load_ignores(ignore) == {
        "opentelemetry-api>=0.0.1",
        "langchain>=1.1",
    }


def test_load_ignores_tolerates_a_missing_file(tmp_path: Path) -> None:
    """A missing ignore file means no exceptions, not an error."""
    assert checker.load_ignores(tmp_path / "nope.txt") == set()


def test_unsafe_package_names_are_never_looked_up(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A name that fails the allowlist must not reach the network."""

    def explode(url: str) -> object:
        message = f"should not have fetched {url}"
        raise AssertionError(message)

    monkeypatch.setattr(checker, "_fetch_json", explode)
    assert checker.fetch_releases(checker.PYPI, "../../etc/passwd") is None
    assert checker.fetch_releases(checker.NPM, "a/../b") is None


def test_lookup_failure_is_unresolved_not_a_bad_version(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A registry outage must not be reported as a nonexistent version."""

    def fail(url: str) -> object:
        raise TimeoutError

    monkeypatch.setattr(checker, "_fetch_json", fail)
    assert checker.fetch_releases(checker.PYPI, "langchain") is None


def test_fetch_releases_reads_pypi_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    """PyPI payloads yield the full release set and the latest version."""
    payload = {"releases": {"1.3.2": [], "1.4.0": []}, "info": {"version": "1.4.0"}}
    monkeypatch.setattr(checker, "_fetch_json", lambda url: payload)
    assert checker.fetch_releases(checker.PYPI, "langchain") == (
        {"1.3.2", "1.4.0"},
        "1.4.0",
    )


def test_fetch_releases_reads_npm_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    """An npm payload yields the version map and the `latest` dist-tag."""
    payload = {
        "versions": {"1.4.15": {}, "1.2.8": {}},
        "dist-tags": {"latest": "1.4.15"},
    }
    monkeypatch.setattr(checker, "_fetch_json", lambda url: payload)
    assert checker.fetch_releases(checker.NPM, "@langchain/langgraph") == (
        {"1.4.15", "1.2.8"},
        "1.4.15",
    )
