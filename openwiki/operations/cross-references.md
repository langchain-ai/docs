---
type: operations guide
title: Cross-Reference Resolution
description: Author scoped `@[reference]` links, understand preprocessing and unresolved-reference behavior, and validate API mappings before changing documentation or API destinations.
tags: [documentation, cross-references, api-links, validation]
verified:
  - by: openwiki/0.4.3
    at: 2026-11-23T08:07:24.438Z
sources:
  - id: openwiki-source-164e2da859b5277df81c7d94
    resource: repo://.github/workflows/ci.yml
  - id: openwiki-source-012f2c78e3b1446dfc35803f
    resource: repo://Makefile
  - id: openwiki-source-17f3856bce97f37118963062
    resource: repo://pipeline/preprocessors/handle_auto_links.py
  - id: openwiki-source-dca59d03b9433eea9242c2e4
    resource: repo://pipeline/preprocessors/link_map.py
  - id: openwiki-source-06a4c757b1153b7de4f47a0e
    resource: repo://pipeline/preprocessors/markdown_preprocessor.py
  - id: openwiki-source-0a0a6c8d7a88288e6b6b9b5b
    resource: repo://scripts/check_cross_refs.py
  - id: openwiki-source-867d24ecd094a73112272b9b
    resource: repo://src/oss/langchain/mcp/index.mdx
  - id: openwiki-source-3b99ef795fb96770516215eb
    resource: repo://src/oss/langchain/mcp/tools.mdx
  - id: openwiki-source-2ecfcd33b729fccd843ab705
    resource: repo://tests/unit_tests/test_handle_auto_links.py
generated: { by: "openwiki/0.4.3", at: "2026-11-23T08:07:24.438Z" }
---

# Cross-Reference Resolution

The `@[Name]` syntax is a source-level Markdown/MDX reference to API documentation. Authors name an API symbol semantically; preprocessing resolves it against the active language scope instead of embedding a hardcoded API URL. The registry for these API destinations is `pipeline/preprocessors/link_map.py`. Use ordinary Markdown links for documentation-site routes, redirects, and anchors.

## Author a reference

Outside a regular fenced code block, the resolver accepts these forms:

```markdown
Use @[StateGraph] to define a graph.
Read @[the graph reference][StateGraph].
Pass @[`StateGraph`] to preserve code formatting in the link title.
```

<!-- openwiki: broken internal link [url] file "url" does not exist. Fix the href or restore the target, then delete this comment. -->
A successful lookup becomes a Markdown `[title](url)` link:

- `@[StateGraph]` uses the map key as the title.
- `@[the graph reference][StateGraph]` uses the supplied custom title.
- `@[`StateGraph`]` uses `` `StateGraph` `` as the title.
- A backticked key in a custom-title form selects the same key, but does not add backticks to the supplied title.

To display the syntax literally, escape the marker:

```markdown
Write \@[StateGraph] when documenting the syntax.
```

The resolver skips the escaped marker, then removes the escape during its final unescaping pass. Readers therefore see literal `@[StateGraph]`, not a link.

## Select a scope and resolve the reference

`preprocess_markdown()` determines the target language from its argument, then `TARGET_LANGUAGE`, then `python`. Unless `default_scope` is supplied, that target is also the initial cross-reference scope. Cross-reference replacement runs before UTM decoration and conditional rendering, while conditional fence lines are still available to the resolver.

```mermaid
flowchart TD
    Source["Markdown or MDX source"] --> Initial["Initial scope: default_scope or target language"]
    Initial --> Line["Read next line"]
    Line --> Code{"Matches code fence"}
    Code -->|"yes"| Toggle["Toggle code-fence state and preserve line"]
    Toggle --> Line
    Code -->|"no, already inside fence"| Preserve["Preserve line without resolving references"]
    Preserve --> Line
    Code -->|"no"| Conditional{"Matches :::language or :::"}
    Conditional -->|"yes"| Scope["Set lowercased language scope, or reset to default"]
    Scope --> Line
    Conditional -->|"no"| Reference{"Contains unescaped @[reference]"}
    Reference -->|"no"| Keep["Preserve line"]
    Keep --> Line
    Reference -->|"yes"| Map{"Exact key exists in active scope map"}
<!-- openwiki: broken internal link [url] file "url" does not exist. Fix the href or restore the target, then delete this comment. -->
    Map -->|"yes"| Link["Emit Markdown [title](url)"]
    Map -->|"no"| Literal["Log location and retain original marker"]
    Link --> Line
    Literal --> Line
```

*The diagram shows the line-oriented autolink pass; later conditional rendering may remove a language block.*

A `:::python` or `:::js` line changes the active scope for following lines. A bare `:::` resets it to the default scope. Scope labels are lowercased, but the flattened maps contain only `python` and `js`; use those supported labels around semantic references. Map keys themselves are exact and case-sensitive.

Language fences let the same source key resolve to different destinations without duplicating prose. For example, both maps contain `MCPAdapter`, while Python and JavaScript expose the method aliases `MCPAdapter.list_tools` and `MCPAdapter.listTools`. Put each language-specific reference in its corresponding fence. In shared, unfenced content, a key must exist in both maps.

`global` is not an authoring scope. If it reaches `_transform_link()`, the resolver logs an error and falls back to `python`; combined global-scope support is not implemented.

## Fence and failure boundaries

The autolink pass recognizes regular code fences beginning with at least three backticks or tildes. It toggles a single fence-state flag on every matching line, preserves both the delimiter and its contents, and gives code-fence state precedence over conditional scope changes. Keep these fences balanced: an unclosed recognized fence leaves all remaining lines untransformed.

This protection is limited to autolink replacement. Conditional-fence validation and rendering scan the whole document without regular code-fence state. Consequently, an unescaped complete `:::python ... :::` or `:::js ... :::` sequence in a code example can still be interpreted during the final rendering stage. Escape conditional syntax that must be shown literally. Conditional validation raises `ValueError` for nested openings, stray closers, or an unclosed block; supported blocks are then retained only when their language matches the target, while unsupported conditional blocks remain unchanged.

A missing map key is non-fatal during preprocessing. `_transform_link()` logs an info-level message containing the file, line, key, and active scope, returns `None`, and the original marker remains in output. Treat that output as a source defect and run the validator rather than relying on a successful build.

## Maintain `LINK_MAPS`

`LINK_MAPS` is a list of entries with:

- `scope`: the language identifier (`python` or `js`);
- `host`: the base API-reference URL; and
- `links`: a mapping from exact author-facing names to relative destinations.

At import time, `_enumerate_links()` flattens these entries into `SCOPE_LINK_MAPS`, grouping by scope and prefixing relative paths with each entry's host. Multiple API hosts can contribute to one language scope, and one semantic key can resolve to different destinations by language.

When adding or changing an API mapping:

1. Identify the exact author-facing key and intended scope or scopes.
2. Add or correct that key in the appropriate `LINK_MAPS` dictionary, preferably as a path relative to its entry's `host`.
3. For an unfenced reference in shared `src/oss/` content, ensure the key exists in both maps. Otherwise, fence the language-specific use with `:::python` or `:::js`.
4. Run `make check-cross-refs` and the focused resolver/checker tests.

Correct an API move in the map rather than changing every consumer when the semantic alias remains valid. The map is not a documentation-route registry; use an ordinary link for a guide page, redirect, anchor, or externally owned destination. See [Reference Documentation Boundaries](/openwiki/integrations/reference-docs.md) for API-reference ownership boundaries.

## Validate source references

Run:

```bash
make check-cross-refs
```

The Make target runs `scripts/check_cross_refs.py` over `.md` and `.mdx` files beneath `src/`. The validator reports each unresolved source-relative file, line, reference name, and applicable scope, then exits with status 1. It is a source-level map-membership check, not a full preprocessor simulation.

Default scopes are derived from the source path:

| Source location | Required scope for an unfenced reference |
| --- | --- |
| `oss/python/` | `python` |
| `oss/javascript/` | `js` |
| Other `oss/` content | `python` and `js` |
| Non-OSS content | `python` |

A supported `:::python` or `:::js` fence narrows checking to that scope. A bare or unsupported conditional fence restores the path-derived defaults. The checker requires an unfenced shared-OSS reference to resolve in **all** applicable scopes, preventing a symbol present in only one language map from silently passing.

The checker shares the resolver's reference and code-fence patterns. It skips `snippets/code-samples/`, paths containing `node_modules`, escaped references, and content inside recognized code fences. Invalid UTF-8 files are warned about and skipped. As in preprocessing, an unclosed recognized code fence excludes the rest of the file from checking. Unsupported conditional labels are especially unsafe: the checker restores path-derived scopes, while the resolver selects the unsupported lowercased label, whose map is empty.

## Use the right checks

Source validation and generated-site link checking are separate:

- `make check-cross-refs` checks symbolic `@[Name]` references against local scoped maps.
- `make broken-links` builds the site and runs Mintlify with redirect checking.
- `make broken-links-with-anchors` additionally checks anchors.

A passing site-link check does not prove that a semantic name exists in `SCOPE_LINK_MAPS`, and a passing map check does not prove that a generated route or anchor is reachable. The rendered-site targets invoke Mintlify with redirect checking; the anchor variant adds anchor checking.

After changing resolver, map, scope, or validator behavior, run:

```bash
uv run pytest tests/unit_tests/test_handle_auto_links.py tests/unit_tests/test_check_cross_refs.py -vv
make check-cross-refs
```

The focused tests cover replacement, titled and backticked forms, escapes, code-fence protection, conditional-looking content inside code, unclosed fences, path-derived scopes, shared-OSS all-scope requirements, multiple references on a line, and exclusions. CI installs the test dependency group and runs `make check-cross-refs` as a dedicated gate.

| Symptom | Action |
| --- | --- |
| Literal `@[Name]` remains after preprocessing | Check the exact, case-sensitive key and active scope; add or correct the scoped map entry if appropriate. |
| Shared OSS content fails validation | Add a compatible key to both maps, or fence the language-specific use. |
| Later references are neither resolved nor checked | Find and close an earlier regular code fence. |
| A site route or anchor fails while map validation passes | Run the appropriate rendered-site check and repair the generated-route link or redirect. |
| Mintlify passes but a symbolic name fails | Run `make check-cross-refs` and repair the source name or map. |

For the broader preprocessing sequence, see [Preprocessing and Link Resolution](/openwiki/concepts/preprocessing.md). For reference-site integration boundaries, see [Reference Documentation Boundaries](/openwiki/integrations/reference-docs.md).
