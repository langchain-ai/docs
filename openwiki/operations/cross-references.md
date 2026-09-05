---
type: operations guide
title: Cross-Reference Links (@[ClassName] Syntax)
description: Use the @[ClassName] syntax to create resilient API reference links that update automatically with changes to the link registry, without hardcoding URLs.
tags: [documentation, cross-references, links, markdown, build-system, api-reference]
verified:
  - by: openwiki/0.5.0
    at: 2026-09-03T15:00:58.567Z
sources:
  - id: openwiki-source-17f3856bce97f37118963062
    resource: repo://pipeline/preprocessors/handle_auto_links.py
  - id: openwiki-source-dca59d03b9433eea9242c2e4
    resource: repo://pipeline/preprocessors/link_map.py
  - id: openwiki-source-06a4c757b1153b7de4f47a0e
    resource: repo://pipeline/preprocessors/markdown_preprocessor.py
generated: { by: "openwiki/0.5.0", at: "2026-09-03T15:00:58.567Z" }
---

# Cross-Reference Links: The @[ClassName] Syntax

The cross-reference system lets writers create links to API documentation using semantic references instead of hardcoded URLs. When you write `@[StateGraph]` in your markdown, the build system automatically resolves it to the appropriate API reference link based on the current scope (typically Python or JavaScript).

## Why Use Cross-References?

Hardcoding URLs to API documentation creates maintenance burden: when reference pages move, URLs break silently across hundreds of pages. The cross-reference system solves this:

- **Semantic, not positional:** You reference the API element by name, not by URL. If the reference docs restructure, update the link map once and all pages update automatically.
- **Language-aware:** The same `@[StateGraph]` reference resolves to different URLs in Python and JavaScript builds, without duplicating source content.
- **Resilient:** Missing references are logged (not silently broken), and the original `@[ClassName]` text appears in output if the reference cannot be resolved.

## Basic Syntax

### Simple Reference
```markdown
You can use @[StateGraph] to define your graph structure.
```

Becomes:
```markdown
You can use [StateGraph](https://reference.langchain.com/python/langgraph/graph/state/StateGraph) to define your graph structure.
```

### Custom Link Text
```markdown
Learn about the @[state management system][StateGraph].
```

Becomes:
```markdown
Learn about the [state management system](https://reference.langchain.com/python/langgraph/graph/state/StateGraph).
```

The format is `@[Custom Title][ClassName]`.

### With Backticks
```markdown
Use @[`StateGraph`] in your code.
```

Becomes:
```markdown
Use [`StateGraph`](https://reference.langchain.com/python/langgraph/graph/state/StateGraph) in your code.
```

Backticks are automatically preserved in the link title.

## Scope Resolution

The scope determines which API reference set is used. The build system supports two primary scopes:

- **python:** Links to `https://reference.langchain.com/python/` API reference
- **js:** Links to `https://reference.langchain.com/javascript/` API reference

### How Scope Is Determined

1. **Explicit conditional blocks:** If your page contains `:::python` or `:::js` fences, cross-references inside that block use the corresponding scope.

2. **Default scope:** If no conditional block is active, the build system uses `target_language` (passed at build time, typically "python" for unversioned content or matched to the build language for versioned content).

### Scope Persistence

Scope persists across lines until a new conditional fence is encountered:

```markdown
:::python
@[StateGraph]        # Uses Python scope
@[Command]           # Still uses Python scope
:::

@[create_agent]      # Reverts to default scope (python)

:::js
@[StateGraph]        # Uses JS scope
:::
```

### Code Block Protection

Cross-references inside code fences (```python, ~~~js, etc.) are never transformed, even if the fence appears to change scope:

```markdown
:::python
@[StateGraph]        # Transformed: Python scope

```markdown
:::js
@[StateGraph]        # NOT transformed: inside code fence
```
```

The code fence state takes precedence over scope changes.

## Link Map Organization

Link mappings are defined in `SCOPE_LINK_MAPS` in `/pipeline/preprocessors/link_map.py`, derived from the `LINK_MAPS` list. Each mapping entry contains:

- **scope:** "python", "js", or other language identifier
- **host:** Base URL (e.g., `https://reference.langchain.com/python/`)
- **links:** Dictionary mapping class/function names to relative paths

Example entry:
```python
"StateGraph": "langgraph/graph/state/StateGraph"
```

With host `https://reference.langchain.com/python/`, this resolves to:
```
https://reference.langchain.com/python/langgraph/graph/state/StateGraph
```

## Examples

The page-specific instructions list these examples:

| Reference | Use Case |
|-----------|----------|
| `@[StateGraph]` | LangGraph state machine class |
| `@[create_agent]` | Agent factory function |
| `@[ChatOpenAI]` | OpenAI chat model integration |
| `@[MemoryMiddleware]` | Deep Agents memory middleware |

Other common references include `@[Command]`, `@[AIMessage]`, `@[BaseTool]`, `@[Runnable]`, and `@[VectorStore]`.

## Handling Missing References

If a reference like `@[UnknownClass]` is not found in the link map for the current scope:

1. An **info-level log** is written with the file path and line number:
   ```
   file.mdx:42: Link 'UnknownClass' not found in scope 'python'.
   ```

2. The **original text appears verbatim** in the output:
   ```
   Use @[UnknownClass] here.
   ```

This allows writers to use semantic references even before link map entries are added, and CI logs guide the fix.

## Adding a New Reference

To add support for a new API element, follow this workflow:

### Step 1: Locate the Reference Page
Find where the API element is documented in the official reference docs. For example:
- LangGraph classes: `https://reference.langchain.com/python/langgraph/graph/state/StateGraph`
- LangChain tools: `https://reference.langchain.com/python/langchain-core/tools/`
- Custom integrations: `https://reference.langchain.com/python/langchain-anthropic/chat_models/ChatAnthropic`

Extract the relative path after the host. For `https://reference.langchain.com/python/langgraph/graph/state/StateGraph`, extract `langgraph/graph/state/StateGraph`.

### Step 2: Add to SCOPE_LINK_MAPS
Edit `/pipeline/preprocessors/link_map.py` and locate the appropriate scope in the `LINK_MAPS` list:

```python
LINK_MAPS: list[LinkMap] = [
    {
        "host": "https://reference.langchain.com/python/",
        "scope": "python",
        "links": {
            # ... existing entries ...
            "MyNewClass": "path/to/MyNewClass",  # Add here
        },
    },
    {
        "host": "https://reference.langchain.com/javascript/",
        "scope": "js",
        "links": {
            # ... existing entries ...
            "MyNewClass": "path/to/MyNewClass",  # Add if it exists in JS
        },
    },
]
```

**Key guidelines:**
- Use the **relative path** from the host, not the full URL.
- If the class exists in only one language (e.g., Python-only), add it only to that scope.
- For shared references (e.g., core LangChain types), add entries to both "python" and "js" scopes.
- If a reference points to a full URL (cross-domain), include the complete URL prefixed with "http".

### Step 3: Test
Use `@[MyNewClass]` in your documentation and build locally:

```bash
make build  # Or your build command
```

Check the logs for confirmation or errors:
- **Success:** No log entry appears; the reference is resolved.
- **Missing:** An info-level log appears listing the file, line, scope, and missing reference name.

Commit the link map change and verify the reference works in the published docs.

## Escaped References

To display a literal `@[ClassName]` without linking, escape the @ symbol:

```markdown
If you want to show the literal text \@[ClassName], use a backslash.
```

Output:
```markdown
If you want to show the literal text @[ClassName], use a backslash.
```

Escaped references work both inside and outside code blocks. The backslash is automatically removed during preprocessing.

## Interaction with Conditional Content

Cross-references work seamlessly with language-specific conditional blocks:

```markdown
:::python
Use @[StateGraph] to build your graph.
:::

:::js
Use @[StateGraph] to build your graph.
:::
```

Inside the `:::python` block, `@[StateGraph]` resolves to the Python reference. Inside the `:::js` block, it resolves to the JavaScript reference. Writers maintain a single source file; the build system handles the translation.

## Integration with the Build Pipeline

Cross-reference resolution is **Layer 2 of the markdown preprocessing pipeline** (see [Markdown Preprocessing Pipeline](/openwiki/concepts/preprocessing.md) for full details).

The pipeline applies transformations in this order:

1. **Conditional Rendering:** Language-specific blocks are resolved
<!-- openwiki: broken internal link [url] file "url" does not exist. Fix the href or restore the target, then delete this comment. -->
2. **Cross-References** (this layer): `@[ClassName]` → `[ClassName](url)`
3. UTM Link Decoration
4. Link Rewriting for Versioned Content
5. Snippet Import Rewriting
6. Source Edit Links

This means cross-references are transformed before link rewriting, so relative URLs in the link map are prefixed with the appropriate host at build time.

## Best Practices

1. **Use semantic references:** Prefer `@[StateGraph]` over hardcoding URLs. It's clearer to readers and maintainers, and automatically updates when the reference docs change.

2. **Add custom titles for readability:** When the class name alone is awkward, use `@[custom description][ClassName]` to improve prose flow:
   ```markdown
   See the @[state update method][CompiledStateGraph.update_state] documentation.
   ```

3. **Group related references:** Collect API references in a "Related API" section at the end of pages.

4. **Test missing references:** If you use a reference before it's added to the link map, the build logs will guide you. Use the logs to track down what needs to be added.

5. **Keep link map entries minimal:** Store only the relative path in the link map. Hosts are defined once per scope and automatically prepended.

6. **Document cross-repository references:** If a reference lives outside `reference.langchain.com`, store the full URL in the link map. This keeps maintenance centralized.

## Scope-Specific Mappings

The link map includes entries for multiple language ecosystems:

- **LangChain core:** `@[BaseChatModel]`, `@[Runnable]`, `@[Document]`
- **LangGraph:** `@[StateGraph]`, `@[Command]`, `@[Pregel]`
- **Deep Agents:** `@[SubAgent]`, `@[MemoryMiddleware]`, `@[FilesystemBackend]`
- **Integrations:** `@[ChatOpenAI]`, `@[ChatAnthropic]`, `@[ChatVertexAI]`
- **Utilities:** `@[AIMessage]`, `@[BaseTool]`, `@[Embeddings]`

Check `/pipeline/preprocessors/link_map.py` for the complete list of available references for your scope.

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `@[ClassName]` appears literally in output | Reference not found in link map | Add the entry to `/pipeline/preprocessors/link_map.py` for the appropriate scope. |
| Link points to wrong reference | Wrong relative path in link map | Verify the path matches the actual reference URL structure; update if needed. |
| Info log: "Link not found" | Typo in the reference name or scope mismatch | Check the reference name spelling and ensure you're using the correct scope. |
| Escaped reference `\@[ClassName]` not appearing as-is | Backslash not in source | Double-check the backslash is present in the markdown source. |
| Different URLs for Python and JS | Expected behavior | Verify both scopes have the same reference name mapped (or intentionally different targets). |

## See Also

- [Markdown Preprocessing Pipeline](/openwiki/concepts/preprocessing.md) — Full details on how preprocessing layers interact
- [Adding and Modifying Documentation Pages](/openwiki/operations/adding-pages.md) — Workflow for creating new pages with cross-references
- `/pipeline/preprocessors/handle_auto_links.py` — Implementation of cross-reference transformation
- `/pipeline/preprocessors/link_map.py` — Link map definitions and scope management
