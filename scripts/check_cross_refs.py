"""Check for unresolved cross-references in documentation source files.

Scans all .mdx and .md files under src/ for @[ref] patterns and validates
that each reference has a corresponding entry in link_map.py. Respects
:::python/:::js scope fences so references are checked against the correct
scope's link map.

Exit code 0 if all references resolve, 1 if any are unresolved.
"""

import sys
from pathlib import Path

from pipeline.preprocessors.handle_auto_links import (
    CODE_FENCE_PATTERN,
    CONDITIONAL_FENCE_PATTERN,
    CROSS_REFERENCE_PATTERN,
)
from pipeline.preprocessors.link_map import SCOPE_LINK_MAPS

SRC_DIR = Path(__file__).resolve().parent.parent / "src"

SCOPES_FOR_PATH: dict[str, list[str]] = {
    "oss/python/": ["python"],
    "oss/javascript/": ["js"],
}


def _default_scopes_for_file(rel_path: str) -> list[str]:
    """Return the default scope(s) a file is built under."""
    for prefix, scopes in SCOPES_FOR_PATH.items():
        if rel_path.startswith(prefix):
            return scopes
    if rel_path.startswith("oss/"):
        return ["python", "js"]
    # Non-OSS content (e.g., langsmith/) only generates Python-scope pages
    return ["python"]


def _extract_refs(
    content: str,
    default_scopes: list[str],
) -> list[tuple[int, str, list[str]]]:
    """Extract (line_number, ref_name, scopes) from file content."""
    refs: list[tuple[int, str, list[str]]] = []
    current_scopes = default_scopes
    in_code_block = False

    for line_number, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()

        if CODE_FENCE_PATTERN.match(stripped):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        fence_match = CONDITIONAL_FENCE_PATTERN.match(stripped)
        if fence_match:
            language = fence_match.group("language")
            if language and language.lower() in ("python", "js"):
                current_scopes = [language.lower()]
            else:
                current_scopes = default_scopes
            continue

        for match in CROSS_REFERENCE_PATTERN.finditer(line):
            # CROSS_REFERENCE_PATTERN uses (?<!\\) lookbehind to skip escaped refs
            ref_name = match.group("link_name_with_title") or match.group("link_name")
            if ref_name:
                refs.append((line_number, ref_name, list(current_scopes)))

    return refs


def check_cross_refs(src_dir: Path) -> list[tuple[str, int, str, list[str]]]:
    """Return list of (file, line, ref_name, scopes) for unresolved refs."""
    errors: list[tuple[str, int, str, list[str]]] = []

    md_files = sorted(
        [*src_dir.rglob("*.mdx"), *src_dir.rglob("*.md")],
    )

    for file_path in md_files:
        rel_path = str(file_path.relative_to(src_dir))

        if rel_path.startswith("snippets/code-samples/"):
            continue
        if "node_modules" in rel_path:
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            print(f"  WARNING: skipping {rel_path} (not valid UTF-8: {exc})")
            continue
        default_scopes = _default_scopes_for_file(rel_path)
        refs = _extract_refs(content, default_scopes)

        for line_number, ref_name, scopes in refs:
            resolved = any(
                ref_name in SCOPE_LINK_MAPS.get(scope, {}) for scope in scopes
            )
            if not resolved:
                errors.append((rel_path, line_number, ref_name, scopes))

    return errors


def main() -> None:
    """CLI entrypoint for cross-reference validation."""
    errors = check_cross_refs(SRC_DIR)

    if not errors:
        print("✅ All cross-references resolved")
        sys.exit(0)

    print(f"found {len(errors)} unresolved cross-reference(s):\n")
    for file_path, line_number, ref_name, scopes in errors:
        scope_str = ", ".join(scopes)
        print(
            f"  {file_path}:{line_number}: @[{ref_name}] not in scope(s): {scope_str}"
        )

    print(
        f"\n❌ {len(errors)} unresolved cross-reference(s). "
        "Add entries to pipeline/preprocessors/link_map.py or fix the reference."
    )
    sys.exit(1)


if __name__ == "__main__":
    main()
