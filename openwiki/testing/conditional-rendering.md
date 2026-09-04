---
type: guide
title: Testing Conditional Rendering
description: How to test :::python and :::js conditional blocks to ensure correct content appears in each language variant during the build process.
tags: [testing, conditional-rendering, versioning, language-variants]
verified:
  - by: openwiki/0.5.0
    at: 2026-09-03T15:00:58.567Z
sources:
  - id: openwiki-source-012f2c78e3b1446dfc35803f
    resource: repo://Makefile
  - id: openwiki-source-d0cdf44431684bdedf34705a
    resource: repo://pipeline/core/builder.py
  - id: openwiki-source-06a4c757b1153b7de4f47a0e
    resource: repo://pipeline/preprocessors/markdown_preprocessor.py
  - id: openwiki-source-24e5f74f0f40e9bfd381871f
    resource: repo://tests/unit_tests/test_builder.py
generated: { by: "openwiki/0.5.0", at: "2026-09-03T15:00:58.567Z" }
---

# Testing Conditional Rendering

Conditional rendering—using `:::python` and `:::js` fence blocks to include language-specific content in a single source file—is a core feature of the documentation pipeline. This guide explains how to verify that conditional blocks are resolved correctly during the build process.

## Overview

Conditional blocks allow documentation authors to provide language-specific examples, explanations, and code samples from a single source file. During the build, the `_apply_conditional_rendering()` function in `/pipeline/preprocessors/markdown_preprocessor.py` resolves these blocks based on the target language:

- When building with `target_language="python"`, `:::python` blocks are kept and `:::js` blocks are removed
- When building with `target_language="js"`, `:::js` blocks are kept and `:::python` blocks are removed
- The content between the opening fence and closing fence is kept or removed as a unit

## How Conditional Rendering Works

### Rendering Rule

The processor uses a regex pattern to match non-escaped conditional blocks:

```regex
(?P<indent>[ \t]*)(?<!\\):::(?P<language>\w+)\s*\n
(?P<content>((?:.*\n)*?))
(?P=indent)[ \t]*(?<!\\):::
```

**Key properties:**

- **Indentation matching** – The closing `:::` must have the same indentation as the opening `:::python` or `:::js`
- **Content preservation** – All content between fences (including blank lines and nested code blocks) is kept or removed together
- **Escape support** – A leading backslash (`\:::`) prevents fence processing; the backslash is removed during post-processing
- **Language-specific** – Only recognized languages (`python` or `js`) are processed; unrecognized languages are left unchanged

### Example: Basic Block Resolution

**Source file** (single version):
```markdown
# Installation

:::python
pip install langchain
:::

:::js
npm install langchain
:::
```

**After build with `target_language="python"`** (file: `/build/oss/python/intro.mdx`):
```markdown
# Installation

pip install langchain

```

**After build with `target_language="js"`** (file: `/build/oss/javascript/intro.mdx`):
```markdown
# Installation

npm install langchain

```

Notice that the removed conditional block leaves an empty string; this may result in blank lines in the output.

## Setting Up a Test

### Test Strategy

The recommended test strategy has four steps:

1. **Create a test file** with both `:::python` and `:::js` blocks in a source directory
2. **Build the documentation** using `make build` to generate both language variants
3. **Verify output files** exist in the correct language-prefixed directories
4. **Assert correct content** – Python version contains Python-specific content and JavaScript version contains JS-specific content

### Step 1: Create a Versioned Test Page

Create a source file at `/src/oss/<product>/<test-page>.mdx`:

```markdown
---
title: Test Conditional Rendering
description: Verify language-specific content appears correctly.
---

# Configuration

Here's how to configure the system:

:::python
```python
from langchain import Config

config = Config(debug=True)
```
:::

:::js
```javascript
import { Config } from 'langchain';

const config = new Config({ debug: true });
```
:::

## Next Steps

<!-- openwiki: broken internal link [/oss/python/guides/next-steps] file "/oss/python/guides/next-steps" does not exist. Fix the href or restore the target, then delete this comment. -->
See the [guide](/oss/python/guides/next-steps) for more.
```

### Step 2: Build the Documentation

Run the build command to generate both Python and JavaScript variants:

```bash
make build
```

This invokes `pipeline build`, which:
1. Clears the existing `/build/` directory
2. Processes all source files through the preprocessing pipeline
3. For versioned OSS content, builds twice—once with `target_language="python"` and once with `target_language="js"`
4. Writes both variants to language-prefixed output paths

### Step 3: Verify Output Files Exist

After the build completes, verify that both language-specific output files were created:

```bash
ls -la build/oss/python/<product>/
ls -la build/oss/javascript/<product>/
```

For the example above, you should see:
- `/build/oss/python/<product>/test-page.mdx`
- `/build/oss/javascript/<product>/test-page.mdx`

### Step 4: Assert Correct Content

Read the output files and verify that the correct language-specific content appears in each:

**Python version** should contain:
```markdown
```python
from langchain import Config

config = Config(debug=True)
```
```

And should NOT contain the JavaScript block.

**JavaScript version** should contain:
```markdown
```javascript
import { Config } from 'langchain';

const config = new Config({ debug: true });
```
```

And should NOT contain the Python block.

## Automated Unit Tests

The build system includes unit tests that verify conditional rendering during integration tests. See `/tests/unit_tests/test_builder.py` for examples.

### Example: Managed Deep Agents Test

The test `test_build_all_creates_managed_deep_agents_language_routes()` verifies that conditional blocks in snippets are resolved correctly:

```python
def test_build_all_creates_managed_deep_agents_language_routes() -> None:
    """Managed Deep Agents pages and snippets build for both languages."""
    files = [
        File(
            path="snippets/langsmith/managed-deep-agents-next-steps.mdx",
            content=(
<!-- openwiki: broken internal link [/langsmith/managed-deep-agents-tools] file "/langsmith/managed-deep-agents-tools" does not exist. Fix the href or restore the target, then delete this comment. -->
                "[Tools](/langsmith/managed-deep-agents-tools)\n"
<!-- openwiki: broken internal link [/oss/deepagents/overview] file "/oss/deepagents/overview" does not exist. Fix the href or restore the target, then delete this comment. -->
                "[Deep Agents](/oss/deepagents/overview)\n"
                ":::python\nPython only.\n:::\n"
                ":::js\nTypeScript only.\n:::\n"
            ),
        ),
    ]

    with file_system(files) as fs:
        builder = DocumentationBuilder(fs.src_dir, fs.build_dir)
        builder.build_all()

        # Verify Python version contains Python content
        python_snippet = (
            fs.build_dir
            / "snippets"
            / "python"
            / "langsmith"
            / "managed-deep-agents-next-steps.mdx"
        ).read_text()
        assert "Python only." in python_snippet
        assert "TypeScript only." not in python_snippet

        # Verify JavaScript version contains JavaScript content
        js_snippet = (
            fs.build_dir
            / "snippets"
            / "javascript"
            / "langsmith"
            / "managed-deep-agents-next-steps.mdx"
        ).read_text()
        assert "TypeScript only." in js_snippet
        assert "Python only." not in js_snippet
```

This pattern—create test files, build, extract output, assert presence/absence of specific strings—applies to any conditional rendering test.

## Local Development Testing

When working in development mode (`make dev`), the build system watches for changes and automatically rebuilds affected files. You can then check both language variants in the UI:

1. **Start development mode**:
   ```bash
   make dev
   ```

2. **Open the documentation** in your browser (Mintlify dev server, typically `http://localhost:3000`)

3. **Locate your test page** in the navigation

4. **Check the Python tab** to verify Python-specific content appears and JavaScript content is absent

5. **Check the JavaScript tab** to verify JavaScript-specific content appears and Python content is absent

6. **Use browser DevTools** (F12) to inspect the rendered content and confirm the HTML structure matches expected output

## Common Mistakes and Pitfalls

### Indentation Mismatch

**Mistake:** Opening and closing fences have different indentation levels.

```markdown
:::python
Some content
  :::
```

**Result:** The closing `:::` is not recognized as the block terminator. The pattern requires the closing fence to be at the exact same indentation as the opening fence (including space/tab characters).

**Fix:** Ensure indentation matches:
```markdown
:::python
Some content
:::
```

### Forgetting the Closing Fence

**Mistake:** A conditional block is not closed.

```markdown
:::python
Some content that continues to the end of the file
```

**Result:** The opening tag is left unmatched; depending on the context, the entire remainder of the file may be treated as conditional content. The build may log an exception for unclosed conditionals.

**Fix:** Always close each conditional block:
```markdown
:::python
Some content
:::
```

### Nesting Conditional Blocks

**Mistake:** Attempting to nest one conditional block inside another.

```markdown
:::python
:::js
Some nested content
:::
:::
```

**Result:** Nesting is not supported. The innermost closing `:::` closes the Python block, leaving a stray `:::` that may cause parsing errors or be treated as literal text.

**Fix:** Use sequential, non-nested blocks instead:
```markdown
:::python
Python-specific content
:::

:::js
JavaScript-specific content
:::
```

### Conditional Blocks Inside Code Fences

**Mistake:** Putting a conditional fence inside a triple-backtick code block.

```markdown
```python
:::js
This is code, not a conditional
:::
```
```

**Result:** Code fence content is not processed for conditional rendering. The `:::js` block is treated as literal code text, not as a conditional marker. This is intentional—the system does not process conditionals inside code fences.

**Fix:** Place conditional blocks outside code fences:
```markdown
:::python
```python
# Python code
print("hello")
```
:::

:::js
```javascript
// JavaScript code
console.log("hello");
```
:::
```

### Escaped Conditionals for Documentation

**Correct usage:** To document the conditional syntax itself, use escaped fences.

```markdown
To show a conditional block, use escaped fences:

\:::python
This will appear as literal text in the output
\:::
```

**Result:** The output will display:
```
To show a conditional block, use escaped fences:

:::python
This will appear as literal text in the output
:::
```

The backslash is removed during post-processing, leaving the original fence syntax visible.

## Inspection and Debugging

### Build Log Output

When the build runs, the preprocessor may log warnings or errors related to conditional blocks. Check the build logs:

```bash
make build 2>&1 | grep -i conditional
```

### Examining Preprocessor Regex

To understand how the regex matches your specific content, you can test the pattern directly in Python:

```python
import re
from pipeline.preprocessors.markdown_preprocessor import _apply_conditional_rendering

source = """
:::python
Python code
:::

:::js
JavaScript code
:::
"""

python_result = _apply_conditional_rendering(source, "python")
js_result = _apply_conditional_rendering(source, "js")

print("Python version:")
print(repr(python_result))
print("\nJavaScript version:")
print(repr(js_result))
```

### Validating Build Output

After building, you can use standard Unix tools to search for expected content in output files:

```bash
# Check if Python version contains expected text
grep -q "Python code" build/oss/python/<product>/<page>.mdx && echo "Found"

# Check that JavaScript version does NOT contain Python-specific text
grep -q "Python code" build/oss/javascript/<product>/<page>.mdx || echo "Not found (correct)"
```

## Edge Cases and Advanced Scenarios

### Indented Conditional Blocks

Conditional blocks can appear inside other indented structures (lists, blockquotes, code fence content indicators, etc.). The indentation must be consistent:

```markdown
1. List item one

   :::python
   Indented Python content inside a list
   :::

2. List item two
```

The closing `:::` must have the same indentation as the opening `:::python`.

### Multiple Conditionals in Sequence

A single file may have multiple conditional blocks at the same level:

```markdown
# Setup

:::python
pip install langchain
:::

:::js
npm install langchain
:::

# Usage

:::python
from langchain import ...
:::

:::js
import { ... } from 'langchain';
:::
```

Each block is processed independently. The processor applies the conditional-resolution rule to all matches in the content.

### Blank Lines and Content Preservation

Content between the opening and closing fences is preserved exactly, including blank lines:

```markdown
:::python

First paragraph after blank line.

Second paragraph.

:::
```

After rendering for Python, the output is:

```markdown

First paragraph after blank line.

Second paragraph.

```

Empty lines at the start and end of the block are preserved.

## Related Concepts

- **Language Versioning Strategy** (`/openwiki/concepts/versioning.md`) – Comprehensive overview of the three versioning patterns and how conditional rendering fits into the pipeline
- **Preprocessing Pipeline** (`/openwiki/concepts/preprocessing.md`) – Details on how `_apply_conditional_rendering()` integrates with cross-reference resolution and link rewriting
- **Building the Documentation** (Makefile) – Command reference for `make build` and `make dev`

## References

- **Implementation** – `/pipeline/preprocessors/markdown_preprocessor.py` – Contains `_apply_conditional_rendering()` and `preprocess_markdown()`
- **Integration Tests** – `/tests/unit_tests/test_builder.py` – Full integration tests including `test_build_all_creates_managed_deep_agents_language_routes()`
- **Versioning Strategy** – `/openwiki/concepts/versioning.md` – Theory and architecture of the multi-branch versioning system
