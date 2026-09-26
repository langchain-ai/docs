"""Tests for the code snippet MDX generator."""

import json
import re
from pathlib import Path

from scripts.generate_code_snippet_mdx import (
    maybe_expand_deepagents_quickstart_codegroup,
)

TAB_COUNT = 7

CODE_SAMPLES = Path(__file__).resolve().parent.parent.parent / "src" / "code-samples"

# First @langchain/google release that sets tool_config.includeServerSideTool-
# Invocations when built-in and function tools are mixed. Older versions send no
# tool_config, and Gemini rejects the request.
GOOGLE_TOOL_CONFIG_MIN = (0, 2, 6)


def _version_tuple(raw: str) -> tuple[int, ...]:
    """Parse a semver-ish version into a comparable tuple, ignoring range chars.

    Deliberately stdlib-only: `packaging` is not a declared project dependency,
    so importing it here would rely on a transitive install.
    """
    cleaned = raw.strip().lstrip("^~>=< ")
    match = re.match(r"(\d+)(?:\.(\d+))?(?:\.(\d+))?", cleaned)
    assert match is not None, f"cannot parse version {raw!r}"
    return tuple(int(part) if part else 0 for part in match.groups())


PY_RAG_SAMPLE = """embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
agent = create_agent(model="anthropic:claude-sonnet-5", tools=tools)
"""

TS_RAG_SAMPLE = """const embeddings = new OpenAIEmbeddings({ model: "text-embedding-3-small" });
const agent = createAgent({ model: "anthropic:claude-sonnet-5", tools });
"""

PY_KEEP_SAMPLE = """# KEEP MODEL
agent = create_agent(model="anthropic:claude-sonnet-5", tools=tools)
"""


def test_embeddings_model_is_not_expanded_python() -> None:
    """A RAG sample varies its chat model, never its embeddings model."""
    expanded, _ = maybe_expand_deepagents_quickstart_codegroup(
        PY_RAG_SAMPLE, language="python", fence_lang="python"
    )
    assert expanded is not None
    # The embeddings model survives untouched in every tab.
    embeddings_call = 'OpenAIEmbeddings(model="text-embedding-3-small")'
    assert expanded.count(embeddings_call) == TAB_COUNT
    # The chat model is the one each tab varies.
    assert 'create_agent(model="openai:gpt-5.5"' in expanded
    assert 'create_agent(model="google_genai:gemini-3.6-flash"' in expanded


def test_embeddings_model_is_not_expanded_typescript() -> None:
    """The TypeScript property form is recognized the same way."""
    expanded, _ = maybe_expand_deepagents_quickstart_codegroup(
        TS_RAG_SAMPLE, language="ts", fence_lang="typescript"
    )
    assert expanded is not None
    embeddings_call = 'new OpenAIEmbeddings({ model: "text-embedding-3-small" })'
    assert expanded.count(embeddings_call) == TAB_COUNT
    assert 'createAgent({ model: "openai:gpt-5.5"' in expanded
    # The Google tab routes to @langchain/google, whose provider key is "google".
    # Python has no equivalent key and stays on "google_genai" (see the
    # python test above), so the two tables intentionally differ.
    assert 'createAgent({ model: "google:gemini-3.6-flash"' in expanded
    # @langchain/google-genai is long-term support only. Its key must not leak
    # back into TypeScript output.
    assert "google-genai:" not in expanded


def test_provider_specific_chat_class_is_not_expanded() -> None:
    """`ChatOpenAI` takes a bare OpenAI ID, so no tab may rewrite it."""
    expanded, stripped = maybe_expand_deepagents_quickstart_codegroup(
        'model = ChatOpenAI(model="gpt-4o-mini")\n',
        language="python",
        fence_lang="python",
    )
    # Nothing routable to vary, so the snippet stays a single fenced block
    # rather than offering six tabs of code that cannot run.
    assert expanded is None
    assert 'ChatOpenAI(model="gpt-4o-mini")' in stripped


def test_embeddings_only_sample_is_left_alone() -> None:
    """A sample with no chat model produces no CodeGroup."""
    expanded, stripped = maybe_expand_deepagents_quickstart_codegroup(
        'embeddings = OpenAIEmbeddings(model="text-embedding-3-small")\n',
        language="python",
        fence_lang="python",
    )
    assert expanded is None
    assert "text-embedding-3-small" in stripped


def test_typescript_samples_use_camel_case_google_search() -> None:
    """@langchain/google only accepts the camelCase built-in search key.

    The legacy @langchain/google-genai spelling is `google_search`. Passing that
    to @langchain/google misses its built-in tool allowlist, falls through to
    the function-declaration converter, and throws InvalidToolError before any
    request is sent. The Python SDK does accept the snake_case key, so this
    check is TypeScript-only.
    """
    offenders = [
        path.relative_to(CODE_SAMPLES).as_posix()
        for path in sorted(CODE_SAMPLES.rglob("*.ts"))
        if "node_modules" not in path.parts and "google_search" in path.read_text()
    ]
    assert offenders == [], (
        "TypeScript samples must use { googleSearch: {} }; the snake_case "
        f"google_search key is legacy-only and fails before any request is "
        f"sent. Offending files: {offenders}"
    )


def test_typescript_samples_pin_a_google_version_that_sends_tool_config() -> None:
    """Built-in tools mixed with function tools need @langchain/google 0.2.6+.

    Gemini rejects the request with "Please enable
    tool_config.include_server_side_tool_invocations to use Built-in tools with
    Function calling" unless that flag is set. @langchain/google first sets it in
    0.2.6, so an older resolved version silently breaks the search-tool sample
    even though the provider string and tool key are both correct.
    """
    package_json = json.loads((CODE_SAMPLES / "package.json").read_text())
    declared = package_json["dependencies"]["@langchain/google"]
    assert _version_tuple(declared) >= GOOGLE_TOOL_CONFIG_MIN, (
        f"@langchain/google {declared} predates the tool_config fix; "
        f"need {'.'.join(str(p) for p in GOOGLE_TOOL_CONFIG_MIN)} or later"
    )

    lockfile = (CODE_SAMPLES / "package-lock.json").read_text()
    resolved = re.search(
        r'"node_modules/@langchain/google":\s*\{[^}]*?"version":\s*"([^"]+)"',
        lockfile,
        re.DOTALL,
    )
    assert resolved is not None, "lockfile no longer pins @langchain/google"
    # The declared range already permitted a fixed version, so a stale lockfile
    # is the failure mode that actually reaches the sample runner.
    assert _version_tuple(resolved.group(1)) >= GOOGLE_TOOL_CONFIG_MIN, (
        f"lockfile resolves @langchain/google to {resolved.group(1)}, which "
        "predates the tool_config fix"
    )


def test_keep_model_marker_still_pins_the_next_model() -> None:
    """The new check runs after the marker, so marker behavior is unchanged."""
    expanded, stripped = maybe_expand_deepagents_quickstart_codegroup(
        PY_KEEP_SAMPLE, language="python", fence_lang="python"
    )
    assert expanded is None
    assert "# KEEP MODEL" not in stripped
    assert 'model="anthropic:claude-sonnet-5"' in stripped
