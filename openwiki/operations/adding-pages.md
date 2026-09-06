---
type: operations guide
title: Adding, Moving, and Retiring Documentation Pages
description: Safely add, move, reorganize, or retire documentation pages by selecting the correct source branch, updating docs.json navigation and redirects, and validating generated output.
tags: [documentation, operations, navigation, redirects, build-system]
sources:
  - id: openwiki-source-2ff9d7e39bfac05172340de7
    resource: repo://.github/workflows/check-removed-pages-redirects.yml
  - id: openwiki-source-8037e2358a2c4f9b2c722a11
    resource: repo://AGENTS.md
  - id: openwiki-source-012f2c78e3b1446dfc35803f
    resource: repo://Makefile
  - id: openwiki-source-6e6efa1569f158fcdb678ef0
    resource: repo://pipeline/cli.py
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
  - id: openwiki-source-7471cbec862ab43f765444c7
    resource: repo://src/oss/openwiki/overview.mdx
  - id: openwiki-source-eed181414ab9190a75c7447b
    resource: repo://tests/unit_tests/tools/test_move_files.py
generated: { by: "openwiki/0.4.3", at: "2026-09-06T08:18:19.246Z" }
verified:
  - by: openwiki/0.4.3
    at: 2026-09-06T08:18:19.246Z
---

# Adding, Moving, and Retiring Documentation Pages

A page change has two separate contracts: the authored source under `src/`, which determines generated routes, and the navigation and compatibility configuration in `src/docs.json`. Select the source branch before creating or moving a file, then make the matching navigation and redirect changes manually. Never edit `build/`: it is regenerated output deployed by Mintlify.

## Choose the source branch

Use the page's build and language behavior, not its sidebar label, to select its source location. The build creates Python and JavaScript variants for ordinary shared OSS content, but OpenWiki and Deep Agents Code are explicit unversioned exceptions.

| Content | Author under | Published route behavior |
| --- | --- | --- |
| Shared LangChain, LangGraph, and most Deep Agents content | `src/oss/langchain/`, `src/oss/langgraph/`, or `src/oss/deepagents/` | One source is built at both `/oss/python/...` and `/oss/javascript/...`. |
| Language-specific OSS content | `src/oss/python/` or `src/oss/javascript/` | Only the matching language route is emitted. |
| OpenWiki | `src/oss/openwiki/` | One unversioned `/oss/openwiki/...` route. |
| Deep Agents Code | `src/oss/deepagents/code/` | One unversioned `/oss/deepagents/code/...` route. |
| Ordinary LangSmith content | `src/langsmith/` | One unversioned `/langsmith/...` route. |
| Managed Deep Agents | `src/langsmith/managed-deep-agents*.mdx` | Special case: Python and JavaScript `/langsmith/...` variants are emitted. |

For shared OSS pages, put language-specific prose and examples in `:::python` and `:::js` blocks. The preprocessor keeps the block matching the target build and removes the other. OpenWiki and Deep Agents Code are built once with the Python target, so do not place them in a language-specific source tree merely to change their sidebar location.

<!-- openwiki: broken internal link [/openwiki/operations/cross-references] file "/openwiki/operations/cross-references" does not exist. Fix the href or restore the target, then delete this comment. -->
Use unprefixed URLs when linking to unversioned OSS products, for example `/oss/openwiki/quickstart` and `/oss/deepagents/code/...`. The OSS link rewriter deliberately leaves those routes unversioned. For API-reference links and their validation, see [Cross-reference links](/openwiki/operations/cross-references).

## Add a page

To add an authored page:

1. Create an `.mdx` file in the source branch selected above. New notebooks are not recommended.
2. Begin the file with YAML frontmatter containing at least a clear `title` and plain-text `description`. Existing page conventions may also use fields such as `sidebarTitle`, `keywords`, or `mode`.
3. Do not put Markdown, links, backticks, or formatting in `description`. Do not author OpenWiki-managed `generated`, `verified`, `sources`, or timestamp fields.
4. Add the page to `src/docs.json`. This is required even when a source file already builds successfully.

```mdx
---
title: Clear page title
description: Concise plain-text summary of the page.
---

# Clear page title
```

### Place the page in navigation

`src/docs.json` is the authoritative navigation and route configuration. Its current structure begins with two `navigation.products`; each product has `menu` items, and an item can contain direct `pages`, language `dropdowns` with `tabs`, or tabs and nested groups. The identifier in a `pages` array is a built page path, without the source `src/` prefix or file extension.

Do not infer the location from the source directory. For example, the OpenWiki source directory appears in the Build menu's OpenWiki tab, while `src/langsmith/fleet/` appears as No-code agents. A shared LangGraph source is listed once in each language dropdown as `oss/python/...` and `oss/javascript/...`; an OpenWiki entry remains `oss/openwiki/...`.

<!-- openwiki: broken internal link [/openwiki/architecture/source-map] file "/openwiki/architecture/source-map" does not exist. Fix the href or restore the target, then delete this comment. -->
Find a neighboring entry in the intended product, menu item, tab, and group, then add the correct identifier while preserving ordering and nesting. A group can itself contain nested groups, and some groups use `root` to designate their landing page. Consult [Source, Navigation, and Output Map](/openwiki/architecture/source-map) before reorganizing a non-obvious section.

## Move or rename a page

Run the move command from the repository checkout, first as a preview:

```bash
python pipeline/cli.py mv src/langsmith/old-name.mdx src/langsmith/new-location/new-name.mdx --dry-run
```

After reviewing the reported changes, run the same command without `--dry-run`:

```bash
python pipeline/cli.py mv src/langsmith/old-name.mdx src/langsmith/new-location/new-name.mdx
```

`docs mv` finds the Git root and treats its `src/` directory as the documentation tree. It scans `.md`, `.mdx`, and notebook markdown cells for Markdown links resolving to the old source file, rewrites them relative to each referring file, then moves the file. It also recalculates relative links inside the moved Markdown file or notebook, preserves anchors, creates destination directories, and records the move in `link_changes.jsonl`. Dry-run reports both incoming-link and moved-file link changes without writing or moving anything.

### Complete the manual work

`docs mv` only moves a file and rewrites resolvable Markdown links. It does not update `src/docs.json`, its `redirects` array, navigation labels, arbitrary URL strings, or other configuration. Complete a move manually:

1. Replace the old navigation identifier with the new built route in the correct `docs.json` location. If the route's language behavior changed, update every relevant Python, JavaScript, or unversioned entry rather than copying the old identifier.
2. Add a redirect from the former public route to the replacement route in the top-level `redirects` array. Keep a language-prefixed source and destination for a versioned route. Point retired Managed Deep Agents URLs at the appropriate language-prefixed replacement.
3. Search for and update references that the command cannot recognize, especially absolute site URLs, component properties, JSON values, and prose that names the old route.
4. Run the verification sequence below.

A move can preserve a source file while removing it from navigation. In that case, it remains reachable and may not need a redirect, but decide deliberately whether its historical public URL should continue to be supported.

## Retire or replace a page

Retiring a page means removing its navigation entry and deleting its source only when it is no longer meant to be reachable. Before deletion, choose an existing replacement URL. Remove or update inbound references and add a top-level `docs.json` redirect:

```json
{
  "source": "/old-route",
  "destination": "/replacement-route"
}
```

The removed-pages workflow runs on pull requests targeting `main`. It loads `src/docs.json` from the pull request base commit and head, then verifies that configured page identifiers resolve to an existing `.mdx` or `.md` source file. For pages removed from navigation whose source also no longer exists, it requires a matching redirect source. It accepts normalized `.mdx` paths and `:path*` redirect sources. A failure comments the checker output on the pull request and fails the workflow.

This check is a guardrail, not a substitute for reviewing public route compatibility: use a redirect whenever a moved or retired route should keep working for bookmarks and inbound links.

## Verify the change

Run the narrowest useful checks while editing, then validate the generated site. `make dev` installs npm dependencies, invokes the pipeline in development mode, and serves the rebuilt site locally. Inspect the changed page, its sidebar placement, and both language variants when applicable.

```bash
make dev
```

Before merging, build and check generated links:

```bash
make build
make broken-links
make broken-links-with-anchors
make check-cross-refs
make lint_prose FILES="src/path/to/changed-page.mdx"
```

`make broken-links` builds first, runs `mint broken-links` inside `build/`, and filters expected reports for OpenAPI-generated routes and standalone snippets. It fails only if the filtered report still contains link failures. Use `make broken-links-with-anchors` when a move changes headings or fragment links. `make check-cross-refs` verifies `@[Name]` references against the link map.

When changing the move implementation or redirect-check behavior, run focused tests in addition to the page checks:

```bash
uv run pytest tests/unit_tests/tools/test_move_files.py -vv
uv run pytest tests/unit_tests/test_check_removed_pages_redirects.py -vv
```

## Final checklist

- [ ] The source file is in the branch that matches its intended generated route behavior.
- [ ] The page has plain-text frontmatter description and no manually authored OpenWiki control fields.
- [ ] Every added page has an entry in `src/docs.json` at the intended product, menu item, tab, and group.
- [ ] Every move has manually updated navigation, and every retired or replaced public route has a reviewed redirect.
- [ ] `docs mv --dry-run` output was reviewed before an actual file move.
- [ ] The local preview, build, broken-link checks, anchor check when relevant, cross-reference check, and prose lint pass.
- [ ] No generated file in `build/` was edited.

## See also

<!-- openwiki: broken internal link [/openwiki/architecture/source-map] file "/openwiki/architecture/source-map" does not exist. Fix the href or restore the target, then delete this comment. -->
- [Source, Navigation, and Output Map](/openwiki/architecture/source-map)
<!-- openwiki: broken internal link [/openwiki/concepts/versioning] file "/openwiki/concepts/versioning" does not exist. Fix the href or restore the target, then delete this comment. -->
- [Language Versioning Strategy](/openwiki/concepts/versioning)
<!-- openwiki: broken internal link [/openwiki/operations/cli-tools] file "/openwiki/operations/cli-tools" does not exist. Fix the href or restore the target, then delete this comment. -->
- [CLI Tools Reference](/openwiki/operations/cli-tools)
<!-- openwiki: broken internal link [/openwiki/operations/cross-references] file "/openwiki/operations/cross-references" does not exist. Fix the href or restore the target, then delete this comment. -->
- [Cross-Reference Links](/openwiki/operations/cross-references)
<!-- openwiki: broken internal link [/openwiki/testing/test-overview] file "/openwiki/testing/test-overview" does not exist. Fix the href or restore the target, then delete this comment. -->
- [Testing Overview](/openwiki/testing/test-overview)
