"""Generate MDX snippet files from extracted code snippet files.

Reads .snippet.*.py, .snippet.*.ts, .snippet.*.java, .snippet.*.kt, .snippet.*.go, and .snippet.*.sh files from src/code-samples-generated/
(produced by ``scripts/extract_code_snippets.py``, Bluehawk-compatible layout).
and creates corresponding MDX files in src/snippets/code-samples/ for use in docs.

When a snippet uses a LangChain-style model string, the generated MDX can be wrapped in
<CodeGroup> with the same seven provider/model options as /oss/deepagents/quickstart
(Google, OpenAI, Anthropic, OpenRouter, Fireworks, Baseten, Ollama). Recognized forms:

- Python: ``model="…"`` / ``model = "…"`` (kwargs or assignments)
- TypeScript: ``model: "…"`` (object properties) or ``model = "…"`` (assignments,
  including ``let model = "…"`` / ``const model = "…"``)

The quoted model ID is what gets swapped per tab, so assignment vs property syntax is
preserved. Every non-kept occurrence of that same ID in the snippet is updated together
(so a shared ``model = "…"`` plus later ``model`` references stay consistent).

Snippets are left as a single fenced block when no model string is found, or when all
model strings are marked to keep.

To keep a specific model line:

- In Python, put `# KEEP MODEL` on the line immediately before the `model="..."` line.
- In TypeScript, put `// KEEP MODEL` on the line immediately before the `model: "..."`
  or `model = "..."` line.

The marker line is stripped during processing and that model occurrence is not
replaced/expanded.

Run as part of `make code-snippets` after `extract_code_snippets.py`.

Optional **CodeGroup tab label** (Mintlify `` ```lang TabTitle``` `` inside ``<CodeGroup>``):

- Put as the **first line inside** the snippet body (after ``:snippet-start:``): ``# :codegroup-tab: Python`` or ``// :codegroup-tab: Java``. Stripped from emitted code.
- Optional **fence modifiers** (for example long samples): the **next** line after a tab marker, or the **first** line when there is no tab, can be ``# :codegroup-fence-mods: expandable wrap`` or ``// :codegroup-fence-mods: expandable wrap``. Stripped from emitted code. Omit for short snippets.
- The fence becomes e.g. `` ```java Java``, `` ```python expandable wrap`` (mods only), or `` ```java Java expandable wrap`` (tab + mods).
"""

from __future__ import annotations

import re
from pathlib import Path

# Optional prefix lines in extracted snippet body; stripped from output. See module docstring.
_CODEGROUP_TAB_MARKER_RE = re.compile(
    r"^\s*(?:#|//)\s*:codegroup-tab:\s*(.+?)\s*$",
)
_CODEGROUP_FENCE_MODS_RE = re.compile(
    r"^\s*(?:#|//)\s*:codegroup-fence-mods:\s*(.+?)\s*$",
)

# Python: keyword argument or assignment model="…" / model = "…".
DEEPAGENTS_PY_MODEL_KWARG_RE = re.compile(r'\bmodel\s*=\s*"([^"]+)"')

# TypeScript: object property model: "…" or assignment model = "…"
# (also matches let/const/var model = "…").
DEEPAGENTS_TS_MODEL_KWARG_RE = re.compile(r'\bmodel\s*(?::|=)\s*"([^"]+)"')

# Tab title and model ID for each variant (matches /oss/deepagents/quickstart;
# JS uses google-genai spelling).
DEEPAGENTS_QUICKSTART_PY_MODEL_TABS: list[tuple[str, str]] = [
    ("Google", "google_genai:gemini-3.6-flash"),
    ("OpenAI", "openai:gpt-5.5"),
    ("Anthropic", "anthropic:claude-sonnet-4-6"),
    ("OpenRouter", "openrouter:z-ai/glm-5.2"),
    ("Fireworks", "fireworks:accounts/fireworks/models/glm-5p2"),
    ("Baseten", "baseten:zai-org/GLM-5.2"),
    ("Ollama", "ollama:north-mini-code-1.0"),
]

DEEPAGENTS_QUICKSTART_TS_MODEL_TABS: list[tuple[str, str]] = [
    ("Google", "google-genai:gemini-3.6-flash"),
    ("OpenAI", "openai:gpt-5.5"),
    ("Anthropic", "anthropic:claude-sonnet-4-6"),
    ("OpenRouter", "openrouter:openrouter:z-ai/glm-5.2"),
    ("Fireworks", "fireworks:accounts/fireworks/models/glm-5p2"),
    ("Baseten", "baseten:zai-org/GLM-5.2"),
    ("Ollama", "ollama:north-mini-code-1.0"),
]


KEEP_MODEL_MARKER_PY = "# KEEP MODEL"
KEEP_MODEL_MARKER_TS = "// KEEP MODEL"


def _strip_codegroup_markers(content: str) -> tuple[str | None, str | None, str]:
    """Strip optional ``:codegroup-tab:`` and ``:codegroup-fence-mods:`` prefix lines.

    Returns ``(tab_title, fence_mods, rest)``. Tab is optional; fence-mods may follow a tab
    or appear alone as the first line (for standalone fenced blocks outside ``<CodeGroup>``).
    """
    if not content:
        return None, None, content
    lines = content.splitlines(keepends=True)
    if not lines:
        return None, None, content
    i = 0
    tab_title: str | None = None
    fence_mods: str | None = None
    first = lines[0].splitlines()[0] if lines[0] else ""
    m = _CODEGROUP_TAB_MARKER_RE.match(first)
    if m:
        tab_title = m.group(1).strip()
        i = 1
    if i < len(lines):
        line = lines[i].splitlines()[0] if lines[i] else ""
        m2 = _CODEGROUP_FENCE_MODS_RE.match(line)
        if m2:
            fence_mods = m2.group(1).strip()
            i += 1
    if tab_title is None and fence_mods is None:
        return None, None, content
    rest = "".join(lines[i:])
    return tab_title, fence_mods, rest


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
    model_id_spans: list[tuple[int, int]],
    tab_definitions: list[tuple[str, str]],
    fence_lang: str,
) -> str:
    """Wrap `content` in a CodeGroup, one tab per quickstart model variant.

    ``model_id_spans`` are character ranges of the quoted model ID only (not the
    ``model=`` / ``model:`` prefix), so assignment and property syntax are preserved.
    """
    parts: list[str] = []
    for title, model_id in tab_definitions:
        code = content
        for start, end in reversed(model_id_spans):
            code = _replace_span(code, start, end, model_id)
        parts.append(_codegroup_fence(title, fence_lang, code))
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

    # Strip marker lines while recording which model ID occurrences to expand.
    out_lines: list[str] = []
    keep_next_model = False
    canonical_model_id: str | None = None
    model_id_spans: list[tuple[int, int]] = []

    for line in content.splitlines(keepends=True):
        if line.strip() == keep_marker:
            keep_next_model = True
            continue

        out_offset = sum(len(l) for l in out_lines)
        for m in model_re.finditer(line):
            if keep_next_model:
                keep_next_model = False
                continue
            model_id = m.group(1)
            if canonical_model_id is None:
                canonical_model_id = model_id
            if model_id == canonical_model_id:
                model_id_spans.append(
                    (out_offset + m.start(1), out_offset + m.end(1))
                )

        out_lines.append(line)

    stripped = "".join(out_lines)
    if not model_id_spans:
        return None, stripped

    return (
        _expand_to_deepagents_codegroup(
            stripped,
            model_id_spans=model_id_spans,
            tab_definitions=tab_definitions,
            fence_lang=fence_lang,
        ),
        stripped,
    )


def format_snippet_mdx(content: str, *, language: str, fence_lang: str) -> str:
    """Return final MDX body for a snippet file."""
    content = content.rstrip() + "\n"
    tab_title, fence_mods, content = _strip_codegroup_markers(content)
    expanded, content = maybe_expand_deepagents_quickstart_codegroup(
        content, language=language, fence_lang=fence_lang
    )
    if expanded is not None:
        return expanded
    if tab_title is not None:
        parts = [fence_lang, tab_title]
        if fence_mods:
            parts.append(fence_mods)
        fence_opener = " ".join(parts)
    elif fence_mods:
        fence_opener = f"{fence_lang} {fence_mods}"
    else:
        fence_opener = fence_lang
    return f"```{fence_opener}\n{content.rstrip()}\n```\n"


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
        ("*.snippet.*.java", "java", "java"),
        ("*.snippet.*.kt", "kotlin", "kotlin"),
        ("*.snippet.*.go", "go", "go"),
        ("*.snippet.*.sh", "bash", "bash"),
    ]

    lang_suffix = {
        "python": "-py",
        "ts": "-js",
        "java": "-java",
        "kotlin": "-kt",
        "go": "-go",
        "bash": "-sh",
    }

    for glob_pattern, language, fence_lang in snippet_configs:
        for snippet_file in generated_dir.rglob(glob_pattern):
            snippet_name = ".".join(snippet_file.stem.split(".")[2:])
            expected_suffix = lang_suffix[language]
            if not snippet_name.endswith(expected_suffix):
                continue

            content = snippet_file.read_text(encoding="utf-8")
            mdx_content = format_snippet_mdx(
                content, language=language, fence_lang=fence_lang
            )
            rel_parent = snippet_file.parent.relative_to(generated_dir)
            out_subdir = snippets_dir / rel_parent
            out_subdir.mkdir(parents=True, exist_ok=True)
            mdx_path = out_subdir / f"{snippet_name}.mdx"
            mdx_path.write_text(mdx_content, encoding="utf-8")
            print(f"Generated {mdx_path.relative_to(repo_root)}")


if __name__ == "__main__":
    main()
