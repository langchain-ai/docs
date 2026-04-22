"""Generate MDX snippet files from Bluehawk-generated code snippet files.

Reads .snippet.*.py and .snippet.*.ts files from src/code-samples-generated/
and creates corresponding MDX files in src/snippets/code-samples/ for use in docs.

When a snippet uses a LangChain-style model argument (`model="…"` in Python or
`model: "…"` in TypeScript), the generated MDX can be wrapped in <CodeGroup> with the same
seven provider/model options as /oss/deepagents/quickstart (Google, OpenAI, Anthropic,
OpenRouter, Fireworks, Baseten, Ollama). Both `provider:model-id` and bare model names
(for example `claude-sonnet-4-5-20250929`) are recognized.

Snippets are left as a single fenced block when no model argument is found, or when all
model arguments are marked to keep.

To keep a specific model line:

- In Python, put `# KEEP MODEL` on the line immediately before the `model="..."` line.
- In TypeScript, put `// KEEP MODEL` on the line immediately before the `model: "..."` line.

The marker line is stripped during processing and that model occurrence is not
replaced/expanded.

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


DEEPAGENTS_PY_SKIP_EXPAND_MODEL_IDS: frozenset[str] = frozenset()
DEEPAGENTS_TS_SKIP_EXPAND_MODEL_IDS: frozenset[str] = frozenset()


def _id_after_first_colon(tab_id: str) -> str:
    """For openai:gpt-5.4 return gpt-5.4; for bare ids return as-is."""
    if ":" not in tab_id:
        return tab_id
    return tab_id.split(":", 1)[1]


KEEP_MODEL_MARKER_PY = "# KEEP MODEL"
KEEP_MODEL_MARKER_TS = "// KEEP MODEL"


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


def _replace_span(text: str, start: int, end: int, replacement: str) -> str:
    return text[:start] + replacement + text[end:]


def _expand_to_deepagents_codegroup(
    content: str,
    *,
    canonical_span: tuple[int, int],
    tab_definitions: list[tuple[str, str]],
    fence_lang: str,
) -> str:
    """Wrap `content` in a CodeGroup, one tab per quickstart model variant."""
    start, end = canonical_span
    parts = [
        _codegroup_fence(
            title, fence_lang, _replace_span(content, start, end, model_token)
        )
        for title, model_token in tab_definitions
    ]
    return "<CodeGroup>\n" + "\n\n".join(parts) + "\n</CodeGroup>\n"


def maybe_expand_deepagents_quickstart_codegroup(
    content: str,
    *,
    language: str,
    fence_lang: str,
) -> tuple[str | None, str]:
    """Return (expanded_mdx_or_none, content_with_keep_markers_stripped)."""
    model_re: re.Pattern[str]
    tab_definitions: list[tuple[str, str]]
    keep_marker: str
    if language == "python":
        model_re = DEEPAGENTS_PY_MODEL_KWARG_RE
        tab_definitions = DEEPAGENTS_QUICKSTART_PY_MODEL_TABS
        keep_marker = KEEP_MODEL_MARKER_PY
    elif language == "ts":
        model_re = DEEPAGENTS_TS_MODEL_KWARG_RE
        tab_definitions = DEEPAGENTS_QUICKSTART_TS_MODEL_TABS
        keep_marker = KEEP_MODEL_MARKER_TS
    else:
        return None, content

    # Strip marker lines while recording which model occurrence to expand.
    out_lines: list[str] = []
    keep_next_model = False
    canonical_span: tuple[int, int] | None = None

    for line in content.splitlines(keepends=True):
        if line.strip() == keep_marker:
            keep_next_model = True
            continue

        out_offset = sum(len(l) for l in out_lines)
        m = model_re.search(line)
        if m is not None:
            if keep_next_model:
                keep_next_model = False
            elif canonical_span is None:
                canonical_span = (out_offset + m.start(), out_offset + m.end())

        out_lines.append(line)

    stripped = "".join(out_lines)
    if canonical_span is None:
        return None, stripped

    return (
        _expand_to_deepagents_codegroup(
            stripped,
            canonical_span=canonical_span,
            tab_definitions=tab_definitions,
            fence_lang=fence_lang,
        ),
        stripped,
    )


def format_snippet_mdx(content: str, *, language: str, fence_lang: str) -> str:
    """Return final MDX body for a snippet file."""
    content = content.rstrip() + "\n"
    expanded, content = maybe_expand_deepagents_quickstart_codegroup(
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
