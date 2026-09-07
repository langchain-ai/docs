---
type: operations guide
title: Adding and Modifying Documentation Pages
description: Safely choose a documentation routing domain, add or move an MDX page and its navigation entry, preserve old URLs with redirects, and validate the generated site.
tags: [documentation, operations, navigation, workflow, build-system]
sources:
  - id: openwiki-source-8037e2358a2c4f9b2c722a11
    resource: repo://AGENTS.md
  - id: openwiki-source-012f2c78e3b1446dfc35803f
    resource: repo://Makefile
  - id: openwiki-source-6e6efa1569f158fcdb678ef0
    resource: repo://pipeline/cli.py
  - id: openwiki-source-b481a230af378c0c50ed9994
    resource: repo://pipeline/commands/dev.py
  - id: openwiki-source-d0cdf44431684bdedf34705a
    resource: repo://pipeline/core/builder.py
  - id: openwiki-source-06a4c757b1153b7de4f47a0e
    resource: repo://pipeline/preprocessors/markdown_preprocessor.py
  - id: openwiki-source-8d071ef0669cd8d2d79c6c15
    resource: repo://pipeline/tools/links.py
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
  - id: openwiki-source-3988d52ac8d59fd5a6618960
    resource: repo://scripts/check_removed_pages_redirects.py
  - id: openwiki-source-a9a8730b7e43a5ad2d0af4f1
    resource: repo://src/docs.json
  - id: openwiki-source-a39cb5ba9006abfe6280b6f8
    resource: repo://src/oss/openwiki/cli-reference.mdx
generated: { by: "openwiki/0.4.3", at: "2026-09-07T08:24:09.165Z" }
verified:
  - by: openwiki/0.4.3
    at: 2026-09-07T08:24:09.165Z
---

# Adding and Modifying Documentation Pages

A documentation change has two source-of-truth concerns: the MDX/Markdown file under `src/` supplies content, while `src/docs.json` supplies the published route and navigation placement. The build directory is generated output: never edit `build/`; make the source and configuration changes, then regenerate it.

## Choose the source and route domain first

Choose based on the page's audience and route semantics, not the label of a navigation menu. Navigation labels intentionally do not always match source directories, and lifecycle menus can contain both OSS and LangSmith pages.

| Content kind | Source location | Generated routes | Authoring implications |
| --- | --- | --- | --- |
| Versioned OSS | Most of `src/oss/`, including `langchain/`, `langgraph/`, and `deepagents/` | `/oss/python/...` and `/oss/javascript/...` | One source page is built twice. Use `:::python` and `:::js` only where content differs. |
| Language-agnostic OSS | `src/oss/openwiki/` and `src/oss/deepagents/code/` | `/oss/openwiki/...` and `/oss/deepagents/code/...` | The page is built once, with Python as the conditional-content target. Do not add a language segment to its route. |
| LangSmith | `src/langsmith/` | Usually `/langsmith/...` | Built once with Python preprocessing. A root-level `managed-deep-agents*.mdx` file is the exception: it emits `/langsmith/python/...` and `/langsmith/javascript/...` only. |

<!-- openwiki: broken internal link [/openwiki/workflows/versioned-content] file "/openwiki/workflows/versioned-content" does not exist. Fix the href or restore the target, then delete this comment. -->
For an OSS page that appears in both language dropdowns, use an unprefixed source link such as `/oss/langgraph/overview`; preprocessing inserts `python` or `javascript` in the corresponding output. In contrast, links to OpenWiki and Deep Agents Code must remain their unprefixed, language-agnostic routes, for example `/oss/openwiki/overview`. See [Writing Versioned Content](/openwiki/workflows/versioned-content) for conditional blocks and snippet behavior.

## Add a page

<!-- openwiki: broken internal link [/openwiki/architecture/source-map] file "/openwiki/architecture/source-map" does not exist. Fix the href or restore the target, then delete this comment. -->
1. **Locate its actual navigation home.** Start with the current `src/docs.json` entry near related pages, then use [the source map](/openwiki/architecture/source-map) if the menu label and directory differ. Follow the existing product → menu item → dropdown (when present) → tab → group nesting and ordering. `src/docs.json` is authoritative; do not infer placement from a directory name.
2. **Create the MDX source beneath `src/`.** Use the domain selected above and a route-oriented filename. Every MDX page needs YAML frontmatter with a plain-text `title` and `description`; descriptions must not contain Markdown. Add other established page-specific fields only when appropriate. Do not author OpenWiki-managed `generated`, `verified`, `sources`, or `timestamp` fields.

   ```mdx
   ---
   title: Your Page Title
   description: A concise plain-text summary of what readers learn on this page.
   ---

   # Your Page Title
   ```

3. **Add the page path to `src/docs.json`.** Use the route path without `/src/` or the `.mdx` extension. For example, `src/oss/openwiki/deployment.mdx` is represented as `"oss/openwiki/deployment"`. Insert it in the group found in step 1; a page file that is absent from this configuration is not navigable as intended. Add a `keywords` field only if the surrounding page convention or task requires it—it is not one of the repository's universal frontmatter requirements.
<!-- openwiki: broken internal link [/openwiki/operations/cross-references] file "/openwiki/operations/cross-references" does not exist. Fix the href or restore the target, then delete this comment. -->
4. **Add links deliberately.** Use the published route for cross-page links, preserve anchors when needed, and use language-neutral OSS links only for content that is actually versioned. Use `@[Name]` for eligible API reference links and run `make check-cross-refs` when adding or changing them. The [cross-reference guide](/openwiki/operations/cross-references) covers resolution rules.

### Navigation path versus source path

A `docs.json` path is normally an output route, not necessarily a literal source filename. In particular, a navigation entry such as `oss/python/langgraph/overview` can be backed by the shared `src/oss/langgraph/overview.mdx` because the builder emits the language variants. Conversely, OpenWiki entries retain `oss/openwiki/...` because they are not duplicated. This distinction prevents creating redundant `src/oss/python/` copies of shared pages.

## Move, rename, or remove a page

Treat a move as a URL migration, not merely a filesystem rename.

### 1. Preview and perform the source move

From the repository root, preview the built-in mover before changing files:

```bash
python pipeline/cli.py mv src/langsmith/evaluation.mdx src/langsmith/deploy/evaluation.mdx --dry-run
```

Then run the command without `--dry-run` after reviewing the output:

```bash
python pipeline/cli.py mv src/langsmith/evaluation.mdx src/langsmith/deploy/evaluation.mdx
```

The mover scans `src/` for Markdown, MDX, and notebook Markdown-cell links to the old file and rewrites relative links. It also recalculates relative links inside the moved document. It does not understand every possible textual URL form, nor does it update navigation or redirects, so inspect the diff and search for old route references afterward.

### 2. Update navigation and preserve old URLs

Change or remove the matching `src/docs.json` page entry in the same change. When a page's old source is deleted and its navigation path disappears, add a redirect object to the top-level `redirects` array in `src/docs.json`:

```json
{
  "source": "/langsmith/evaluation",
  "destination": "/langsmith/deploy/evaluation"
}
```

Use published URL paths, including language prefixes when an old versioned route requires its own redirect. This preserves bookmarks and inbound links. The redirect checker compares the base and proposed navigation: it allows a removed navigation entry without a redirect only while a corresponding source file still exists; otherwise it fails. It also fails when any configured page cannot be resolved to a `.mdx` or `.md` source file (including the shared-source mapping for versioned OSS paths).

If a page is only being regrouped and remains at the same route with its source file intact, update its navigation position but do not add an unnecessary redirect. If a page is genuinely removed, redirect it to the closest useful successor rather than a generic page.

## Validate the generated site

Use generated output to validate; do not repair output directly.

1. Run `make dev` and browse `http://localhost:3000`. It performs an initial build, watches `src/`, and starts Mintlify from `build/`. Verify the new page's route, title and rendering, its exact navigation location, and both Python and JavaScript variants for versioned content.
2. Run a clean full generation with `make build` when you need a reproducible result. The builder clears and recreates `build/`, so any manual change there is discarded.
3. Run `make broken-links`. It depends on `build`, runs Mintlify's broken-link checker against generated output, and filters known false positives from deploy-time OpenAPI pages and snippets. Use `make broken-links-with-anchors` when the change adds or changes fragment links.
4. Run focused structural checks when applicable:

   ```bash
   make check-cross-refs
   uv run pytest tests/unit_tests/test_check_removed_pages_redirects.py -vv
   ```

   The focused redirect test protects the navigation/source-file and removed-page redirect policy; the site build and link checks confirm the end-to-end generated routes.

## Completion checklist

- [ ] The page is under the correct `src/` domain for its routing and language behavior.
- [ ] Its frontmatter has plain-text `title` and `description`, and no human-authored OpenWiki control fields.
- [ ] `src/docs.json` contains the extensionless route in the current, correct product/menu/tab/group location.
- [ ] A move updated relative links, navigation, direct route links, and a redirect for every retired URL whose source was deleted.
- [ ] `make dev` was used to inspect rendering and navigation; versioned pages were checked in both language variants.
- [ ] `make build` and `make broken-links` pass; anchor and cross-reference checks were run when relevant.

## See also

<!-- openwiki: broken internal link [/openwiki/architecture/source-map] file "/openwiki/architecture/source-map" does not exist. Fix the href or restore the target, then delete this comment. -->
- [Source map](/openwiki/architecture/source-map)
<!-- openwiki: broken internal link [/openwiki/operations/cli-tools] file "/openwiki/operations/cli-tools" does not exist. Fix the href or restore the target, then delete this comment. -->
- [CLI tools](/openwiki/operations/cli-tools)
<!-- openwiki: broken internal link [/openwiki/operations/cross-references] file "/openwiki/operations/cross-references" does not exist. Fix the href or restore the target, then delete this comment. -->
- [Cross-reference links](/openwiki/operations/cross-references)
<!-- openwiki: broken internal link [/openwiki/workflows/local-development] file "/openwiki/workflows/local-development" does not exist. Fix the href or restore the target, then delete this comment. -->
- [Local development](/openwiki/workflows/local-development)
<!-- openwiki: broken internal link [/openwiki/workflows/versioned-content] file "/openwiki/workflows/versioned-content" does not exist. Fix the href or restore the target, then delete this comment. -->
- [Writing versioned content](/openwiki/workflows/versioned-content)
<!-- openwiki: broken internal link [/openwiki/testing/test-overview] file "/openwiki/testing/test-overview" does not exist. Fix the href or restore the target, then delete this comment. -->
- [Testing overview](/openwiki/testing/test-overview)
