"""Convert standalone `pip install` code blocks to CodeGroup with both pip and uv.

Searches for standalone `pip install` commands in MDX files and converts them
to the CodeGroup format that shows both pip and uv installation options side-by-side.

Usage:
    # Convert all MDX files in current directory (recursively)
    python3 convert_pip_to_codegroup.py

    # using uv
    uv run convert_pip_to_codegroup.py

    # Preview changes without modifying files
    python3 convert_pip_to_codegroup.py --dry-run

    # Convert files in a specific directory
    python3 convert_pip_to_codegroup.py /path/to/docs

    # Convert a single file
    python3 convert_pip_to_codegroup.py --file path/to/file.mdx

Example conversion:
    Before:
        ```bash
        pip install langchain
        ```

    After:
        <CodeGroup>
        ```bash pip
        pip install langchain
        ```

        ```bash uv
        uv add langchain
        ```
        </CodeGroup>
"""

import argparse
import re
from pathlib import Path
from re import Match


def pip_to_uv(pip_cmd: str) -> str:
    """Convert a `pip install` command to equivalent `uv add` command."""
    # Remove 'pip install' and clean up
    cmd = pip_cmd.replace("pip install", "").strip()

    # Handle pip flags - need to handle combined flags like -qU carefully
    # Remove upgrade flags (uv add upgrades by default)
    cmd = re.sub(r"-U\b", "", cmd)
    cmd = re.sub(r"--upgrade\b", "", cmd)

    # Remove quiet flags
    cmd = re.sub(r"-q\b", "", cmd)
    cmd = re.sub(r"--quiet\b", "", cmd)

    # Remove editable flags (uv add handles local paths as editable by default)
    cmd = re.sub(r"-e\b", "", cmd)
    cmd = re.sub(r"--editable\b", "", cmd)

    # Remove requirements file flags (different handling in uv)
    cmd = re.sub(r"-r\b", "", cmd)
    cmd = re.sub(r"--requirement\b", "", cmd)

    # Handle pre-release flag
    cmd = re.sub(r"--pre\b", "@pre", cmd)

    # Clean up extra spaces first
    cmd = " ".join(cmd.split())

    # Handle quotes around package names with version specifiers
    # If package has version specifiers (>=, <=, ==, !=, ~=, >, <), keep quotes
    packages = []
    for part in cmd.split():
        if any(op in part for op in [">=", "<=", "==", "!=", "~=", ">", "<"]):
            # Add quotes if not already quoted and contains version specifiers
            if not (part.startswith('"') and part.endswith('"')) and not (
                part.startswith("'") and part.endswith("'")
            ):
                packages.append(f'"{part}"')
            else:
                packages.append(part)
        else:
            # Remove quotes from packages without version specifiers
            packages.append(part.replace('"', "").replace("'", ""))

    cmd = " ".join(packages)

    # Handle special cases
    if "[" in cmd and "]" in cmd:
        # Handle extras like "package[extra]" -> "package[extra]"
        pass  # uv handles extras the same way

    if "@pre" in cmd:
        # Move @pre to end of package name
        parts = cmd.split()
        if len(parts) == 1:
            return f"uv add {parts[0]}"
        # Multiple packages with @pre - apply to all
        packages = [p + "@pre" if "@pre" not in p else p for p in parts if p != "@pre"]
        return f"uv add {' '.join(packages)}"

    return f"uv add {cmd}" if cmd else "uv add"


def convert_pip_block_to_codegroup(content: str) -> str:
    """Convert standalone pip install code blocks to CodeGroup format."""
    # Match only bash blocks where pip install appears within the first few lines
    # This prevents matching across unrelated code blocks
    pip_pattern = re.compile(
        r"```(?:bash|shell|sh)?\s*\n((?:[^\n]*\n){0,3}[^\n]*pip install[^\n]*(?:\n(?!```)[^\n]*)*)\n```",  # noqa: E501
        re.MULTILINE,
    )

    def replace_pip_block(match: Match[str]) -> str:
        # Check if we're already inside a CodeGroup by examining the full context
        start_pos = match.start()

        # Look backwards for the nearest <CodeGroup> or </CodeGroup>
        text_before = content[:start_pos]
        last_codegroup_start = text_before.rfind("<CodeGroup>")
        last_codegroup_end = text_before.rfind("</CodeGroup>")

        # If the most recent CodeGroup tag before this match is an opening tag,
        # then we're inside a CodeGroup
        if last_codegroup_start > last_codegroup_end:
            return match.group(0)  # Already in CodeGroup

        block_content = match.group(1).strip()
        lines = block_content.split("\n")

        # Check if this is a simple pip install command (not part of a larger script)
        pip_lines = []
        other_lines = []

        for current_line in lines:
            line = current_line.strip()
            if line.startswith("pip install") and not line.startswith("#"):
                pip_lines.append(line)
            elif line and not line.startswith("#"):
                other_lines.append(line)

        # Only convert if we have pip install commands and minimal other content
        if pip_lines and len(other_lines) <= 2:  # noqa: PLR2004
            # Create the CodeGroup replacement
            pip_block_lines = []
            uv_block_lines = []

            for line in lines:
                if line.strip().startswith("pip install"):
                    pip_block_lines.append(line)
                    uv_line = pip_to_uv(line.strip())
                    uv_block_lines.append(uv_line)
                elif line.strip() and not line.strip().startswith("#"):
                    # Keep non-pip commands in both blocks
                    pip_block_lines.append(line)
                    uv_block_lines.append(line)
                elif line.strip().startswith("#"):
                    # Keep comments in both blocks
                    pip_block_lines.append(line)
                    uv_block_lines.append(line)

            pip_content = "\n".join(pip_block_lines)
            uv_content = "\n".join(uv_block_lines)

            return f"""<CodeGroup>
```bash pip
{pip_content}
```

```bash uv
{uv_content}
```
</CodeGroup>"""
        # Return original if it's a complex script
        return match.group(0)

    return pip_pattern.sub(replace_pip_block, content)


def convert_file(file_path: str, *, dry_run: bool = False) -> bool:
    """Convert a single MDX file. Returns True if changes were made."""
    try:
        file_obj = Path(file_path)
        original_content = file_obj.read_text(encoding="utf-8")

        converted_content = convert_pip_block_to_codegroup(original_content)

        if original_content != converted_content:
            if not dry_run:
                file_obj.write_text(converted_content, encoding="utf-8")
            return True
    except Exception:  # noqa: BLE001, S110
        pass
    return False


def main() -> None:
    """Convert pip install commands to CodeGroup format in MDX files."""
    parser = argparse.ArgumentParser(
        description=(
            "Convert pip install code blocks to CodeGroup format with uv alternatives"
        )
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to search for MDX files (default: current directory)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without modifying files"
    )
    parser.add_argument(
        "--file", help="Convert a specific file instead of searching directory"
    )

    args = parser.parse_args()

    if args.file:
        files = [args.file]
    else:
        # Find all MDX files
        search_path = Path(args.path)
        files = [str(f) for f in search_path.rglob("*.mdx")]

    if not files:
        return

    if args.dry_run:
        pass

    converted_count = 0
    for file_path in files:
        if convert_file(file_path, dry_run=args.dry_run):
            converted_count += 1


if __name__ == "__main__":
    main()
