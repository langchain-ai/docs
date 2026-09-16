---
type: operations guide
title: Adding and Maintaining Documentation Pages
description: Safely add, revise, move, or retire documentation by selecting the owning source, synchronizing navigation and redirects, regenerating derived content, and validating the built site.
tags: [documentation, operations, navigation, redirects, build-system]
sources:
  - id: openwiki-source-18732c72f962c06354cb62db
    resource: repo://.agents/skills/add-docs-page/SKILL.md
  - id: openwiki-source-b48b39ee604e5154ddb6fbad
    resource: repo://.agents/skills/docs-edit/SKILL.md
  - id: openwiki-source-b372ee6d00ad6d446e0fc042
    resource: repo://.agents/skills/docs-review/SKILL.md
  - id: openwiki-source-a5534bfe9d1400e6ecbd306e
    resource: repo://.agents/skills/docs-team-voice/SKILL.md
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
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
  - id: openwiki-source-3988d52ac8d59fd5a6618960
    resource: repo://scripts/check_removed_pages_redirects.py
  - id: openwiki-source-63d8ba810a7c0181c548a307
    resource: repo://scripts/refresh_integration_downloads.py
  - id: openwiki-source-5fdebe45088d0434f7fa98d0
    resource: repo://scripts/refresh_mda_oauth_catalog.py
  - id: openwiki-source-a9a8730b7e43a5ad2d0af4f1
    resource: repo://src/docs.json
  - id: openwiki-source-e86cdb94e153ccc6c527238a
    resource: repo://src/langsmith/managed-deep-agents-connections.mdx
  - id: openwiki-source-a39cb5ba9006abfe6280b6f8
    resource: repo://src/oss/openwiki/cli-reference.mdx
generated: { by: "openwiki/0.4.3", at: "2026-09-15T08:21:56.110Z" }
verified:
  - by: openwiki/0.4.3
    at: 2026-09-15T08:21:56.110Z
---

# Adding and Maintaining Documentation Pages

A documentation change is complete only when every owning surface agrees. Authored prose and assets live under `src/`; `src/docs.json` owns visible navigation and redirects; the pipeline derives `build/`. Never edit `build/` to repair a preview or validation result. Fix its source input, then regenerate it.

```mermaid
flowchart TD
    Start["Classify the requested change"] --> Owner{"Choose owning source"}
    Owner --> Page["Authored page or snippet"]
    Owner --> Sample["Testable code sample"]
    Owner --> Listing["Generated integration listing"]
    Page --> Navigation["Update docs.json navigation"]
    Sample --> RegenerateSample["Regenerate sample snippets"]
    Listing --> RegenerateListing["Regenerate listing snippets"]
    Navigation --> Retired{"Public route moved or removed"}
    Retired -->|"Yes"| Redirect["Add docs.json redirect"]
    Retired -->|"No"| Validate["Build and run focused checks"]
    Redirect --> Validate
    RegenerateSample --> Validate
    RegenerateListing --> Validate
    Validate --> Review["Review finished prose"]
```

This flow separates editable inputs from generated artifacts and keeps a route migration from becoming a broken public link.

## Select the procedure before editing

Use the repository skills that match the task:

| Situation | Procedure |
| --- | --- |
| Add, move, rename, delete, navigate, or redirect a page | Use `add-docs-page`. It defines the required navigation, redirect, and validation sequence. |
| Revise a page on an existing pull request | Use `docs-edit`. Check out the pull request's head branch rather than creating a second branch, inspect its real diff, and run prose and link checks appropriate to the change. |
| Draft or substantially revise prose | Use `docs-team-voice` with the repository style rules. Keep sentences focused, use exact identifiers, link a term on first mention, and remove unverified claims. |
| Review completed prose | Use `docs-review` after editing, and only for Markdown or MDX changed in this pass. A navigation-only or redirect-only change has no prose to review. |

Repository-wide rules live in `AGENTS.md`; task procedures live in `.agents/skills/`. Most supported agents read that tree directly. Claude Code users run `make skills` once to link it into `.claude/skills`.

## Choose the content owner and route model

Choose the source directory from the desired route and language behavior, not from a menu label. Navigation labels and directories intentionally differ. For example, `src/langsmith/fleet/` appears as **No-code agents**, and lifecycle menus can contain both OSS and LangSmith content.

| Content | Authoritative input | Emitted route behavior | Change rule |
| --- | --- | --- | --- |
| Shared OSS content | Most of `src/oss/`, including LangChain, LangGraph, and Deep Agents outside `code/` | Python and JavaScript routes | Keep shared prose in one file; use `:::python` and `:::js` only for material that differs. |
| Language-specific OSS content | `src/oss/python/` or `src/oss/javascript/` | Only the matching language route | Add navigation only in its matching language dropdown. |
| OpenWiki | `src/oss/openwiki/` | One `/oss/openwiki/...` route | Use unprefixed OpenWiki routes in navigation and links. |
| Deep Agents Code | `src/oss/deepagents/code/` | One `/oss/deepagents/code/...` route | Use unprefixed Deep Agents Code routes in navigation and links. |
| Ordinary LangSmith content | `src/langsmith/` | One `/langsmith/...` route | Place it in the applicable lifecycle or setup area in `docs.json`. |
| Managed Deep Agents | Direct `src/langsmith/managed-deep-agents*.mdx` files | Python and JavaScript LangSmith routes | Add both language navigation entries and retain relevant legacy redirects. |
| Reusable snippet | `src/snippets/` | Imported content, not a standalone page route | Edit only authored snippets and import them from consuming MDX. |
| Runnable example | `src/code-samples/` | Generator input for code snippet MDX | Test the sample, then regenerate its derivative artifacts. |
| Integration component table | Hosted-guide `integration` frontmatter and `scripts/data/integration_external_docs.yaml` | Generated `src/snippets/oss/` table snippets | Change metadata, then run the listing generator. |

The build pipeline clears and reconstructs `build/` from `src/`. Shared OSS pages build twice, with conditional blocks resolved for each target and unqualified OSS links rewritten to the active language route. OpenWiki and Deep Agents Code are intentional exceptions: they build once without a language segment, resolving conditionals with the Python target. Their unprefixed routes are also excluded from OSS link rewriting. An unqualified link from either unversioned product to ordinary shared OSS content therefore resolves to the Python route.

## Add or revise an authored page

For an ordinary page, first inspect neighboring entries in `src/docs.json` and the applicable source directory. Navigation is hierarchical: product, menu item, optional dropdown, tab, and nested group. `docs.json` is the authority for public navigation and routing, even when its labels diverge from the source tree.

1. Create or revise the `.mdx` or `.md` source under the selected owner. Preserve local conventions rather than restructuring unaffected content.
2. Give a new MDX page plain-text `title` and `description` frontmatter. Markdown, links, and backticks in `description` break SEO. Verify factual prose against the source it describes; do not invent examples, field names, UI labels, or policy details.
3. Add the extensionless emitted route to `src/docs.json`. Do not put `src/` or `.mdx` in a navigation path. For example, `src/langsmith/sandboxes.mdx` is `"langsmith/sandboxes"`.
4. Add both language entries for a shared OSS or Managed Deep Agents page. Add only the matching entry for a language-specific source. OpenWiki has one emitted artifact, but its same unprefixed route is listed in both Build dropdowns.
5. Put an index route first when creating a group. Integration pages are the exception: add them to their component `index.mdx`; change `docs.json` only when creating a component group.
6. Use public routes for internal links. An unqualified `/oss/...` link follows the target language except for OpenWiki and Deep Agents Code. Use `@[Name]` only for eligible API-reference links and run `make check-cross-refs` when adding one.

## Change generated-content inputs, not results

Generated MDX is still generated even when it is committed under `src/`. Do not patch it by hand.

- **Code samples:** `make code-snippets` extracts content from `src/code-samples/` into `src/code-samples-generated/` and `src/snippets/code-samples/`. Edit and test the sample source, then regenerate.
- **Integration tables:** hosted guides provide `integration` frontmatter; third-party rows come from `scripts/data/integration_external_docs.yaml`. Regenerate after changing either input:

  ```bash
  uv run python scripts/refresh_integration_downloads.py --write
  ```

  Before changing an external `docs_url`, run the offline validation:

  ```bash
  uv run python scripts/refresh_integration_downloads.py --check-docs-urls
  ```

  It allows `https://`, `http://`, and a single-slash site-relative path, but rejects protocol-relative and unsafe schemes. Full generation may fetch npm or PyPI download data; an unsafe external URL is a metadata error, not a reason to edit the rendered table.
- **Managed Deep Agents OAuth catalog:** `src/langsmith/managed-deep-agents-connections.mdx` owns prose and imports `src/snippets/langsmith/mda-oauth-catalog.mdx`. The installed `mda` CLI supplies catalog data. Upgrade the CLI and regenerate rather than editing the table:

  ```bash
  uv tool upgrade --pre managed-deepagents
  uv run python scripts/refresh_mda_oauth_catalog.py --write
  ```

## Move, rename, or remove a page

A source move is also a public-route migration. Start with the mover preview:

```bash
uv run docs mv src/langsmith/evaluation.mdx src/langsmith/deploy/evaluation.mdx --dry-run
```

After reviewing the result, rerun without `--dry-run`. The installed `docs` console script routes to `pipeline.cli:main`. Its mover scans Markdown, MDX, and notebook Markdown cells under `src/`, rewrites relative links that point to the moved file, moves the file, and recalculates relative links inside it. It leaves external, mail, absolute, and in-page-only links untouched. It does not update `src/docs.json`, redirects, or arbitrary public-route text, so search for the old route and review the diff.

Update the applicable `src/docs.json` navigation entry in the same change. When a public route is retired, add a redirect to its `redirects` array using site paths:

```json
{
  "source": "/langsmith/evaluation",
  "destination": "/langsmith/deploy/evaluation"
}
```

A retired versioned OSS route needs its language prefix. A shared OSS or Managed Deep Agents move can require a redirect for each former language route. A regrouping that retains the emitted route does not need a redirect. For a deletion, redirect to the closest useful successor.

`scripts/check_removed_pages_redirects.py` protects both sides of this contract. It verifies that navigation paths resolve to an existing `.mdx` or `.md` source, including shared-source mappings for Python and JavaScript routes. It compares base and proposed navigation and, if a removed page no longer has a source, requires a matching redirect. A `:path*` source can cover a route family. Leaving a source in place is the only removed-navigation case that does not require a redirect.

## Regenerate and validate the correct surface

Use generated output to validate inputs, never as an editable source of truth. Start with the narrowest check that covers the change, and use a clean build for navigation, routing, preprocessing, generated structure, or deletion changes.

1. Lint prose edits:

   ```bash
   make lint_prose FILES="src/path/to/page.mdx"
   ```

2. Preview a page with `make dev` and inspect <http://localhost:3000>. It performs an initial build, watches `src/`, and serves Mintlify from `build/`. Inspect both routes for versioned content. Do not rely on the watcher after structural changes: its incremental path does not recreate the full tree.
3. Run `make build` for a clean full-tree result. It clears `build/`, so stale artifacts cannot hide a route or deletion problem.
4. Run `make broken-links` for route or link changes, or `make broken-links-with-anchors` when fragments change. These targets build first, run Mint from `build/`, and filter known OpenAPI-generated and standalone-snippet noise. Remaining indented link lines are failures.
5. Run focused checks when applicable: `make check-cross-refs` for `@[...]`; `make test-code-samples FILES="..."` and `make code-snippets` for examples; `--check-docs-urls` and the integration refresh for listing metadata; and focused pytest when changing builder, generator, watcher, mover, or redirect behavior.
6. Invoke `docs-review` when finished prose changed. Hand off the source/configuration diff with the commands run, their results, and any check not run.

## Completion checklist

- [ ] The requested change used the matching authoring skill and selected the owner before editing.
- [ ] Authored content changed under `src/`; neither `build/` nor another generated result was hand-edited.
- [ ] A new or moved page has the correct extensionless `src/docs.json` navigation path.
- [ ] Shared and special route models have their required language or unversioned entries.
- [ ] A retired public route has an appropriate `docs.json` redirect.
- [ ] Samples, snippets, and integration tables were changed through their inputs and regenerated.
- [ ] Prose, rendering, links, references, and focused behavior were validated as appropriate.
- [ ] Completed prose received a diff-scoped `docs-review` review.

## See also

- [Source directory map](/openwiki/architecture/source-map.md)
- [Language versioning strategy](/openwiki/concepts/versioning.md)
- [Agent authoring skills](/openwiki/operations/agent-skills.md)
- [Testing overview](/openwiki/testing/test-overview.md)
- [Integration listing automation](/openwiki/workflows/integration-listing-automation.md)
- [Local development workflow](/openwiki/workflows/local-development.md)
