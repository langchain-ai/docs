#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from typing import Any


# Ref API JSON (?format=json). For JS, the config object matches CreateDeepAgentParams
# (the argument to `createDeepAgent`); see
# https://reference.langchain.com/api/ref/javascript/deepagents/types/CreateDeepAgentParams
PYTHON_REF_JSON_URL = "https://reference.langchain.com/api/ref/python/deepagents/create_deep_agent?format=json"
JS_CREATE_DEEP_AGENT_PARAMS_JSON_URL = "https://reference.langchain.com/api/ref/javascript/deepagents/types/CreateDeepAgentParams?format=json"

PY_SNIPPET_PATH = Path("src/snippets/create-deep-agent-config-options-py.mdx")
JS_SNIPPET_PATH = Path("src/snippets/create-deep-agent-config-options-js.mdx")


def _strip_query_and_fragment(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def _normalize_fetch_url(url: str) -> str:
    base = _strip_query_and_fragment(url)
    return f"{base}?format=json" if "format=" not in url else url


def _fetch_json(url: str) -> Any:
    req = urllib.request.Request(
        _normalize_fetch_url(url),
        headers={
            "User-Agent": "langchain-docs-sync-bot/1.0",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return json.loads(resp.read().decode(charset))


def _render_js_config_snippet(member_name_types: list[tuple[str, str]]) -> str:
    """
    Render a docs-friendly createDeepAgent config object snippet that focuses on the
    parameter surface, not the full generic function signature.
    Order and types come from the CreateDeepAgentParams JSON (members list).
    """
    ordered: list[tuple[str, str]] = []
    seen: set[str] = set()
    for name, typ in member_name_types:
        if name not in seen:
            ordered.append((name, typ))
            seen.add(name)

    lines = ["const agent = createDeepAgent({"]
    for i, (key, hint) in enumerate(ordered):
        suffix = "," if i < len(ordered) - 1 else ""
        lines.append(f"  {key}?: {hint}{suffix}")
    lines.append("});")
    return "```typescript\n" + "\n".join(lines) + "\n```\n"


def _py_signature_from_json(data: dict[str, Any]) -> str:
    try:
        code = data["signature"]
    except KeyError as e:
        raise RuntimeError("Python ref JSON missing 'signature'") from e
    code = code.rstrip()
    # API reference often has a trailing comma after the last param; the docs prefer omitting it.
    code = re.sub(r",(\n\s*)\) ->", r"\1) ->", code, count=1)
    return f"```python\n{code}\n```\n"


def _js_members_name_types(data: dict[str, Any]) -> list[tuple[str, str]]:
    try:
        members = data["members"]
    except KeyError as e:
        raise RuntimeError("CreateDeepAgentParams JSON missing 'members'") from e
    out: list[tuple[str, str]] = []
    for m in members:
        if m.get("kind") != "property" or m.get("visibility") != "public":
            continue
        name = m.get("name")
        typ = m.get("type")
        if not isinstance(name, str) or not isinstance(typ, str):
            continue
        out.append((name, typ))
    if not out:
        raise RuntimeError("No public properties found on CreateDeepAgentParams JSON")
    return out


def _write_if_changed(path: Path, new_content: str) -> bool:
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    if old == new_content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(new_content, encoding="utf-8")
    return True


def main() -> int:
    py_data = _fetch_json(PYTHON_REF_JSON_URL)
    js_params_data = _fetch_json(JS_CREATE_DEEP_AGENT_PARAMS_JSON_URL)

    if not isinstance(py_data, dict) or not isinstance(js_params_data, dict):
        raise RuntimeError("Unexpected JSON root type from ref API")

    py_block = _py_signature_from_json(py_data)

    if js_params_data.get("name") != "CreateDeepAgentParams":
        raise RuntimeError("CreateDeepAgentParams ref JSON missing expected name")

    js_member_tuples = _js_members_name_types(js_params_data)
    js_block = _render_js_config_snippet(js_member_tuples)

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
