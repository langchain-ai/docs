---
type: operations guide
title: Adding and Maintaining Documentation Pages
description: Add, move, retire, and regenerate documentation pages by choosing the right source owner, maintaining navigation and redirects, and validating rendered output.
tags: [documentation, operations, navigation, redirects, build-system]
verified:
  - by: openwiki/0.4.3
    at: 2026-10-03T08:20:07.933Z
sources:
  - id: openwiki-source-18732c72f962c06354cb62db
    resource: repo://.agents/skills/add-docs-page/SKILL.md
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
  - id: openwiki-source-8d071ef0669cd8d2d79c6c15
    resource: repo://pipeline/tools/links.py
  - id: openwiki-source-05ccef8d4cf1698187f20464
    resource: repo://pyproject.toml
  - id: openwiki-source-3988d52ac8d59fd5a6618960
    resource: repo://scripts/check_removed_pages_redirects.py
  - id: openwiki-source-a9a8730b7e43a5ad2d0af4f1
    resource: repo://src/docs.json
generated: { by: "openwiki/0.4.3", at: "2026-10-03T08:20:07.933Z" }
---

# Adding and Maintaining Documentation Pages

A page change is complete when its authored source, public route, navigation, and validation agree. Work in `src/`, never `build/`: the builder clears and recreates `build/`. Do not hand-edit generated integration listings, code-sample derivatives, transformed OpenAPI specifications, or Mintlify deployment-generated endpoint pages; update their inputs and run their owning generator.

## Choose the source family first

Choose the directory by source ownership, not its visible menu name. Build mixes OSS and LangSmith sources, while **No-code agents** is backed by `src/langsmith/fleet/`.

| Content | Source | Published route |
| --- | --- | --- |
| Shared OSS | `src/oss/` shared directories | Both `/oss/python/...` and `/oss/javascript/...` |
| Language-specific OSS | `src/oss/python/` or `src/oss/javascript/` | Matching language only |
| OpenWiki and Deep Agents Code | `src/oss/openwiki/` or `src/oss/deepagents/code/` | One unversioned route |
| Ordinary LangSmith | `src/langsmith/` | One `/langsmith/...` route |
| Managed Deep Agents | direct `src/langsmith/managed-deep-agents*.mdx` | Python and JavaScript LangSmith routes |

Shared OSS pages use one source file. Use `:::python` and `:::js` for divergent material. The build emits each language and rewrites supported links. OpenWiki and Deep Agents Code stay unversioned; link to `/oss/openwiki/...` and `/oss/deepagents/code/...` without a language prefix. Managed Deep Agents instead emits two language routes; legacy unversioned routes redirect to Python.

## Add navigation with the page

`src/docs.json` is the authoritative navigation and route configuration. Its current structure is `navigation.products[]` → `menu[]`. A menu item may hold direct `pages`, `tabs`, or—under Build—`dropdowns[]` containing `tabs[]`; `pages` arrays contain route strings and nested group objects.

1. Create the `.md` or `.mdx` file beneath its source owner. Include required frontmatter; `description` must be plain text.
2. Add its extensionless route relative to `src` to the neighboring `pages` array: `src/langsmith/sandboxes.mdx` becomes `langsmith/sandboxes`.
3. Add every emitted route: two Build entries for shared OSS, one for language-specific or unversioned content, and one Managed Deep Agents entry per language dropdown.
4. Put an index route first in a new group. For an integration in an existing component, update its `index.mdx`; update `docs.json` only for a new component group.
5. Search inbound fragment links before changing a heading, since changing its words changes its anchor.

The removed-pages checker does not descend through the current `products[].menu[]` layer. It cannot verify menu-contained page existence or redirect coverage, so inspect the edited menu branch and use the build/link checks.

## Move or retire safely

Preview a move before applying it:

```bash
uv run docs mv src/langsmith/evaluation.mdx src/langsmith/deploy/evaluation.mdx --dry-run
```

The mover scans Markdown, MDX, and notebook Markdown cells for links to the old file and recalculates relative links inside a moved document. A dry run makes no edits; a real run logs the move, relocates the source, and updates internal links. It does not update navigation or public redirects.

Update the relevant `docs.json` route strings, then add a top-level redirect for each published route that moved or retired, including both language paths where applicable:

```json
{ "source": "/langsmith/evaluation", "destination": "/langsmith/deploy/evaluation" }
```

## Regenerate derived surfaces

Reusable blocks live in `src/snippets/` and use imports such as `from '/snippets/...'`. Testable samples live in `src/code-samples/`; regenerate their derivatives rather than editing `src/code-samples-generated/` or `src/snippets/code-samples/`.

```bash
make test-code-samples FILES="src/code-samples/path/to/sample.py"
make code-snippets
```

Integration tables derive from hosted integration frontmatter and external discovery records. Refresh them through their script. OpenAPI groups in `docs.json` configure Mintlify-generated endpoint directories; deployment-generated endpoints are not authored MDX. The LangSmith REST specification is processed with:

```bash
uv run python scripts/process_langsmith_openapi.py --write
make check-openapi
```

## Validate

1. Run `make lint_prose FILES="src/path/to/page.mdx"`.
2. Run `make check-cross-refs` after changing `@[...]` references.
3. Run the focused sample or generator check after changing an input.
4. Use `make dev` to inspect output; review both languages for shared OSS and Managed Deep Agents.
5. Run `make build`, then `make broken-links` for route/link changes or `make broken-links-with-anchors` for anchor changes. These checks include redirects and filter expected deployment-time OpenAPI and standalone-snippet reports.
6. Review authored source, `src/docs.json`, generator inputs, and generated output. Rendered `build/` content is evidence, not the source of truth.
