---
type: documentation metadata workflow
title: Integration Listing Automation
description: How integration metadata becomes hosted guides, external listings, generated download tables, and the Python provider overview. Covers ownership boundaries, scheduled regeneration, URL safety validation, and the checks required for safe changes.
tags: [integrations, documentation, metadata, automation, validation]
verified:
  - by: openwiki/0.4.3
    at: 2026-10-26T08:26:41.390Z
sources:
  - id: openwiki-source-8bdd8b6031ea08044f515d8c
    resource: repo://.agents/skills/submit-integration/SKILL.md
  - id: openwiki-source-1bf310cf2d4f8606635de732
    resource: repo://.github/workflows/check-external-doc-links.yml
  - id: openwiki-source-164e2da859b5277df81c7d94
    resource: repo://.github/workflows/ci.yml
  - id: openwiki-source-4de47c60d7e3210385c34d35
    resource: repo://.github/workflows/update-package-downloads.yml
  - id: openwiki-source-e52f38a56cc76188818237f7
    resource: repo://packages.yml
  - id: openwiki-source-0539c4d1a36abb10d1ed2fa9
    resource: repo://pipeline/tools/partner_pkg_table.py
  - id: openwiki-source-ac5a96b2eaef63c5d8d74d9a
    resource: repo://scripts/check-legacy-doc-links.sh
  - id: openwiki-source-0d19fa2f26e6485d05a6b929
    resource: repo://scripts/data/integration_external_docs.yaml
  - id: openwiki-source-250d64a0be85992104c0f95b
    resource: repo://scripts/flag_hosted_docs_candidates.py
  - id: openwiki-source-d4fdd9dfc4cf980ce0889985
    resource: repo://scripts/packages_yml_get_downloads.py
  - id: openwiki-source-63d8ba810a7c0181c548a307
    resource: repo://scripts/refresh_integration_downloads.py
  - id: openwiki-source-1f06ff54a6b42441ba3f34c3
    resource: repo://src/oss/contributing/publish-langchain.mdx
  - id: openwiki-source-7be0fdefc402d868b9f2fdca
    resource: repo://tests/unit_tests/test_refresh_integration_downloads.py
generated: { by: "openwiki/0.4.3", at: "2026-10-26T08:26:41.390Z" }
---

# Integration Listing Automation

Integration discovery is assembled from distinct owned inputs rather than edited as a single page. A listing can have a hosted MDX guide, an external table entry, an authored provider card, and a package-registry entry; not every integration has every surface. The automation has two independent generated products:

- **Component download snippets** combine hosted-guide `integration:` frontmatter and external-listing YAML. They are consumed by component landing pages.
- The **Python provider overview** is generated from `packages.yml`, with the authored Python provider-card catalog participating in link resolution.

Generated snippets and `src/oss/python/integrations/providers/overview.mdx` are outputs. Change the owning metadata or generator, then regenerate; do not preserve a hand-edited generated result.

## Listing decision and source ownership

A full hosted guide is for integrations with at least 50,000 monthly PyPI or npm downloads, or an explicit maintainer featured decision. An integration below that threshold is listed externally instead of receiving a new hosted MDX page. The decision does not make `featured: true` automatic: that is a maintainer decision. When moving an integration to a hosted guide, remove its matching external YAML row to avoid two table rows.

| Owned input | Responsibility | Change when |
| --- | --- | --- |
| `scripts/data/integration_external_docs.yaml` | Third-party rows grouped as `language` then `component`; `name`, registry package, `docs_url`, and supported component metadata | Adding, correcting, or removing an external listing |
| Hosted integration MDX frontmatter under `src/oss/{python,javascript}/integrations/` | The hosted row's display name, PyPI/npm package, featured/deprecated status, and component capabilities | Changing a hosted guide's listing metadata |
| `packages.yml` | Package/repository registry, monthly download record, JS package mapping, visibility, and maintainer-only `highlight` | Changing the Python provider overview's package input |
| `src/oss/python/integrations/providers/all_providers.mdx` | Authored provider discovery cards and their destinations | Adding or correcting provider discovery content or an overview-link fallback |

The external YAML comments define the link preference: partner documentation, then a GitHub repository, then a PyPI/npm page. It is the canonical source for external language/component entries. Hosted rows instead come from `integration:` frontmatter: for example, Browser Use supplies `name` and `pypi`, while the Azure Cosmos DB vector-store guide supplies `featured` and declared vector-store capabilities. A page without an `integration:` mapping or a `name` is skipped with a warning rather than becoming a row.

`all_providers.mdx` is authored content, not a generated provider overview. In particular, a card can link to an external destination, while a hosted provider page has a site-relative destination. The Python overview generator parses these cards as a fallback, so card title and href changes can affect generated overview links.

```mermaid
flowchart TD
    Hosted["Hosted MDX integration frontmatter"] --> Rows["Collect component rows"]
    External["External listing YAML"] --> Validate["Validate external docs URL"]
    Validate --> Rows
    Rows --> Downloads["Fetch cached registry downloads"]
    Downloads --> Render["Render component download snippets"]
    Packages["packages.yml"] --> Overview["Generate Python provider overview"]
    Cards["Authored Python provider cards"] --> Overview
```

This diagram separates the component-table pipeline from the provider-overview pipeline.

## Component download-table generation

Run the generator from the repository root:

```bash
uv run python scripts/refresh_integration_downloads.py --write
```

It scans configured component directories for Python and JavaScript, excluding index pages, templates, and example data. It collects hosted rows, appends external rows for the same language/component, then sorts rows with known downloads descending and name secondarily; unavailable counts are last. The run caches each registry/package download lookup. npm and PyPI requests retry HTTP 429 up to six times with exponential backoff; other request, parsing, or missing-data failures leave that row without a package/download value instead of failing the full collection.

The generated files begin with a do-not-edit marker. An all-rows `*-downloads.mdx` snippet is written for every nonempty component. A `*-featured.mdx` snippet is also written for chat, even if empty, and for any other component with featured rows. The renderer chooses component-specific columns: chat capabilities, middleware availability/source, retriever fields, and vector-store capability columns only when at least one row declares the corresponding value. It embeds sort values in capability and download cells for the client-side table sorter.

Without `--write`, the command renders tables to standard output. `--language` and `--component` limit it to the supported choices or `all`. Use these options for focused regeneration, but run a full regeneration before merging a cross-cutting metadata change.

### External URL boundary

External `docs_url` values are untrusted metadata because they become Markdown link destinations. The generator permits `https://`, `http://`, or a site-relative path beginning with exactly one `/`; it rejects blank values, protocol-relative `//…`, and other schemes such as `javascript:`, `data:`, and `vbscript:`.

```mermaid
flowchart TD
    URL["External docs URL"] --> Present{"Nonblank string"}
    Present -- "No" --> Missing["Validation error or skipped row"]
    Present -- "Yes" --> Allowed{"HTTP S or HTTP or single slash path"}
    Allowed -- "No" --> Unsafe["Reject unsafe URL"]
    Allowed -- "Yes" --> ExternalLink["Render external link"]
```

This is the link-safety boundary before external metadata reaches generated MDX.

There are deliberately different failure semantics by entrypoint:

- `--check-docs-urls` validates every external YAML row without network calls or writes, reports missing or unsafe values, and exits nonzero on errors.
- Normal collection warns and skips an external row missing `docs_url`, but an unsafe external URL raises `ValueError` and stops generation.
- A hosted row with an unsafe optional `docs_url` loses that URL and renders its normal internal route instead, so `_model_link` never emits an unsafe href.

Validate listing URLs before regeneration:

```bash
uv run python scripts/refresh_integration_downloads.py --check-docs-urls
```

The pull-request workflow named **Check for External Doc Links** is complementary rather than a replacement for this validator: for pull requests to `main` that touch Markdown-related paths, it runs a shell scan across authored `.md` and `.mdx` files and fails on retired documentation hostnames (apart from the Helm exception). Replace such links with relative documentation routes or `reference.langchain.com` API links.

## Python provider overview

The overview generator has a different input contract:

```bash
uv run python pipeline/tools/partner_pkg_table.py
```

It reads `packages.yml`, ignores core package names, derives a short name and display title, rejects `has_reference_docs: true` together with `integration: false`, and keeps packages with at least 100,000 downloads unless `highlight` is set. Highlighted packages sort before ordinary packages, then both groups sort by downloads; the output is limited to 50 rows. `highlight` is explicitly documented as a maintainer-only way to feature strategic or new integrations.

The generator chooses a provider destination in this order: an absolute `provider_page` in `packages.yml`; an existing hosted provider page using `provider_page` or the derived short name; a matching `all_providers.mdx` card href; the configured GitHub repository; and finally PyPI. Thus, update the package record when package identity or an explicit destination changes, and update the provider card when its discovery destination is intentionally the fallback.

The generated overview itself carries a do-not-manually-edit marker. CI regenerates it and fails if the checked-in result differs, directing changes to `packages.yml` or `partner_pkg_table.py`.

## Scheduled refresh and hosted-guide follow-up

`update-package-downloads.yml` runs every Sunday at 23:59 UTC and may also be manually dispatched. Its read-only generation job refreshes package downloads, writes the provider overview, regenerates integration snippets, and then uploads only `packages.yml`, the overview, and generated snippets to the write-capable job. The latter exits without a PR when those tracked paths are unchanged; otherwise it creates a timestamped branch and an automated PR with squash auto-merge enabled.

```mermaid
flowchart TD
    Schedule["Sunday schedule or manual dispatch"] --> Counts["Refresh packages.yml downloads"]
    Counts --> Provider["Generate provider overview"]
    Provider --> Snippets["Regenerate integration snippets"]
    Snippets --> Flag["Check external hosted-guide candidates"]
    Flag --> Artifact["Upload designated generated paths"]
    Artifact --> Diff{"Tracked files changed"}
    Diff -- "No" --> NoPR["Exit without PR"]
    Diff -- "Yes" --> PR["Open automated update PR"]
```

This workflow separates read-only generation from the job permitted to write a branch and pull request.

The package refresher detects duplicate package names, avoids refetching a package updated in the previous 24 hours, records a missing Pepy badge as zero, and timestamps refreshed records. The same scheduled workflow also looks for external entries at the 50,000-download threshold. It is a dry run without both `LINEAR_API_KEY` and `LINEAR_TEAM_KEY`; with both configured, it creates Linear follow-up only after searching by a stable title fragment so changing counts do not create duplicate open issues.

## Change and verification procedure

1. Decide whether the integration is a hosted guide or external listing from measured monthly registry downloads and a maintainer feature decision. Do not use a generated table as the source of truth.
2. Change the owner: hosted `integration:` frontmatter, external YAML, `packages.yml`, an authored provider card, or generator code. If promoting an external listing to a guide, remove the external row.
3. Validate external links, then regenerate the affected component tables and, when package/provider-link inputs changed, the Python overview.
4. Inspect the generated diff for component, language, links, capability columns, featured rows, and unavailable-download fallback. Do not hand-patch a snippet or overview.
5. Run focused URL and rendering coverage when changing the download generator or its metadata rules:

   ```bash
   uv run pytest tests/unit_tests/test_refresh_integration_downloads.py
   ```

The focused tests cover accepted and rejected URL forms, ensure an unsafe URL cannot enter a rendered link, validate the repository YAML, and verify Markdown-cell normalization. CI independently detects manual drift in the generated provider overview; the scheduled workflow provides recurring regeneration of both output families.

## Related pages

- [Source Directory Map](/openwiki/architecture/source-map.md)
- [GitHub Actions and CI/CD](/openwiki/integrations/github-actions.md)
- [Adding pages](/openwiki/operations/adding-pages.md)
- [Quickstart](/openwiki/quickstart.md)
- [Testing overview](/openwiki/testing/test-overview.md)
