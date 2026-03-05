"""Generate MDX snippet files from Bluehawk-generated code snippet files.

Reads .snippet.*.py and .snippet.*.ts files from src/code-samples-generated/
and creates corresponding MDX files in src/snippets/code-samples/ for use in docs.

Run as part of `make code-snippets` after Bluehawk extraction.
"""

from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    generated_dir = repo_root / "src" / "code-samples-generated"
    snippets_dir = repo_root / "src" / "snippets" / "code-samples"

    if not generated_dir.exists():
        return

    snippets_dir.mkdir(parents=True, exist_ok=True)

    # Mapping: (glob_pattern, language, suffix) for each snippet type
    snippet_configs = [
        ("*.snippet.*.py", "python", "-py"),
        ("*.snippet.*.ts", "ts", "-js"),
    ]

    for glob_pattern, language, suffix in snippet_configs:
        for snippet_file in generated_dir.glob(glob_pattern):
            content = snippet_file.read_text(encoding="utf-8")
            # Create MDX with fenced code block
            mdx_content = f"```{language}\n{content.rstrip()}\n```\n"
            # Output filename: tool-return-values-py.mdx from return-a-string.snippet.tool-return-values.py
            snippet_name = ".".join(snippet_file.stem.split(".")[2:])
            mdx_path = snippets_dir / f"{snippet_name}{suffix}.mdx"
            mdx_path.write_text(mdx_content, encoding="utf-8")
            print(f"Generated {mdx_path.relative_to(repo_root)}")


if __name__ == "__main__":
    main()
