---
type: operations guide
title: Adding and Maintaining Documentation Pages
description: Safely add, move, retire, or regenerate documentation pages by selecting the source owner, maintaining current navigation and compatibility redirects, and validating rendered output.
tags: [documentation, operations, navigation, redirects, build-system]
sources:
  - id: openwiki-source-18732c72f962c06354cb62db
    resource: repo://.agents/skills/add-docs-page/SKILL.md
  - id: openwiki-source-8037e2358a2c4f9b2c722a11
    resource: repo://AGENTS.md
  - id: openwiki-source-a2371d6362e5db4bc834ad03
    resource: repo://CLAUDE.md
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
  - id: openwiki-source-05ccef8d4cf1698187f20464
    resource: repo://pyproject.toml
  - id: openwiki-source-3988d52ac8d59fd5a6618960
    resource: repo://scripts/check_removed_pages_redirects.py
  - id: openwiki-source-697851c98229599f97376bfb
    resource: repo://scripts/process_langsmith_openapi.py
  - id: openwiki-source-63d8ba810a7c0181c548a307
    resource: repo://scripts/refresh_integration_downloads.py
  - id: openwiki-source-a9a8730b7e43a5ad2d0af4f1
    resource: repo://src/docs.json
  - id: openwiki-source-f79ecf48880bff8d363b1fbd
    resource: repo://src/langsmith/bind-evaluator-to-dataset-link.mdx
  - id: openwiki-source-a39cb5ba9006abfe6280b6f8
    resource: repo://src/oss/openwiki/cli-reference.mdx
generated: { by: "openwiki/0.4.3", at: "2026-09-28T08:28:57.771Z" }
verified:
  - by: openwiki/0.4.3
    at: 2026-09-28T08:28:57.771Z
---

# Adding and Maintaining Documentation Pages

A documentation change is complete only when its durable owner, public route, navigation, and validation agree. `AGENTS.md` is the active authoring guidance; `CLAUDE.md` points readers to it. Edit manual content under `src/`, never `build/`: the builder clears and recreates `build/`. Likewise, change generator inputs rather than generated snippets, integration listings, transformed specifications, or Mintlify deployment-generated endpoint pages.

```mermaid
flowchart TD
    Start["Classify the requested change"] --> Owner{"Authored page or derived surface"}
    Owner -->|"Authored"| Source["Change a source page under src"]
    Owner -->|"Derived"| Input["Change metadata or generator input"]
    Source --> Nav["Update current docs.json navigation"]
    Input --> Generate["Run the owning generator"]
    Nav --> Route{"Published route changed or retired"}
    Route -->|"Yes"| Redirect["Add compatibility redirects"]
    Route -->|"No"| Check["Run focused validation"]
    Redirect --> Check
    Generate --> Check
    Check --> Review["Review source config and rendered output"]
    classDef process fill:#E5F4FF,stroke:#006DDD,stroke-width:2px,color:#030710
    classDef trigger fill:#F6FFDB,stroke:#6E8900,stroke-width:2px,color:#2E3900
    classDef decision fill:#FDF3FF,stroke:#7E65AE,stroke-width:2px,color:#504B5F
    classDef output fill:#EBD0F0,stroke:#885270,stroke-width:2px,color:#441E33
    class Start trigger
    class Owner,Route decision
    class Source,Input,Nav,Generate,Redirect,Check process
    class Review output
```

This flow distinguishes durable changes from derived output and makes public-route compatibility explicit.

## Choose the owner and route family

Choose by source ownership, not the visible menu label. Build mixes OSS and LangSmith sources, while Fleet is labelled **No-code agents**. The builder emits the following route families:

| Content | Authored source | Emitted routes |
| --- | --- | --- |
| Shared OSS, including LangChain, LangGraph, and most Deep Agents | `src/oss/` outside language-specific directories | One source builds to `/oss/python/...` and `/oss/javascript/...`. |
| Language-specific OSS, including integrations | `src/oss/python/` or `src/oss/javascript/` | The matching language route only. |
| OpenWiki and Deep Agents Code | `src/oss/openwiki/` or `src/oss/deepagents/code/` | One unversioned route: `/oss/openwiki/...` or `/oss/deepagents/code/...`. |
| Ordinary LangSmith | `src/langsmith/` | One unversioned `/langsmith/...` route. |
| Managed Deep Agents | Direct `src/langsmith/managed-deep-agents*.mdx` files | Both `/langsmith/python/...` and `/langsmith/javascript/...`. |

Shared OSS pages use one source file. Use `:::python` and `:::js` fences for divergent material; preprocessing retains the selected branch and rewrites supported links and snippet imports. Use ordinary unprefixed `/oss/...` source links rather than manually inserting `/python/` or `/javascript/`.

OpenWiki and Deep Agents Code intentionally remain unversioned. From versioned OSS content, link to `/oss/openwiki/...` or `/oss/deepagents/code/...` without a language segment; the builder excludes those paths from OSS link rewriting. Conditional fences on those pages resolve as Python.

Managed Deep Agents is the exception to ordinary LangSmith output: direct matching files are omitted from the unversioned build and emitted for both languages. In source, an unversioned `/langsmith/managed-deep-agents...` link is rewritten to the matching language route for language-targeted output. Existing unversioned routes are compatibility redirects to Python pages; do not create a duplicate unversioned page.

## Add an authored page to current navigation

`src/docs.json` is the authoritative site configuration and navigation source. The current shape is `navigation.products[]` → `menu[]`. Each menu item has an `item` label and can contain direct `pages`, `tabs`, or Build's `dropdowns[]` with `tabs`; a `pages` array can mix route strings with recursively nested `{ "group": ..., "pages": [...] }` objects. Locate the neighboring route in its actual array and preserve its presentation fields such as `root`, `expanded`, and `tag` only when needed.

For an authored page:

1. Inspect a neighboring file and create the `.md` or `.mdx` page under the selected `src/` owner. Supply required frontmatter and keep `description` plain text.
2. Add the extensionless route relative to `src` to the matching current `pages` array. For example, `src/langsmith/sandboxes.mdx` maps to `langsmith/sandboxes`.
3. Add every route the owner emits: shared OSS needs Python and TypeScript entries; language-specific content needs one; OpenWiki and Deep Agents Code need one unversioned entry; Managed Deep Agents needs one entry in each language dropdown.
4. Put a new group's index route first when it has an index. For an integration in an existing component, add it to that component's `index.mdx`; change `docs.json` only for a new component group.
5. Search inbound fragment links before changing a heading, because its anchor changes with the heading.

Navigation placement can intentionally provide more than one discovery path. For example, `bind-evaluator-to-dataset` is the full Evaluators-tab page, while the Experiment configuration group contains a small `bind-evaluator-to-dataset-link` page whose `url` points at that same route. Keep such wrappers and canonical pages consistent rather than treating duplicate titles as accidental routes. The TypeSafe-compatible provider page belongs in Prompt & Context Hub's **Connect to models** group.

### Checker limitation and route review

Use `scripts/check_removed_pages_redirects.py` as a focused source/redirect guard, but do not mistake it for validation of the current menu-shaped navigation. Its extractor walks direct `products[].pages`, legacy `products[].tabs`, `products[].dropdowns`, and `groups`, but does not descend through `products[].menu`. Consequently, with the current `docs.json` layout it cannot establish that a newly added menu route maps to a source file or that a removed menu route has a redirect. Manually review the exact `menu` branch and use a clean build plus link checks for navigation changes.

## Move or retire a page safely

Start a filesystem move with the preferred mover in preview mode:

```bash
uv run docs mv src/langsmith/evaluation.mdx src/langsmith/deploy/evaluation.mdx --dry-run
```

The installed `docs` console script routes to `pipeline.cli:main`. The mover scans `src/` Markdown, MDX, and notebook Markdown cells for links resolving to the moved file. When the directory changes, it recalculates relative links in the moved document. `--dry-run` reports prospective rewrites without moving or editing; a real run writes the move to `link_changes.jsonl`, moves the source, and updates its internal relative links.

Then update route strings in their actual `docs.json` arrays, search for root-relative references to the old public path, and make the compatibility decision separately. The mover does not update navigation or redirects. Add a redirect for every route that moved or retired, including both language routes where relevant:

```json
{ "source": "/langsmith/evaluation", "destination": "/langsmith/deploy/evaluation" }
```

Redirects are top-level `redirects` entries and use site paths. The checker compares base and proposed route sets only for the shapes it extracts; when it sees a removed route whose source file is gone, it accepts an exact `source` or a covering `:path*` redirect. Retaining source bypasses that narrow condition but is not a substitute for preserving a published URL deliberately.

For Managed Deep Agents, preserve or replace legacy unversioned aliases that currently point to Python routes, and add redirects for changed Python and JavaScript routes. This is a compatibility surface in addition to the two emitted routes.

```bash
python3 scripts/check_removed_pages_redirects.py --base-ref origin/main src/docs.json
```

## Regenerate derived surfaces through their inputs

### Snippets and testable samples

Reusable blocks belong in `src/snippets/` and must use an import such as `from '/snippets/...'`; the builder can rewrite this form to language-specific copies, unlike Mintlify's `<Snippet file="..." />`. Runnable examples belong in `src/code-samples/`, not generated display files.

```bash
make test-code-samples FILES="src/code-samples/path/to/sample.py"
make code-snippets
```

The extraction pipeline writes derivative files under `src/code-samples-generated/` and `src/snippets/code-samples/`. Regenerate them; never hand-edit them.

### Integration pages and listings

Integration guides are language-specific source pages. The current JavaScript MCP Toolbox page demonstrates `integration.name` plus an `npm` package in frontmatter; the Python Chroma provider overview is an authored provider page, while its component tutorial is linked separately. Follow the established page's source owner and component index rather than assuming provider overviews are generator output.

The integration download-table generator reads hosted-guide `integration:` frontmatter and merges third-party records from `scripts/data/integration_external_docs.yaml`. It sorts rows by download availability, count, then name, and writes listing snippets. External rows use `docs_url`; unsafe schemes and protocol-relative URLs are rejected before rendering.

```bash
uv run python scripts/refresh_integration_downloads.py --check-docs-urls
uv run python scripts/refresh_integration_downloads.py --write
```

### OpenAPI references

`docs.json` `openapi` group entries configure Mintlify-generated endpoint pages. The Agent Server and LangSmith REST API use committed source specifications and explicit output directories; Control Plane uses a deploy-time remote specification. Generated endpoint pages do not exist in the local build, so they must never become authored MDX or a manual edit target.

`src/langsmith/langsmith-platform-openapi.json` is a processed, committed input refreshed by automation. `scripts/process_langsmith_openapi.py` fetches its default only from the allow-listed `api.smith.langchain.com`, marks selected operations hidden, standardizes visible operation titles, adds and orders tag groups, and writes only with `--write`.

```bash
uv run python scripts/process_langsmith_openapi.py --write
make check-openapi
```

`make check-openapi` builds first and currently invokes `mint openapi-check` only for `build/langsmith/agent-server-openapi.json`. It does not validate the processed LangSmith REST specification, so inspect its generated diff and use the appropriate focused tests or tooling when changing the processor.

## Validate the change

Choose checks by what changed:

1. Run `make lint_prose FILES="src/path/to/page.mdx"`; omit `FILES` to lint all of `src/`.
2. Run `make check-cross-refs` after changing `@[...]` references.
3. Run the affected sample, generator, integration URL check, or OpenAPI command after changing its inputs.
4. Use `make dev` to inspect rendered content. It performs an initial build unless skipped, watches `src`, and runs `mint dev` from `build/` on port 3000. Review both language outputs for shared OSS and Managed Deep Agents.
5. Run `make build` for clean output. For route or link changes run `make broken-links`; for anchor changes run `make broken-links-with-anchors`. Both ask Mint to validate redirects and links, then filter known deployment-time OpenAPI and standalone-snippet reports before failing remaining reported links.
6. Review source, `src/docs.json`, generator input, and regenerated output. A `build/` diff is evidence of rendering, never the durable change.

## Completion checklist

- [ ] The edit is in authored source or a generator input, never build or deployment-generated output.
- [ ] New pages have valid frontmatter with a plain-text description and the correct current `docs.json` menu entry.
- [ ] Navigation contains every route emitted by the selected route family.
- [ ] Moved and retired public URLs, including Managed Deep Agents aliases, redirect to maintained destinations.
- [ ] Generated snippets, samples, listings, and specifications were regenerated through their owners.
- [ ] Focused checks, a clean build, and relevant link checks ran.
- [ ] The final source/configuration and rendered output were reviewed, including manual review of menu navigation.

## See also

- [Source directory map](/openwiki/architecture/source-map.md)
- [Versioning](/openwiki/concepts/versioning.md)
- [Mintlify integration](/openwiki/integrations/mintlify.md)
- [Integration listing automation](/openwiki/workflows/integration-listing-automation.md)
- [Versioned content](/openwiki/workflows/versioned-content.md)
