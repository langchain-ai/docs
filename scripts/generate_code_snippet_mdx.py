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

    # Mapping: (glob_pattern, language) for each snippet type
    snippet_configs = [
        ("*.snippet.*.py", "python"),
        ("*.snippet.*.ts", "ts"),
    ]

    # Only process snippets that already have language suffix to
    # avoid Bluehawk duplicates
    lang_suffix = {"python": "-py", "ts": "-js"}

    for glob_pattern, language in snippet_configs:
        for snippet_file in generated_dir.glob(glob_pattern):
            snippet_name = ".".join(snippet_file.stem.split(".")[2:])
            expected_suffix = lang_suffix[language]
            # Only process language-specific snippets
            # (tool-return-object-py, not tool-return-object) to avoid
            # duplicates when Bluehawk emits both suffixed and unsuffixed versions
            if not snippet_name.endswith(expected_suffix):
                continue

            content = snippet_file.read_text(encoding="utf-8")
            # Create MDX with fenced code block
            mdx_content = f"```{language}\n{content.rstrip()}\n```\n"
            mdx_path = snippets_dir / f"{snippet_name}.mdx"
            mdx_path.write_text(mdx_content, encoding="utf-8")
            print(f"Generated {mdx_path.relative_to(repo_root)}")


if __name__ == "__main__":
    main()
