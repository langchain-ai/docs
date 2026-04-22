"""Generate MDX snippet files from Bluehawk-generated code snippet files.

Reads .snippet.*.py and .snippet.*.ts files from src/code-samples-generated/
and creates corresponding MDX files in src/snippets/code-samples/ for use in docs.

When a snippet uses a LangChain-style model argument (`model="…"` in Python or
`model: "…"` in TypeScript), the generated MDX can be wrapped in <CodeGroup> with the same
seven provider/model options as /oss/deepagents/quickstart (Google, OpenAI, Anthropic,
OpenRouter, Fireworks, Baseten, Ollama). Both `provider:model-id` and bare model names
(for example `claude-sonnet-4-5-20250929`) are recognized.

Snippets are left as a single fenced block when the model is already a non-Google
quickstart tab line, the bare name for one of those tabs (for example `claude-sonnet-4-6`),
or other known non-Deep-Agents cases (for example `gemini-2.5-flash-image` for the
Google Genai client API). The first model= / model: in the file that is not skipped
is the one that triggers expansion.

Run as part of `make code-snippets` after Bluehawk extraction.
"""

from __future__ import annotations

import re
from pathlib import Path

# Python: keyword argument model="…" (init_chat_model / create_deep_agent / etc.).
DEEPAGENTS_PY_MODEL_KWARG_RE = re.compile(r'\bmodel\s*=\s*"([^"]+)"')

# TypeScript: object property model: "…" (ChatAnthropic, createDeepAgent, …).
DEEPAGENTS_TS_MODEL_KWARG_RE = re.compile(r'\bmodel\s*:\s*"([^"]+)"')

# Tab title and full `model=` / `model:` token for each variant (matches
# src/oss/deepagents/quickstart.mdx Python tabs; JS uses google-genai spelling).
DEEPAGENTS_QUICKSTART_PY_MODEL_TABS: list[tuple[str, str]] = [
    ("Google", 'model="google_genai:gemini-3.1-pro-preview"'),
    ("OpenAI", 'model="openai:gpt-5.4"'),
    ("Anthropic", 'model="anthropic:claude-sonnet-4-6"'),
    ("OpenRouter", 'model="openrouter:anthropic/claude-sonnet-4-6"'),
    ("Fireworks", 'model="fireworks:accounts/fireworks/models/qwen3p5-397b-a17b"'),
    ("Baseten", 'model="baseten:zai-org/GLM-5"'),
    ("Ollama", 'model="ollama:devstral-2"'),
]

DEEPAGENTS_QUICKSTART_TS_MODEL_TABS: list[tuple[str, str]] = [
    ("Google", 'model: "google-genai:gemini-3.1-pro-preview"'),
    ("OpenAI", 'model: "openai:gpt-5.4"'),
    ("Anthropic", 'model: "anthropic:claude-sonnet-4-6"'),
    ("OpenRouter", 'model: "openrouter:anthropic/claude-sonnet-4-6"'),
    ("Fireworks", 'model: "fireworks:accounts/fireworks/models/qwen3p5-397b-a17b"'),
    ("Baseten", 'model: "baseten:zai-org/GLM-5"'),
    ("Ollama", 'model: "ollama:devstral-2"'),
]


def _model_id_from_py_tab_token(tab_token: str) -> str:
    m = re.match(r'model="([^"]+)"', tab_token)
    if not m:
        msg = f"expected model= tab token, got {tab_token!r}"
        raise ValueError(msg)
    return m.group(1)


def _model_id_from_ts_tab_token(tab_token: str) -> str:
    m = re.match(r'model:\s*"([^"]+)"', tab_token)
    if not m:
        msg = f"expected model: tab token, got {tab_token!r}"
        raise ValueError(msg)
    return m.group(1)


# If the snippet already uses one of these model IDs (non-Google quickstart tab),
# do not expand: the author chose that tab line verbatim.
DEEPAGENTS_PY_SKIP_EXPAND_MODEL_IDS: frozenset[str] = frozenset(
    _model_id_from_py_tab_token(token)
    for title, token in DEEPAGENTS_QUICKSTART_PY_MODEL_TABS
    if title != "Google"
)

DEEPAGENTS_TS_SKIP_EXPAND_MODEL_IDS: frozenset[str] = frozenset(
    _model_id_from_ts_tab_token(token)
    for title, token in DEEPAGENTS_QUICKSTART_TS_MODEL_TABS
    if title != "Google"
)


def _id_after_first_colon(tab_id: str) -> str:
    """For openai:gpt-5.4 return gpt-5.4; for bare ids return as-is."""
    if ":" not in tab_id:
        return tab_id
    return tab_id.split(":", 1)[1]


# Bare names that are not Deep Agents init lines (google.genai client, legacy tutorials).
DEEPAGENTS_PY_EXTRA_BARE_SKIP_EXPAND_MODEL_IDS: frozenset[str] = frozenset(
    {
        "gemini-2.5-flash-image",
        "claude-3-haiku-20240307",
    }
)
DEEPAGENTS_TS_EXTRA_BARE_SKIP_EXPAND_MODEL_IDS: frozenset[str] = frozenset(
    {
        "gemini-2.5-flash-image",
        "claude-3-haiku-20240307",
    }
)


def _should_skip_expand_py(model_id: str) -> bool:
    if ":" in model_id:
        return model_id in DEEPAGENTS_PY_SKIP_EXPAND_MODEL_IDS
    return model_id in DEEPAGENTS_PY_EXTRA_BARE_SKIP_EXPAND_MODEL_IDS


def _should_skip_expand_ts(model_id: str) -> bool:
    if ":" in model_id:
        return model_id in DEEPAGENTS_TS_SKIP_EXPAND_MODEL_IDS
    return model_id in DEEPAGENTS_TS_EXTRA_BARE_SKIP_EXPAND_MODEL_IDS


def _codegroup_fence(tab_title: str, fence_lang: str, code: str) -> str:
    """One fenced code block inside a <CodeGroup> (indent matches docs conventions)."""
    body = "\n".join("    " + line for line in code.splitlines())
    return "\n".join(
        [
            f"    ```{fence_lang} {tab_title}",
            body,
            "    ```",
        ]
    )


def _expand_to_deepagents_codegroup(
    content: str,
    *,
    canonical: str,
    tab_definitions: list[tuple[str, str]],
    fence_lang: str,
) -> str:
    """Wrap `content` in a CodeGroup, one tab per quickstart model variant."""
    parts = [
        _codegroup_fence(title, fence_lang, content.replace(canonical, model_token))
        for title, model_token in tab_definitions
    ]
    return "<CodeGroup>\n" + "\n\n".join(parts) + "\n</CodeGroup>\n"


def maybe_expand_deepagents_quickstart_codegroup(
    content: str,
    *,
    language: str,
    fence_lang: str,
) -> str | None:
    """If content uses a quickstart-expandable model= line, return CodeGroup MDX."""
    if language == "python":
        for m in DEEPAGENTS_PY_MODEL_KWARG_RE.finditer(content):
            if not _should_skip_expand_py(m.group(1)):
                return _expand_to_deepagents_codegroup(
                    content,
                    canonical=m.group(0),
                    tab_definitions=DEEPAGENTS_QUICKSTART_PY_MODEL_TABS,
                    fence_lang=fence_lang,
                )
        return None
    if language == "ts":
        for m in DEEPAGENTS_TS_MODEL_KWARG_RE.finditer(content):
            if not _should_skip_expand_ts(m.group(1)):
                return _expand_to_deepagents_codegroup(
                    content,
                    canonical=m.group(0),
                    tab_definitions=DEEPAGENTS_QUICKSTART_TS_MODEL_TABS,
                    fence_lang=fence_lang,
                )
        return None
    return None


def format_snippet_mdx(content: str, *, language: str, fence_lang: str) -> str:
    """Return final MDX body for a snippet file."""
    content = content.rstrip() + "\n"
    expanded = maybe_expand_deepagents_quickstart_codegroup(
        content, language=language, fence_lang=fence_lang
    )
    if expanded is not None:
        return expanded
    return f"```{fence_lang}\n{content.rstrip()}\n```\n"


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    generated_dir = repo_root / "src" / "code-samples-generated"
    snippets_dir = repo_root / "src" / "snippets" / "code-samples"

    if not generated_dir.exists():
        return

    snippets_dir.mkdir(parents=True, exist_ok=True)

    snippet_configs = [
        ("*.snippet.*.py", "python", "python"),
        ("*.snippet.*.ts", "ts", "ts"),
    ]

    lang_suffix = {"python": "-py", "ts": "-js"}

    for glob_pattern, language, fence_lang in snippet_configs:
        for snippet_file in generated_dir.glob(glob_pattern):
            snippet_name = ".".join(snippet_file.stem.split(".")[2:])
            expected_suffix = lang_suffix[language]
            if not snippet_name.endswith(expected_suffix):
                continue

            content = snippet_file.read_text(encoding="utf-8")
            mdx_content = format_snippet_mdx(
                content, language=language, fence_lang=fence_lang
            )
            mdx_path = snippets_dir / f"{snippet_name}.mdx"
            mdx_path.write_text(mdx_content, encoding="utf-8")
            print(f"Generated {mdx_path.relative_to(repo_root)}")


if __name__ == "__main__":
    main()
