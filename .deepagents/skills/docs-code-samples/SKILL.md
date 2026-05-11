---
name: docs-code-samples
description: Use this skill when migrating inline code samples from LangChain docs (MDX files) into external, testable code files that are extracted by this repo’s snippet scripts and used as Mintlify snippets. Applies when extracting code blocks from documentation, creating runnable code samples, using snippet delineators, or wiring snippet output into MDX includes.
license: MIT
compatibility: LangChain docs monorepo with Mintlify. Requires Python and Make (Node.js is also required for TypeScript samples).
metadata:
  author: langchain
  version: "1.0"
---

# docs-code-samples

## Overview

This skill documents the workflow for moving inline code samples from LangChain documentation into standalone, testable files that this repo extracts into snippets for use in MDX using Mintlify.

## When to use

- Migrating inline Python, TypeScript/JavaScript, or Java code blocks from MDX to external files
- Creating runnable, testable code samples for documentation
- Setting up snippet extraction and Mintlify snippet includes

## Directory structure

Code samples live under `src/code-samples/` in folders that match the product:

- `langchain/` — LangChain and LangGraph docs
- `deepagents/` — Deep Agents docs
- `langsmith/` — LangSmith docs

Example:

```
src/
├── code-samples/              # Source: testable code with snippet tags
│   ├── langchain/
│   │   ├── return-a-string.py
│   │   └── return-a-string.ts
│   ├── deepagents/
│   │   └── example-skill.py
│   └── langsmith/
│       ├── trace-example.py
│       └── trace-example.java
├── code-samples-generated/    # Snippet output (gitignored)
│   ├── return-a-string.snippet.tool-return-values.py
│   ├── return-a-string.snippet.tool-return-values.ts
│   └── ...
└── snippets/
    └── code-samples/          # MDX snippets for docs (all products)
        ├── tool-return-values-py.mdx
        ├── tool-return-values-js.mdx
        └── ...
```

**More than one snippet in one file**: A single code sample file can contain more than one named snippet using different `:snippet-start: snippet-name` and `:snippet-end:` pairs. Each snippet must have a unique name. This is useful for keeping related code samples together in one testable file.

## Step-by-step instructions

### 1. Create the code sample file

Place the file under `src/code-samples/` in the folder for the product: `langchain/`, `deepagents/`, or `langsmith/` (for example, `src/code-samples/langchain/return-a-string.py` for LangChain docs).

Use a descriptive filename, for example, `return-a-string.py`, `return-a-string.ts`, or `traceable-pipeline.java`.

### 2. Add snippet delineators

Wrap the code that should appear in the docs with snippet tags:

**Python:**
```python
# :snippet-start: snippet-name-py
from langchain.tools import tool

@tool
def get_weather(city: str) -> str:
    """Get weather for a city."""
    return f"It is currently sunny in {city}."

# :snippet-end:
```

**TypeScript/JavaScript:**
```ts
// :snippet-start: snippet-name-js
import { tool } from "langchain";
// ... tool definition ...
// :snippet-end:
```

**Java:**
```java
// :snippet-start: snippet-name-java
public class Example {
  public static void main(String[] args) {
    System.out.println("hello");
  }
}
// :snippet-end:
```

Choose a unique `snippet-name` in kebab-case. All snippet names must include a language suffix: `-py` for Python files, `-js` for TypeScript/JavaScript files, `-java` for Java files, and `-kt` for Kotlin files (for example, `tool-return-values-py`, `tool-return-values-js`, `traceable-pipeline-java`, `traceable-pipeline-kt`). This becomes the base of the output filename.

### 3. Add runnable test code in remove blocks

Wrap any code that makes the sample executable but should not appear in docs:

**Python:**
```python
# :remove-start:
if __name__ == "__main__":
    result = get_weather.invoke({"city": "San Francisco"})
    assert result == "It is currently sunny in San Francisco."
    print("✓ Tool works as expected")
# :remove-end:
```

**TypeScript:**
```ts
// :remove-start:
async function main() {
  const result = await getWeather.invoke({ city: "San Francisco" });
  if (result !== "It is currently sunny in San Francisco.") {
    throw new Error(`Expected "...", got "${result}"`);
  }
  console.log("✓ Tool works as expected");
}
main();
// :remove-end:
```

The extraction script strips `:remove-start:` / `:remove-end:` content when extracting snippets.

### 4. Test the code sample

Before extracting snippets, verify the code sample runs correctly:

```bash
# Test the file(s) you added (faster)
make test-code-samples FILES="src/code-samples/langchain/return-a-string.py"

# Or run all code samples
make test-code-samples
```

For multiple files: `FILES="path1 path2"`. Fix any failures before proceeding—do not extract snippets until the samples pass.

Java files (`.java`) under `src/code-samples/` are run using `jbang`. To keep CI green, Java samples must:

- Print at least one line of output so it's obvious the sample ran
- Exit successfully (code 0) when required API keys are not set, for example:
  - `OPENAI_API_KEY` for LLM calls
  - `LANGSMITH_API_KEY` for posting runs to LangSmith

Check formatting with:

```bash
make lint
```

Fix any ruff or mypy issues before proceeding. Run `make format` to auto-fix formatting.

### 5. Run snippet extraction

From the repo root:

```bash
make code-snippets
```

For LangSmith JVM samples only (faster; updates stems listed in `CODE_SNIPPET_LANGSMITH_SOURCES` in the Makefile):

```bash
make code-snippets-langsmith
```

This command:

1. Runs `python scripts/extract_code_snippets.py` (line-based, Bluehawk-compatible; handles `/**` in TS strings). Optional env `CODE_SNIPPET_SOURCES` limits extraction to specific paths under `src/code-samples/` (`make code-snippets-langsmith` sets this).
2. Runs `scripts/generate_code_snippet_mdx.py` to produce MDX snippets in `src/snippets/code-samples/` (always regenerates MDX from everything under `src/code-samples-generated/`)

Output files:

- `return-a-string.snippet.tool-return-values.py` → `tool-return-values-py.mdx`
- `return-a-string.snippet.tool-return-values.ts` → `tool-return-values-js.mdx`

### 6. Update the MDX file to use the snippet

Add an import at the top of the MDX file (after frontmatter):

```mdx
import ToolReturnValuesPy from '/snippets/code-samples/tool-return-values-py.mdx';
import ToolReturnValuesJs from '/snippets/code-samples/tool-return-values-js.mdx';
```

Replace the inline code blocks with the snippet components:

```mdx
:::python

<ToolReturnValuesPy />

:::

:::js

<ToolReturnValuesJs />

:::
```

## Naming conventions

| Element | Convention | Example |
|--------|-------------|---------|
| Code file | Descriptive, kebab-case | `return-a-string.py`, `return-a-string.ts`, `traceable-pipeline.java`, `traceable-pipeline.kt` |
| Snippet name | Kebab-case with language suffix: `-py` for Python, `-js` for JS/TS, `-java` for Java, `-kt` for Kotlin | `tool-return-values-py`, `tool-return-values-js`, `traceable-pipeline-java`, `traceable-pipeline-kt` |
| MDX snippet (Python) | `{snippet-name}.mdx` (snippet name ends in `-py`) | `tool-return-values-py.mdx` |
| MDX snippet (JS) | `{snippet-name}.mdx` (snippet name ends in `-js`) | `tool-return-values-js.mdx` |
| Component name | PascalCase | `ToolReturnValuesPy`, `ToolReturnValuesJs` |

## Script behavior

`scripts/generate_code_snippet_mdx.py`:

- Reads `*.snippet.*.py` and `*.snippet.*.ts` from `src/code-samples-generated/`
- Wraps content in fenced code blocks (`` ```python `` or `` ```ts ``)
- Writes to `src/snippets/code-samples/{snippet-name}-py.mdx` or `-js.mdx`

To support additional languages, add config entries in that script.

## Guidelines

- Do not mock LangChain internals (for example `unittest.mock.patch` on `init_chat_model` helpers) so that imports resolve real chat model instances. Tests should exercise real model wiring; use lightweight fakes such as `GenericFakeChatModel` only when you need deterministic assertions without API calls.
- Do not change `pyproject.toml` when making code sample changes.
- Always run `make test-code-samples FILES="path/to/your/file.py"` before `make code-snippets` to ensure new samples pass.
- Run `make lint` once the code sample is written; fix any issues (or run `make format` to auto-fix).
- Do not add code samples to linting ignore rules when making lint-related changes—fix the code instead.
- `src/code-samples-generated/` is gitignored; regenerate with `make code-snippets` or `make code-snippets-langsmith` when iterating on LangSmith JVM files only.
- Reference `CLAUDE.md` and `AGENTS.md` for docs style and rules.
- Use `:::python` and `:::js` fences for language-specific content; the build produces separate Python and JavaScript doc versions.
- For python tests, try to correct the type rather than adding `# type: ignore[arg-type]`
