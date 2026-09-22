---
type: operations guide
title: Adding and Maintaining Documentation Pages
description: Safely add, move, retire, or regenerate documentation by choosing the owning input, maintaining docs.json navigation and redirects, and running focused validation.
tags: [documentation, operations, navigation, redirects, build-system]
sources:
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
  - id: openwiki-source-560bf24db9566b97ee19e383
    resource: repo://scripts/generate_code_snippet_mdx.py
  - id: openwiki-source-697851c98229599f97376bfb
    resource: repo://scripts/process_langsmith_openapi.py
  - id: openwiki-source-63d8ba810a7c0181c548a307
    resource: repo://scripts/refresh_integration_downloads.py
  - id: openwiki-source-a9a8730b7e43a5ad2d0af4f1
    resource: repo://src/docs.json
  - id: openwiki-source-a39cb5ba9006abfe6280b6f8
    resource: repo://src/oss/openwiki/cli-reference.mdx
verified:
  - by: openwiki/0.4.3
    at: 2026-09-21T08:24:04.334Z
generated: { by: "openwiki/0.4.3", at: "2026-09-21T08:24:04.334Z" }
---

# Adding and Maintaining Documentation Pages

A safe documentation change starts at the input that owns it. `src/` contains authored pages and configuration; `build/` is cleared and recreated by the builder. `src/docs.json` is the public site contract for navigation and redirects. Therefore, every new authored page must be navigated, while a moved or removed public route must retain a redirect to its maintained successor.

```mermaid
flowchart TD
    Start["Classify the requested change"] --> Owner{"Choose an owning input"}
    Owner --> Authored["Author page or navigation input"]
    Owner --> Generated["Change generator input"]
    Authored --> Route["Update docs.json route contract"]
    Route --> Retired{"Public route moved or removed"}
    Retired -->|"Yes"| Redirect["Add redirect"]
    Retired -->|"No"| Gates["Run focused checks"]
    Redirect --> Gates
    Generated --> Regenerate["Regenerate derived files"]
    Regenerate --> Gates
    Gates --> Review["Review source and configuration diff"]
    classDef process fill:#E5F4FF,stroke:#006DDD,stroke-width:2px,color:#030710
    classDef trigger fill:#F6FFDB,stroke:#6E8900,stroke-width:2px,color:#2E3900
    classDef decision fill:#FDF3FF,stroke:#7E65AE,stroke-width:2px,color:#504B5F
    classDef output fill:#EBD0F0,stroke:#885270,stroke-width:2px,color:#441E33
    class Start trigger
    class Owner,Retired decision
    class Authored,Generated,Route,Redirect,Regenerate,Gates process
    class Review output
```

This change flow separates authored inputs from derived output and makes URL compatibility an explicit decision.

## Choose the source and route model

The builder has three route models:

| Content | Authoring location | Emitted routes |
| --- | --- | --- |
| Shared OSS content, including LangChain, LangGraph, and most Deep Agents content | `src/oss/` | One source produces `/oss/python/...` and `/oss/javascript/...`. Use `:::python` and `:::js` blocks only for language-specific material. |
| Language-specific integration content | `src/oss/python/` or `src/oss/javascript/` | Only that language's route. |
| OpenWiki and Deep Agents Code | `src/oss/openwiki/` or `src/oss/deepagents/code/` | A single unversioned `/oss/openwiki/...` or `/oss/deepagents/code/...` route. |
| Ordinary LangSmith documentation | `src/langsmith/` | A single `/langsmith/...` route. |
| Managed Deep Agents | Direct `src/langsmith/managed-deep-agents*.mdx` files | Both `/langsmith/python/...` and `/langsmith/javascript/...` routes. |

The full builder clears `build/`, renders both versioned OSS variants, renders the two language-agnostic OSS products once, then renders LangSmith and Managed Deep Agents. Conditional fences retain only their matching language; language-agnostic OSS pages resolve them as Python. During versioned output, unprefixed ordinary `/oss/...` links are rewritten to the selected language route. Links to OpenWiki and Deep Agents Code are exceptions: use `/oss/openwiki/...` and `/oss/deepagents/code/...` without a language prefix.

Managed Deep Agents is the LangSmith exception. Its direct files do not produce ordinary unversioned LangSmith output; legacy unversioned URLs redirect to the Python routes through `docs.json`. Do not create an unversioned duplicate to preserve an old URL.

## Place every authored page in current navigation

`src/docs.json` is authoritative for navigation, routing, redirects, and configured generated API references. The current top-level navigation contains two products: **AGENT DEVELOPMENT LIFECYCLE**, whose menu has Home, Build, Test, Deploy, and Monitor; and **PRODUCTS AND SETUP**, whose menu includes LangSmith setup, LLM Gateway, No-code agents, Engine, and Deep Agents Code. A Build menu item has Python and TypeScript dropdowns with tabs and nested groups; other menu items can use their own page or group structure. Labels are not directory names: Build combines `src/oss/` and `src/langsmith/`, while No-code agents is sourced from `src/langsmith/fleet/`.

Before adding a route, locate a neighboring entry in the relevant `docs.json` `pages` array rather than deriving placement from its label. Use an extensionless path relative to `src`; for example, `src/langsmith/sandboxes.mdx` is `"langsmith/sandboxes"`. A shared OSS source is valid for the matching Python and JavaScript entries. For a new group, put its index route first.

For a standard authored page:

1. Inspect neighboring source pages and the target `docs.json` group. Create a `.md` or `.mdx` file under the chosen owner with frontmatter. Keep `description` plain text: repository guidance prohibits Markdown there.
2. Add the emitted route or routes to the exact product, menu item, dropdown, tab, and group. A source file alone is not navigated.
3. For a shared OSS page, add both language routes; for language-specific content, add the applicable route; for OpenWiki or Deep Agents Code, add its one unversioned route. Add both Managed Deep Agents routes to their respective language navigation.
4. An integration guide inside an existing component is normally added to that component's `index.mdx`; update `docs.json` only when creating a new component group.
5. Use root-relative internal routes. Do not manually add `/python/` or `/javascript/` to ordinary versioned OSS links, because preprocessing adds the target prefix. Check inbound fragment links before changing a heading.

The removed-pages checker also requires every navigation page to resolve to an existing `.mdx` or `.md` source. That makes navigation an integrity constraint, not merely a sidebar preference.

## Move or retire a route without breaking it

Use the mover for the filesystem move and qualifying relative-link maintenance, then make navigation and redirect changes explicitly:

```bash
uv run docs mv src/langsmith/evaluation.mdx src/langsmith/deploy/evaluation.mdx --dry-run
```

The installed `docs` command routes to `pipeline.cli:main`. `--dry-run` reports changes without moving or rewriting files. A real move appends the operation to `link_changes.jsonl`, scans Markdown, MDX, and notebook Markdown cells under `src/`, moves the file, and recalculates relative links within the moved file. It does **not** update `docs.json`, public root-relative route strings, or redirects. Review the preview, perform the move, and search for the old public route.

Update the navigation entry in the same change. If a published route changes or disappears, add a redirect in `docs.json` to the closest maintained destination:

```json
{
  "source": "/langsmith/evaluation",
  "destination": "/langsmith/deploy/evaluation"
}
```

A shared OSS or Managed Deep Agents move can require redirects for each retired language route. The removed-pages check compares base and proposed navigation. If a route disappears from navigation **and** no corresponding source remains, it requires a redirect; a `:path*` source can cover a route family. Retaining source while removing navigation avoids that particular checker failure, but remains a deliberate reachability decision rather than a substitute for preserving a published URL.

Run the checker against the comparison ref when changing navigation or redirects:

```bash
python3 scripts/check_removed_pages_redirects.py --base-ref origin/main src/docs.json
```

## Change generated surfaces through their owners

Generated files are outputs, not alternate authoring surfaces. Change the input, run its generator, and review the derivative diff.

### Code samples and snippets

Runnable samples belong in `src/code-samples/`. `make code-snippets` extracts marked regions to `src/code-samples-generated/` and produces derivative MDX in `src/snippets/code-samples/`. The MDX generator supports Python, TypeScript, Java, Kotlin, Go, and shell intermediates; it can emit language fences or eligible Deep Agents provider CodeGroups and add trace links from the trace manifest. Do not hand-edit the derived snippets.

```bash
make test-code-samples FILES="src/code-samples/path/to/sample.py"
make code-snippets
```

Test a changed source sample before publishing it. If credentials or an unavailable dependency prevent local execution, report that limitation rather than editing generated display code.

### Integration discovery tables

A hosted integration guide's `integration:` frontmatter and `scripts/data/integration_external_docs.yaml` own generated component tables. Hosted guides provide internal links; external records link through `docs_url`. Change that metadata rather than `src/snippets/oss/*-downloads.mdx`, then validate and refresh:

```bash
uv run python scripts/refresh_integration_downloads.py --check-docs-urls
uv run python scripts/refresh_integration_downloads.py --write
```

The refresh script permits `https://`, `http://`, and single-slash site-relative URLs, and rejects protocol-relative and unsafe schemes before it renders external links.

### OpenAPI reference configuration

`docs.json` OpenAPI entries are Mintlify configuration, not authored endpoint MDX. Mintlify creates endpoint pages at deployment, so those routes are not normal local source pages. The committed Agent Server spec, configured remote Control Plane source, and committed LangSmith REST spec have separate lifecycles; do not hand-author their endpoint output.

For a LangSmith REST specification refresh, use the processor rather than editing the transformed spec:

```bash
uv run python scripts/process_langsmith_openapi.py --write
```

With its default input, the processor fetches only its allow-listed LangSmith API host, hides selected operations, normalizes titles, groups and orders sidebar tags, and writes only with `--write`. For an Agent Server spec change, use `make check-openapi`; this currently validates `langsmith/agent-server-openapi.json` from `build/`.

## Run focused checks

Select checks based on the changed owner, then add rendering and link checks for routes, navigation, preprocessing, moves, removals, or generated inputs:

1. Run `make lint_prose FILES="src/path/to/page.mdx"` for prose. It installs the repository-pinned Vale binary; without `FILES`, it lints `src/`.
2. Run `make check-cross-refs` after adding or changing `@[...]` references.
3. Run focused sample, generator, integration URL, or OpenAPI checks for the owner you changed.
4. Run `make dev` to inspect rendered output. It builds first, watches `src/`, and starts `mint dev` from `build/` on port 3000. Inspect both language variants for versioned content.
5. Run `make build` for a clean result, then `make broken-links` after route or link work. Use `make broken-links-with-anchors` when fragments changed. These targets invoke Mint's redirect validation and filter expected reports from deployment-time OpenAPI pages and standalone snippets.
6. Review the completed source and `docs.json` diff; never accept a `build/` edit as the durable fix.

## Completion checklist

- [ ] The page, metadata, sample, listing input, or specification changed at its actual owner.
- [ ] Every new authored page has plain-text frontmatter and the correct extensionless `docs.json` navigation entry.
- [ ] The selected route model has every required language-specific or unversioned navigation entry.
- [ ] A move or removal updates navigation and preserves each retired public route with an appropriate redirect.
- [ ] Derived snippets, integration tables, and OpenAPI specifications were regenerated rather than hand-edited.
- [ ] Focused lint, cross-reference, generator, source-sample, OpenAPI, build, and link checks ran where applicable.
- [ ] The rendered route and final source/configuration diff were reviewed.

## See also

- [Source directory map](/openwiki/architecture/source-map.md)
- [Versioned content](/openwiki/concepts/versioning.md)
- [Mintlify integration](/openwiki/integrations/mintlify.md)
- [Cross-references](/openwiki/operations/cross-references.md)
- [Testing overview](/openwiki/testing/test-overview.md)
- [Versioned content workflow](/openwiki/workflows/versioned-content.md)
