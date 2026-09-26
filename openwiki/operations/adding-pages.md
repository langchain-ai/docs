---
type: operations guide
title: Adding and Maintaining Documentation Pages
description: Safely add, move, retire, or regenerate documentation pages by selecting the source owner, maintaining navigation and compatibility redirects separately, and validating rendered output.
tags: [documentation, operations, navigation, redirects, build-system]
verified:
  - by: openwiki/0.4.3
    at: 2026-09-26T08:20:04.541Z
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
  - id: openwiki-source-a39cb5ba9006abfe6280b6f8
    resource: repo://src/oss/openwiki/cli-reference.mdx
generated: { by: "openwiki/0.4.3", at: "2026-09-26T08:20:04.541Z" }
---

# Adding and Maintaining Documentation Pages

A documentation change is complete only when its owning input, public route, navigation, and validation are correct. `AGENTS.md` is the repository's active authoring guidance; `CLAUDE.md` points to it. Make manual changes under `src/`, never in `build/`: a build clears and recreates that directory. Likewise, do not hand-edit generated snippets, integration tables, or transformed OpenAPI output—change their declared inputs and regenerate.

Treat **authored-source movement**, **navigation**, and **redirects** as separate operations. Moving a file can update file-resolved links, but it does not decide where the page appears in the UI or preserve its former public URL. Every new public authored page needs navigation; every changed or retired published route needs an explicit compatibility decision.

```mermaid
flowchart TD
    Start["Classify the requested change"] --> Owner{"Authored page or derived surface"}
    Owner -->|"Authored"| Source["Change source under src"]
    Owner -->|"Derived"| Input["Change metadata or generator input"]
    Source --> Nav["Update docs.json navigation"]
    Nav --> Route{"Published route changed or retired"}
    Route -->|"Yes"| Redirect["Add compatibility redirects"]
    Route -->|"No"| Check["Run focused validation"]
    Input --> Generate["Run the owning generator"]
    Generate --> Check
    Redirect --> Check
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

This flow keeps source ownership, placement, route compatibility, and regeneration independently reviewable.

## Select the source owner and route family

Choose the source directory by subject ownership, not from a navigation label. Build, for example, mixes OSS and LangSmith sources; Fleet appears as **No-code agents** in navigation. The builder produces these route families:

| Content | Authored source | Emitted routes |
| --- | --- | --- |
| Shared OSS content, including LangChain, LangGraph, and most Deep Agents | `src/oss/` outside language-specific directories | One source is built at both `/oss/python/...` and `/oss/javascript/...`. |
| Language-specific OSS content, including integrations | `src/oss/python/` or `src/oss/javascript/` | Only the matching language route. |
| OpenWiki and Deep Agents Code | `src/oss/openwiki/` or `src/oss/deepagents/code/` | One unversioned route: `/oss/openwiki/...` or `/oss/deepagents/code/...`. |
| Ordinary LangSmith content | `src/langsmith/` | One unversioned `/langsmith/...` route. |
| Managed Deep Agents | Direct `src/langsmith/managed-deep-agents*.mdx` files | Both `/langsmith/python/...` and `/langsmith/javascript/...` routes. |

Shared OSS pages use one source file and can use `:::python` and `:::js` fences for language-specific material. The preprocessing pass retains the matching block, resolves cross-references in that language, rewrites supported snippet imports, and rewrites ordinary root-relative `/oss/...` links to the target language. Do not manually insert `/python/` or `/javascript/` into ordinary shared OSS links.

OpenWiki and Deep Agents Code deliberately remain unversioned. From versioned OSS content, link to `/oss/openwiki/...` or `/oss/deepagents/code/...` without a language segment: the builder explicitly skips those paths when rewriting OSS links. Their conditional fences resolve as Python.

Managed Deep Agents is the exception within LangSmith. The builder excludes its direct source files from ordinary unversioned output and emits language variants instead. Use unversioned `/langsmith/managed-deep-agents...` links in source where a language-specific build should choose the corresponding variant; the builder rewrites them for Python or JavaScript. Existing unversioned public routes are compatibility aliases in `docs.json` that redirect to Python—do not restore a duplicate unversioned source page.

## Add an authored page to current navigation

`src/docs.json` is the navigation and route configuration. Its current structure is `navigation.products[]`, then each product's `menu[]`. A menu item may have direct `pages`, `tabs`, `groups`, or—for Build—`dropdowns[]` containing `tabs[]`; a `pages` array can hold route strings and nested `{ "group": ..., "pages": [...] }` objects. Find a neighboring route in the intended array and mirror its shape and optional fields such as `root`, `expanded`, and `tag` only where appropriate. Do not assume every route has a product → tab → group path.

For an authored page:

1. Inspect a neighboring source page and create the `.md` or `.mdx` file under the selected `src/` owner. Give it required frontmatter and keep `description` plain text—Markdown breaks SEO.
2. Add an extensionless route relative to `src` to the exact navigation `pages` array. For example, `src/langsmith/sandboxes.mdx` becomes `langsmith/sandboxes`.
3. Add entries for every route the owner emits: shared OSS pages need Python and JavaScript entries; a language-specific page needs one; OpenWiki and Deep Agents Code need one unversioned entry; and a Managed Deep Agents page needs one entry in each Build language dropdown.
4. For a new nested group, put its index route first when that group has an index. For an integration inside an existing component, add the page to that component's `index.mdx`; change `docs.json` only for a new component group.
5. Before renaming a heading, search for inbound fragment links, because its generated anchor changes with the heading text.

The current navigation illustrates why owner and menu placement must be checked independently. `langsmith/decision-model-evaluator` is ordinary, unversioned LangSmith content in Test → Evaluators → Evaluator types → UI. In contrast, `managed-deep-agents-identity` appears in both Build → Managed Deep Agents language dropdowns even though it has one source file.

### Navigation-checker limitation

Run `python3 scripts/check_removed_pages_redirects.py --base-ref origin/main src/docs.json` after navigation or redirect changes, but do not treat its current success as proof that a `menu[]` entry is correct. The checker recursively handles the older product-level `pages`, `tabs`, `dropdowns`, and `groups` shapes, but it does not traverse `product.menu`; the current `docs.json` places its navigation below `menu`. It therefore cannot presently discover or validate the current menu-contained routes. Review the precise JSON placement and use a build/link check as the effective safeguard.

## Move or retire a page safely

Use the mover for the filesystem operation, then change navigation and make the public-route decision separately. Begin with a preview:

```bash
uv run docs mv src/langsmith/evaluation.mdx src/langsmith/deploy/evaluation.mdx --dry-run
```

The installed `docs` console script routes to `pipeline.cli:main`. Its mover scans Markdown, MDX, and notebook Markdown cells below `src/` for links resolving to the moved file; when the parent directory changes, it also recalculates relative links inside the moved document. `--dry-run` reports prospective rewrites without moving or editing files. A real run appends the move to `link_changes.jsonl`, relocates the source, and then updates its internal relative links.

After reviewing the preview:

1. Run the move without `--dry-run`.
2. Change affected route strings in their actual `docs.json` `pages` arrays and search for root-relative uses of the old public URL. The mover handles file-resolved links, not navigation or public-route compatibility.
3. Add a redirect for every published route that moved or retired. Shared OSS and Managed Deep Agents commonly need one redirect per language route.

```json
{
  "source": "/langsmith/evaluation",
  "destination": "/langsmith/deploy/evaluation"
}
```

Redirects belong in the top-level `redirects` array and use site paths. The checker compares proposed navigation with a base `docs.json`; for the route shapes it discovers, a removed route whose source no longer exists requires an exact redirect source or a covering `:path*` wildcard. Retaining a source file bypasses that narrow check, but does not itself preserve a URL after an intentional route change.

### Managed Deep Agents compatibility redirects

Treat a Managed Deep Agents move as a two-language navigation change plus an unversioned compatibility surface. Current identity and HTTP-channel pages appear under both `langsmith/python/managed-deep-agents-*` and `langsmith/javascript/managed-deep-agents-*`. The redirect list maps legacy unversioned routes such as `/langsmith/managed-deep-agents-identity` and `/langsmith/managed-deep-agents-channels-http` to their matching Python routes. Preserve or replace those aliases when changing the source page, and add redirects for changed Python and JavaScript public routes as well.

## Regenerate derived surfaces through their inputs

Generated content has an owner. Edit the source metadata or generator input, run its generation command, and review the resulting change rather than changing the derivative.

### Reusable snippets and testable samples

Put reusable MDX in `src/snippets/` and import it using `from '/snippets/...'`. The builder recognizes and rewrites that import into a language-specific copy for versioned pages; Mintlify's `<Snippet file="..." />` form is not rewritten.

Author runnable examples in `src/code-samples/`. Test a changed sample and regenerate its extracted and rendered forms:

```bash
make test-code-samples FILES="src/code-samples/path/to/sample.py"
make code-snippets
```

The extraction pipeline creates intermediate content under `src/code-samples-generated/` and MDX under `src/snippets/code-samples/`. Do not hand-edit either output. If a sample cannot run locally because required credentials or dependencies are unavailable, report that limitation rather than modifying generated display code.

### Integration listings

Integration listing snippets are generated from `integration:` frontmatter on hosted integration guides and external records in `scripts/data/integration_external_docs.yaml`. A component index imports its derived downloads snippet; adding a hosted integration with appropriate frontmatter can therefore alter the shared listing. External rows link through `docs_url`, and the refresh script allows only `https://`, `http://`, or a single-slash site-relative URL.

```bash
uv run python scripts/refresh_integration_downloads.py --check-docs-urls
uv run python scripts/refresh_integration_downloads.py --write
```

### OpenAPI references

OpenAPI navigation entries configure Mintlify-generated endpoint pages rather than authored endpoint MDX. The LangSmith processor fetches its default input only from the allow-listed LangSmith API host; it hides selected operations, normalizes titles, assigns and orders sidebar tag groups, and writes the transformed specification only with `--write`.

```bash
uv run python scripts/process_langsmith_openapi.py --write
make check-openapi
```

`make check-openapi` builds first and validates `langsmith/agent-server-openapi.json` in `build/`. Do not hand-edit deployment-generated endpoint pages or transformed specifications as if they were their source.

## Validate the change

Run focused checks for the owner you changed, then render and check routes where applicable:

1. Run `make lint_prose FILES="src/path/to/page.mdx"`; omit `FILES` to lint all of `src/`.
2. Run `make check-cross-refs` after changing `@[...]` references.
3. Run the relevant sample, generator, integration URL, or OpenAPI check after changing a generator input.
4. Use `make dev` to inspect the rendered result. It performs an initial build, watches `src/`, and serves `build/` with `mint dev` on port 3000. Inspect both language outputs for shared OSS and Managed Deep Agents pages.
5. Run `make build` for a clean output. After route or link changes, run `make broken-links`; after fragment changes, run `make broken-links-with-anchors`. Both ask Mint to check redirect destinations as well as links and filter expected deployment-time OpenAPI and standalone-snippet reports before failing on remaining broken-link output.
6. Review authored source, `src/docs.json`, generator inputs and output. A `build/` diff is validation evidence, not the durable edit.

## Completion checklist

- [ ] The change was made in an authored owner or generator input, never a generated output.
- [ ] Every new authored page has valid plain-text-description frontmatter and an entry in the correct current `docs.json` menu shape.
- [ ] Navigation includes all routes emitted by its selected route family; each current `menu[]` placement was manually reviewed.
- [ ] Each moved or retired public URL, including Managed Deep Agents aliases, redirects to a maintained destination.
- [ ] Snippets, samples, integration listings, and OpenAPI surfaces were regenerated from their owners.
- [ ] Focused lint, cross-reference, generator, build, and link checks ran where applicable.
- [ ] Rendered output and the final source/configuration diff were reviewed.

## See also

- [Source directory map](/openwiki/architecture/source-map.md)
- [Versioning](/openwiki/concepts/versioning.md)
- [Mintlify integration](/openwiki/integrations/mintlify.md)
- [Quickstart](/openwiki/quickstart.md)
- [Versioned content](/openwiki/workflows/versioned-content.md)
