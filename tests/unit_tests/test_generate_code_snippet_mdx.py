"""Tests for the code snippet MDX generator."""

from scripts.generate_code_snippet_mdx import (
    maybe_expand_deepagents_quickstart_codegroup,
)

TAB_COUNT = 7

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


def test_keep_model_marker_still_pins_the_next_model() -> None:
    """The new check runs after the marker, so marker behavior is unchanged."""
    expanded, stripped = maybe_expand_deepagents_quickstart_codegroup(
        PY_KEEP_SAMPLE, language="python", fence_lang="python"
    )
    assert expanded is None
    assert "# KEEP MODEL" not in stripped
    assert 'model="anthropic:claude-sonnet-5"' in stripped
