"""Markdown preprocessor for handling cross-references and conditional blocks.

This module provides functionality to preprocess markdown files by:
1. Transforming @[link_name] references to proper markdown links
2. Processing conditional language blocks (:::python, :::js)
"""

import logging
import os
import re
from pathlib import Path

from pipeline.preprocessors.handle_auto_links import replace_autolinks
from pipeline.preprocessors.utm_links import add_utm_to_cta_links

logger = logging.getLogger(__name__)

_FENCE_OPEN = re.compile(r"^[ \t]*:::(\w+)\s*$")
_FENCE_CLOSE = re.compile(r"^[ \t]*:::\s*$")
_FENCE_LIKE = re.compile(r"^[ \t]*:::")
_CODE_FENCE = re.compile(r"^[ \t]*(```|~~~)")


def _validate_conditional_fences(md_text: str) -> None:
    """Raise if conditional fences are unbalanced or split a table.

    Conditional rendering pairs each opener with the next closer, so a broken
    fence does not fail on its own: content leaks into the other language and
    a stray ``:::`` renders as text. A fence between two table rows splits the
    table, because the stripped fence leaves a blank line behind.

    Args:
        md_text: The markdown content to check.

    Raises:
        ValueError: Listing the line number and problem for each broken fence.
    """
    lines = md_text.split("\n")
    problems: list[str] = []
    open_line: int | None = None
    in_code = False

    for number, line in enumerate(lines, start=1):
        if _CODE_FENCE.match(line):
            in_code = not in_code
        if in_code or line.lstrip().startswith("\\:::"):
            continue

        if match := _FENCE_OPEN.match(line):
            if open_line is not None:
                problems.append(
                    f"line {number}: :::{match.group(1)} opens inside the block "
                    f"opened at line {open_line}"
                )
            open_line = number
        elif _FENCE_CLOSE.match(line):
            if open_line is None:
                problems.append(f"line {number}: ::: closes a block that is not open")
            open_line = None
        elif _FENCE_LIKE.match(line):
            problems.append(
                f"line {number}: malformed fence {line.strip()[:40]!r}; put each "
                "fence on its own line"
            )
            continue
        else:
            continue

        previous = lines[number - 2].strip() if number > 1 else ""
        following = lines[number].strip() if number < len(lines) else ""
        if previous.startswith("|") and following.startswith("|"):
            problems.append(
                f"line {number}: fence inside a table splits it; write one full "
                "table per language"
            )

    if open_line is not None:
        problems.append(f"line {open_line}: block is never closed with :::")

    if problems:
        msg = "Broken conditional fences:\n  " + "\n  ".join(problems)
        raise ValueError(msg)


def _apply_conditional_rendering(md_text: str, target_language: str) -> str:
    r"""Apply conditional rendering to markdown content.

    Processes conditional blocks like:
    :::python
    This content is only shown for Python
    :::

    Escaped blocks (with backslash) are preserved as literal text:
    \:::python
    This will appear as :::python in the output
    \:::

    Args:
        md_text: The markdown content to process.
        target_language: The target language ("python" or "js").

    Returns:
        Processed markdown with conditional blocks resolved and escaped tags unescaped.

    Raises:
        ValueError: If target_language is not "python" or "js".
    """
    if target_language not in {"python", "js"}:
        msg = "target_language must be 'python' or 'js'"
        raise ValueError(msg)

    _validate_conditional_fences(md_text)

    # Pattern for non-escaped conditional blocks
    pattern = re.compile(
        r"(?P<indent>[ \t]*)(?<!\\):::(?P<language>\w+)\s*\n"
        r"(?P<content>((?:.*\n)*?))"  # Capture content inside the block
        r"(?P=indent)[ \t]*(?<!\\):::"  # Match closing, same indentation, not escaped
    )

    def replace_conditional_blocks(match: re.Match) -> str:
        """Keep active conditionals."""
        language = match.group("language")
        content = match.group("content")

        if language not in {"python", "js"}:
            # If the language is not supported, return the original block
            return match.group(0)

        if language == target_language:
            return content

        # If the language does not match, return an empty string
        return ""

    # Process conditional blocks first
    result = pattern.sub(replace_conditional_blocks, md_text)

    # Then unescape escaped tags by removing the backslash
    return re.sub(r"\\(:::)", r"\1", result)


def preprocess_markdown(
    content: str,
    file_path: Path,
    *,
    target_language: str | None = None,
    default_scope: str | None = None,
) -> str:
    """Preprocess markdown content with cross-references and conditional blocks.

    Args:
        content: The markdown content to process.
        file_path: Path to the file being processed (for error reporting).
        target_language: Target language for conditional blocks ("python" or "js").
                        If None, uses TARGET_LANGUAGE environment variable.
        default_scope: Default scope for cross-references. If None,
            uses target_language.

    Returns:
        Processed markdown content.
    """
    # Determine target language
    if target_language is None:
        target_language = os.environ.get("TARGET_LANGUAGE", "python")

    # Determine default scope for cross-references
    if default_scope is None:
        default_scope = target_language

    # Apply cross-reference preprocessing
    content = replace_autolinks(content, str(file_path), default_scope=default_scope)

    # Add UTM tracking to LangSmith CTA links
    content = add_utm_to_cta_links(content, file_path)

    # Apply conditional rendering for code blocks
    return _apply_conditional_rendering(content, target_language)
