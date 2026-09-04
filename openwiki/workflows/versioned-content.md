---
type: workflow guide
title: Writing Versioned Content (Python/JavaScript)
description: Best practices for authoring documentation that appears in both Python and JavaScript variants using conditional blocks and language-specific code examples.
tags: [versioning, language-branching, conditional-rendering, code-examples, multi-language]
verified:
  - by: openwiki/0.5.0
    at: 2026-09-03T15:00:58.567Z
sources:
  - id: openwiki-source-d0cdf44431684bdedf34705a
    resource: repo://pipeline/core/builder.py
generated: { by: "openwiki/0.5.0", at: "2026-09-03T15:00:58.567Z" }
---

# Writing Versioned Content (Python/JavaScript)

This guide explains how to write documentation that automatically generates separate Python and JavaScript variants from a single source file. The build system processes conditional blocks, rewrites links, and manages language-specific imports to create language-specific output.

## Understanding the Build Model

The documentation system builds versioned OSS content (LangChain, LangGraph, and most Deep Agents documentation) twice: once for Python output and once for JavaScript/TypeScript output. A single source file in `/src/oss/...` produces two built files:

- `/build/oss/python/...` (Python variant)
- `/build/oss/javascript/...` (JavaScript/TypeScript variant)

Language-agnostic content (Deep Agents Code, OpenWiki) builds once at `/build/oss/deepagents/code/...` or `/build/oss/openwiki/...` with no language split.

## Basic Conditional Blocks

### Writing Language-Specific Sections

Use indented fence blocks to mark content that only appears in one language:

```markdown
:::python
This section is only shown to Python users.
:::

:::js
This section is only shown to JavaScript/TypeScript users.
:::

This section appears in both versions.
```

**Key properties:**
- Blocks are indented and closed with a matching `:::` at the same indentation level
- Content between `:::python` and `:::` is removed from JavaScript builds
- Content between `:::js` and `:::` is removed from Python builds
- Content outside conditional blocks appears in both versions
- Unsupported language specifiers (neither `python` nor `js`) are left unchanged

### Escaping Conditional Markers

When writing documentation that explains the conditional syntax itself, escape the opening marker with a backslash:

```markdown
\:::python
This will appear literally as :::python in the output
\:::

\:::js
This will appear literally as :::js in the output
\:::
```

The backslash is stripped during processing, leaving literal fence syntax in the output. This is useful for:
- Documenting the syntax itself
- Showing examples of conditional blocks in tutorials
- Creating reference material about the build system

## Conditional Code Examples

### Simple Language-Specific Examples

Wrap entire code blocks in conditional fences when they differ between languages:

```markdown
### Install the package

:::python
```bash
pip install langchain
```
:::

:::js
```bash
npm install @langchain/core
```
:::
```

### Side-by-Side Comparisons

Use a neutral heading, then provide language-specific content:

```markdown
### Using tools

:::python
```python
@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
```
:::

:::js
```typescript
const add = tool(
  async (a: number, b: number) => {
    return a + b;
  },
  {
    name: "add",
    description: "Add two numbers",
  }
);
```
:::
```

### Mixed Explanatory Content and Code

Combine narrative text with language-specific code blocks:

```markdown
## Creating an agent

To create an agent, instantiate the appropriate class for your framework:

:::python
```python
from langchain.agents import create_agent

agent = create_agent(
    llm=model,
    tools=tools,
    prompt=prompt
)
```
:::

:::js
```typescript
import { createAgent } from "@langchain/langgraph";

const agent = createAgent({
  llm: model,
  tools: tools,
  prompt: prompt,
});
```
:::

You can now invoke the agent with:

:::python
```python
result = agent.invoke({"query": "hello"})
```
:::

:::js
```typescript
const result = await agent.invoke({
  query: "hello",
});
```
:::
```

## Handling Links in Versioned Content

### Automatic Link Rewriting

Don't manually prefix links to versioned products. Write unprefixed paths, and the build system automatically rewrites them:

```markdown
<!-- openwiki: broken internal link [/oss/langgraph/overview] file "/oss/langgraph/overview" does not exist. Fix the href or restore the target, then delete this comment. -->
See the [LangGraph overview](/oss/langgraph/overview) for more details.
```

During build:
- Python build rewrites to: `/oss/python/langgraph/overview`
- JavaScript build rewrites to: `/oss/javascript/langgraph/overview`

### Language-Agnostic Product Links

Always use unprefixed URLs for language-agnostic products; these are never rewritten:

```markdown
<!-- openwiki: broken internal link [/oss/deepagents/code/overview] file "/oss/deepagents/code/overview" does not exist. Fix the href or restore the target, then delete this comment. -->
See [Deep Agents Code](/oss/deepagents/code/overview) for details.
See [OpenWiki](/oss/openwiki/) for information.
```

These links remain `/oss/deepagents/code/...` and `/oss/openwiki/...` in both builds.

### External and Unversioned Links

Links to external sites, images, and unversioned content are unaffected:

```markdown
<!-- openwiki: broken internal link [/langsmith/overview] file "/langsmith/overview" does not exist. Fix the href or restore the target, then delete this comment. -->
[Visit LangSmith](/langsmith/overview)
[API Reference](https://example.com)
![Example image](/oss/images/diagram.png)
```

## Importing Language-Specific Snippets

### Snippet Sources

Snippets are short reusable markdown fragments stored in `/src/snippets/`. The build system generates language-specific copies:

- `/src/snippets/example.mdx` → `/build/snippets/python/example.mdx` (Python build)
- `/src/snippets/example.mdx` → `/build/snippets/javascript/example.mdx` (JavaScript build)
- `/build/snippets/example.mdx` → Python-default copy (for unversioned pages)

### Importing Snippets in Versioned Pages

In versioned pages (those built for both Python and JavaScript), import snippets without the language prefix. The build system automatically inserts the language path:

```mdx
import MySnippet from '/snippets/my-snippet.mdx'
```

During build:
- Python build rewrites to: `import MySnippet from '/snippets/python/my-snippet.mdx'`
- JavaScript build rewrites to: `import MySnippet from '/snippets/javascript/my-snippet.mdx'`

### Importing Snippets in Unversioned Pages

In unversioned pages (language-agnostic content), import snippets at the base path or with the `python/` prefix:

```mdx
import MySnippet from '/snippets/my-snippet.mdx'
// or explicitly:
import MySnippet from '/snippets/python/my-snippet.mdx'
```

Both work; already-prefixed imports are left unchanged by the rewrite system.

### Creating Snippet Sources

If a snippet needs to be language-specific, author it with conditional blocks:

```mdx
<!-- /src/snippets/installation.mdx -->

:::python
```bash
pip install langchain
```
:::

:::js
```bash
npm install @langchain/core
```
:::
```

This single source snippet becomes language-specific when built, producing `/snippets/python/installation.mdx` and `/snippets/javascript/installation.mdx`.

## Testing in Local Development

### Verify Conditional Rendering

When you build or start the development server with `make dev`, check that conditional blocks are properly resolved:

1. **Python variant**: Navigate to the `/oss/python/...` route in your browser. You should see only `:::python` content and no `:::js` sections.
2. **JavaScript variant**: Navigate to the `/oss/javascript/...` route. You should see only `:::js` content and no `:::python` sections.
3. **Shared content**: Verify that non-conditional text appears in both variants.

### Language Selector

The documentation site displays a language dropdown (Python/TypeScript) at the top. Switch between languages to verify:
- Content inside matching conditional blocks appears
- Content inside non-matching blocks is absent
- Links are rewritten correctly for the target language
- Snippet imports resolve to the correct language variant

### Local Build Testing

Build the documentation locally to catch link and snippet issues early:

```bash
make build
```

Check the build output in `/build/oss/python/` and `/build/oss/javascript/` to verify:
- Conditional blocks are properly removed
- Links are rewritten with language prefixes
- Snippet imports are rewritten with language paths

## Fallback for Language Parity Issues

When a feature is only available in one language, document it with a note:

```markdown
:::python
```python
from langchain.agents import create_agent
agent = create_agent(...)
```
:::

:::js
<Note>
    This feature is not yet available in TypeScript. See the Python variant for an example.
</Note>
:::
```

Alternatively, provide a note about the feature gap:

```markdown
This feature is currently available in Python only. TypeScript support is coming soon.
```

## Common Patterns

### Parameter Names That Differ

When parameter names differ between languages, use conditional blocks:

```markdown
Call the function with the required parameters:

:::python
- `model`: The LLM instance
- `tools`: List of tools the agent can use
:::

:::js
- `llm`: The language model instance
- `tools`: Array of tools the agent can invoke
:::
```

### Error Messages and Diagnostics

When error messages or debugging output differs:

```markdown
If you encounter an error, check the output:

:::python
```
ValueError: Model not initialized
```
:::

:::js
```
Error: Model not initialized
```
:::
```

### Import Statements

Always show language-specific imports:

```markdown
### Import the module

:::python
```python
from langchain.tools import tool
```
:::

:::js
```typescript
import { tool } from "@langchain/core/tools";
```
:::
```

### API Reference Links

Use semantic cross-references (`@[ClassName]`) instead of hardcoding URLs. These resolve to language-specific API docs:

```markdown
See @[StateGraph] for details on graph state management.
```

## Best Practices

1. **Keep parity in mind**: Ensure documentation covers both languages equally unless a feature is truly unavailable.

2. **Use neutral headings**: When heading introduces content that differs by language, avoid language-specific headings. The conditional blocks handle the language split.

3. **Don't hardcode language prefixes**: Write `/oss/langgraph/overview` not `/oss/python/langgraph/overview`. Let the preprocessor handle language routing.

4. **Test both variants**: Check that the Python and JavaScript tabs both render correctly in the dev server before submitting.

5. **Keep code current**: If you update a code example for one language, consider whether the other language example needs updating too.

6. **Document assumptions**: If Python and JavaScript implementations differ significantly, explain the differences clearly.

7. **Use code highlighting carefully**: Conditional blocks protect regular code fences (``` or ~~~) from being processed as conditional content. You can nest code blocks inside conditional fences safely.

8. **Escape when needed**: Only use backslash escapes (`\:::`) when documenting the syntax itself, not in regular content.

## Conditional Block Invariants

The preprocessor enforces these rules:

- **Code fence protection**: Content inside triple-backtick or triple-tilde code blocks is never processed as conditional content. If you have `:::python` inside a code fence, it's treated as literal text.
- **Indentation matching**: Conditional blocks are matched at the same indentation level. A `:::python` block must close with `:::` at the same indentation.
- **Nested conditionals not supported**: The innermost unescaped `:::` closes the current block. Nested conditionals like `:::python` → `:::js` → `:::` are not supported.
- **Order preservation**: All transformations occur in a strict order: conditional rendering first, then cross-references, then link rewriting, then snippet import rewriting.

## Troubleshooting

### Conditional Block Not Working

**Problem**: A `:::python` block appears in the JavaScript build.

**Solution**:
- Check indentation: The closing `:::` must match the indentation of `:::python`.
- Verify the fence is not inside a code block. If `:::python` is inside triple backticks, it's literal text, not a conditional marker.
- Check that the file is in a versioned OSS path (`/src/oss/langgraph/`, `/src/oss/langchain/`, etc.), not an unversioned path.

### Links Not Rewriting

**Problem**: A link like `/oss/langgraph/overview` appears without the language prefix in the build output.

**Solution**:
- Check that the link path starts with `/oss/` and doesn't already contain `/python/` or `/javascript/`.
- Verify the page is in a versioned OSS path that gets built for both languages.
- Check for typos in the URL path.

### Snippet Import Not Found

**Problem**: A build error says the snippet file doesn't exist.

**Solution**:
- Verify the snippet source exists at `/src/snippets/my-snippet.mdx`.
- Check that you're importing the unversioned path (`/snippets/my-snippet.mdx`), not the language-specific path (which is added during build).
- If the snippet contains language-specific content, ensure it's inside conditional blocks so both language variants are generated.

## Related Documentation

<!-- openwiki: broken internal link [/oss/openwiki/concepts/versioning.md] file "/oss/openwiki/concepts/versioning.md" does not exist. Fix the href or restore the target, then delete this comment. -->
- [Language Versioning Strategy](/oss/openwiki/concepts/versioning.md) — Deep dive into how the build system creates language-specific variants
<!-- openwiki: broken internal link [/oss/openwiki/concepts/preprocessing.md] file "/oss/openwiki/concepts/preprocessing.md" does not exist. Fix the href or restore the target, then delete this comment. -->
- [Markdown Preprocessing Pipeline](/oss/openwiki/concepts/preprocessing.md) — Complete reference for all six preprocessing layers
- [Local Development Workflow](/openwiki/workflows/local-development.md) — How to test changes locally in both Python and JavaScript builds
