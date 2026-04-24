#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


PYTHON_REF_URL = "https://reference.langchain.com/python/deepagents/graph/create_deep_agent"
JS_REF_URL = "https://reference.langchain.com/javascript/deepagents/agent/createDeepAgent"
JS_PARAMS_URL = "https://reference.langchain.com/javascript/deepagents/types/CreateDeepAgentParams"

PY_SNIPPET_PATH = Path("src/snippets/create-deep-agent-config-options-py.mdx")
JS_SNIPPET_PATH = Path("src/snippets/create-deep-agent-config-options-js.mdx")


def _strip_query_and_fragment(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def _fetch(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={
            # Some CDNs return different content without a UA.
            "User-Agent": "langchain-docs-sync-bot/1.0",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="replace")


def _ts_pretty_signature(sig: str) -> str:
    """
    The JS reference page signature is typically rendered as a single very long
    line. Make it readable for docs by inserting line breaks at safe boundaries.
    """
    s = sig.strip()
    if "\n" in s:
        return s

    # If the return type is enormous, keep the snippet focused on the parameter
    # surface (which is what we want to track for docs).
    if "): " in s and ": DeepAgent<" in s:
        s = s.split(": DeepAgent<", 1)[0] + ": DeepAgent<...>"

    out: list[str] = []
    indent = 0
    paren = 0
    angle = 0

    def push(txt: str) -> None:
        out.append(txt)

    def newline(extra_indent: int = 0) -> None:
        while out and out[-1].endswith(" "):
            out[-1] = out[-1].rstrip(" ")
        out.append("\n" + "  " * max(indent + extra_indent, 0))

    i = 0
    while i < len(s):
        ch = s[i]

        if ch == "<":
            angle += 1
            push(ch)
            if angle == 1:
                indent += 1
                newline()
            i += 1
            continue
        if ch == ">":
            if angle == 1:
                indent = max(indent - 1, 0)
                newline(-1)
            angle = max(angle - 1, 0)
            push(ch)
            i += 1
            continue
        if ch == "(":
            paren += 1
            push(ch)
            indent += 1
            newline()
            i += 1
            continue
        if ch == ")":
            paren = max(paren - 1, 0)
            indent = max(indent - 1, 0)
            newline(-1)
            push(ch)
            i += 1
            continue

        # Break at commas only at the top level within generics/params.
        if ch == "," and (angle == 1 or paren == 1):
            push(",")
            newline()
            i += 1
            if i < len(s) and s[i] == " ":
                i += 1
            continue

        if s.startswith("):", i):
            push("):")
            i += 2
            newline()
            continue

        push(ch)
        i += 1

    return "".join(out).strip()


def _extract_js_param_names_from_create_params(html: str) -> list[str]:
    """
    Extract the bullet list under '## Properties' from the CreateDeepAgentParams page.
    The page content frequently uses escaped newlines.
    """
    idx = html.find("## Properties")
    if idx == -1:
        raise RuntimeError("Could not find '## Properties' on CreateDeepAgentParams page")

    after = html[idx:]
    # Prefer the escaped-newline representation first.
    if "\\n- `" in after:
        # Example: "## Properties\\n\\n- `backend`\\n- `checkpointer`..."
        m = re.search(r"## Properties\\\\n\\\\n(.*?)(?:\\\\n\\\\n---|\\n\\n---)", after, flags=re.DOTALL)
        if not m:
            raise RuntimeError("Could not extract properties block from escaped content")
        block = m.group(1)
        items = re.findall(r"- `([^`]+)`", block)
        return items

    # Fallback: real markdown newlines.
    m = re.search(r"## Properties\\s*\\n\\s*(.*?)(?:\\n---|\\Z)", after, flags=re.DOTALL)
    if not m:
        raise RuntimeError("Could not extract properties block")
    block = m.group(1)
    return re.findall(r"- `([^`]+)`", block)


def _render_js_config_snippet(param_names: list[str]) -> str:
    """
    Render a docs-friendly 'createDeepAgent({ ... })' snippet that focuses on the
    parameter surface, not the full generic function signature.
    """
    # Follow the order from the API reference ("## Properties") to avoid docs drift.
    ordered: list[str] = []
    seen: set[str] = set()
    for key in param_names:
        if key not in seen:
            ordered.append(key)
            seen.add(key)

    type_hints: dict[str, str] = {
        "model": "BaseLanguageModel | string",
        "tools": "TTools | StructuredTool[]",
        "systemPrompt": "string | SystemMessage",
        "middleware": "TMiddleware",
        "subagents": "TSubagents",
        "responseFormat": "TResponse",
        "backend": "AnyBackendProtocol | ((config) => AnyBackendProtocol)",
        "interruptOn": "Record<string, boolean | InterruptOnConfig>",
        "memory": "string[]",
        "skills": "string[]",
        # Keep the rest intentionally generic; they’re less commonly shown.
        "checkpointer": "unknown",
        "contextSchema": "unknown",
        "store": "unknown",
        "name": "string",
        "debug": "boolean",
        "cache": "unknown",
        "permissions": "unknown",
    }

    lines = ["const agent = createDeepAgent({"]
    for key in ordered:
        hint = type_hints.get(key, "unknown")
        lines.append(f"  {key}?: {hint},")
    lines.append("  ...")
    lines.append("});")
    return "```typescript\n" + "\n".join(lines) + "\n```\n"

def _extract_signature_codeblock(
    html: str, *, language: str, fence_language: str
) -> str:
    """
    Extract the first code fence that appears after a '## Signature' heading.
    Returns a complete fenced code block (```...```), with the fence language
    rewritten to `fence_language`.
    """
    signature_idx = html.find("## Signature")
    if signature_idx == -1:
        raise RuntimeError("Could not find '## Signature' section")

    after = html[signature_idx:]

    # The reference site content often includes literal "\n" sequences instead
    # of actual newlines (e.g., embedded JSON). Handle both cases.
    start = f"```{language}"
    start_idx = after.find(start)
    if start_idx == -1:
        raise RuntimeError(f"Could not find ```{language} fenced block after Signature")

    after_start = after[start_idx + len(start) :]
    if after_start.startswith("\n"):
        # Standard markdown fence.
        end_marker = "\n```"
        end_idx = after_start.find(end_marker)
        if end_idx == -1:
            raise RuntimeError(f"Could not find closing fence for ```{language}")
        code = after_start[1:end_idx]
    elif after_start.startswith("\\n"):
        # Escaped newlines.
        end_marker = "\\n```"
        end_idx = after_start.find(end_marker)
        if end_idx == -1:
            raise RuntimeError(f"Could not find closing fence for ```{language}")
        raw = after_start[2:end_idx]
        code = raw.encode("utf-8").decode("unicode_escape")
    else:
        raise RuntimeError(
            f"Unexpected content immediately after ```{language} fence: {after_start[:20]!r}"
        )

    code = code.rstrip()
    if fence_language == "typescript":
        code = _ts_pretty_signature(code)
    return f"```{fence_language}\n{code}\n```\n"


def _write_if_changed(path: Path, new_content: str) -> bool:
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    if old == new_content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(new_content, encoding="utf-8")
    return True


def main() -> int:
    py_url = _strip_query_and_fragment(PYTHON_REF_URL)
    js_url = _strip_query_and_fragment(JS_REF_URL)
    js_params_url = _strip_query_and_fragment(JS_PARAMS_URL)

    py_html = _fetch(py_url)
    js_html = _fetch(js_url)
    js_params_html = _fetch(js_params_url)

    py_block = _extract_signature_codeblock(
        py_html, language="python", fence_language="python"
    )
    # For JS, keep docs-friendly config-object snippet (not the giant generic signature).
    js_param_names = _extract_js_param_names_from_create_params(js_params_html)
    js_block = _render_js_config_snippet(js_param_names)

    changed = False
    changed |= _write_if_changed(PY_SNIPPET_PATH, py_block)
    changed |= _write_if_changed(JS_SNIPPET_PATH, js_block)

    if changed:
        print("Updated deepagents signature snippets.")
    else:
        print("No deepagents signature snippet changes detected.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
