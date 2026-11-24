---
type: concept
title: Repository Source Map
description: Maps the ownership boundaries for authored MDX, navigation, preprocessing, generated documentation, package metadata, release automation, code samples, and external API references. Use it to find the durable source before editing or regenerating an artifact.
tags: [documentation, build, automation, repository]
verified:
  - by: openwiki/0.4.3
    at: 2026-11-23T08:07:24.438Z
sources:
  - id: openwiki-source-9361c44d74c0e18006d0d76f
    resource: repo://.agents/skills/README.md
  - id: openwiki-source-21617d8a6b2b570989a7c900
    resource: repo://.github/workflows/check-version-claims.yml
  - id: openwiki-source-f2608d0d515da097485b6ec5
    resource: repo://.github/workflows/publish.yml
  - id: openwiki-source-0976291f8216a4c7151f20a7
    resource: repo://.github/workflows/refresh-external-versions.yml
  - id: openwiki-source-5153f86e64d6ee0b305f72b3
    resource: repo://.github/workflows/refresh-langsmith-openapi.yml
  - id: openwiki-source-4de47c60d7e3210385c34d35
    resource: repo://.github/workflows/update-package-downloads.yml
  - id: openwiki-source-8037e2358a2c4f9b2c722a11
    resource: repo://AGENTS.md
  - id: openwiki-source-15059b0f9cd678e06d6faff0
    resource: repo://docs-release-watch/agent.py
  - id: openwiki-source-12c8fb32a02de9dce773720f
    resource: repo://docs-release-watch/README.md
  - id: openwiki-source-2b522af6f26794f2e71ccb4e
    resource: repo://docs-release-watch/tools/products.py
  - id: openwiki-source-012f2c78e3b1446dfc35803f
    resource: repo://Makefile
  - id: openwiki-source-e52f38a56cc76188818237f7
    resource: repo://packages.yml
  - id: openwiki-source-d0cdf44431684bdedf34705a
    resource: repo://pipeline/core/builder.py
  - id: openwiki-source-17f3856bce97f37118963062
    resource: repo://pipeline/preprocessors/handle_auto_links.py
  - id: openwiki-source-dca59d03b9433eea9242c2e4
    resource: repo://pipeline/preprocessors/link_map.py
  - id: openwiki-source-0539c4d1a36abb10d1ed2fa9
    resource: repo://pipeline/tools/partner_pkg_table.py
  - id: openwiki-source-05ccef8d4cf1698187f20464
    resource: repo://pyproject.toml
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
  - id: openwiki-source-0a0a6c8d7a88288e6b6b9b5b
    resource: repo://scripts/check_cross_refs.py
  - id: openwiki-source-99b53585619b83f258314f8b
    resource: repo://scripts/check_version_claims.py
  - id: openwiki-source-fd0cb9d6fca56bf4963559e9
    resource: repo://scripts/extract_code_snippets.py
  - id: openwiki-source-560bf24db9566b97ee19e383
    resource: repo://scripts/generate_code_snippet_mdx.py
  - id: openwiki-source-d22c99c9d9abf854bbf1a047
    resource: repo://scripts/generate_egress_ip_tables.py
  - id: openwiki-source-2b15ecffacad911ef9db112f
    resource: repo://scripts/test_code_samples.py
  - id: openwiki-source-a9a8730b7e43a5ad2d0af4f1
    resource: repo://src/docs.json
  - id: openwiki-source-b376e653ac97bac12d5a0385
    resource: repo://src/langsmith/egress-ip-addresses.json
  - id: openwiki-source-607673c5c40214b511f9e0a7
    resource: repo://tests/unit_tests/test_check_version_claims.py
  - id: openwiki-source-30a490be0964e690a58135e7
    resource: repo://tests/unit_tests/test_egress_ip_inventory.py
generated: { by: "openwiki/0.4.3", at: "2026-11-23T08:07:24.438Z" }
---

This repository owns the source and build pipeline for `docs.langchain.com`, hosted by Mintlify. It does **not** build `reference.langchain.com`: that API reference site is generated and deployed outside this repository. The safe-change rule is to identify the durable owner first. `src/`, configuration, metadata, and committed inputs are sources; `build/` and explicitly generated documentation are outputs.

## Source-to-build control flow

```mermaid
flowchart TD
    Authored["Authored MDX and assets in src"] --> Builder["DocumentationBuilder build_all"]
    Navigation["src/docs.json site settings and navigation"] --> Builder
    Preprocess["pipeline preprocessors"] --> Builder
    Builder --> Build["Disposable build output"]
    Build --> Mintlify["Mintlify deployment to docs.langchain.com"]
    RefMap["link_map.py reference mappings"] --> Preprocess
    CrossCheck["check_cross_refs.py"] --> RefMap
    CrossCheck --> Authored
```

This diagram shows how authored content, navigation, preprocessing, and cross-reference validation converge in the local deployment artifact.

The builder deletes and recreates `build/`, creates versioned Python and JavaScript OSS routes, emits unversioned Deep Agents Code and OpenWiki content, builds LangSmith and Managed Deep Agents variants, and copies shared files. The root `pyproject.toml` provides the `docs` console entrypoint and requires Python 3.13 or newer. Use repository entrypoints rather than editing or invoking a generated route directly:

```bash
make build
make dev
make test
make broken-links-with-anchors
make check-cross-refs
```

The Makefile runs link validation from `build/` with redirect and anchor checks, and runs the Python suite with network sockets disabled except Unix sockets. The publication workflow builds on `main`, verifies that `build/` exists, stages it below `public/build`, and publishes that directory to the `prod` branch. `build/` is therefore a reproducible deployment artifact, not an editing surface.

## Durable ownership boundaries

| Concern | Durable owner | Safe change boundary |
| --- | --- | --- |
| Documentation prose, frontmatter, reusable MDX, assets, and executable examples | `src/` | Edit the owning source. `src/langsmith/` owns LangSmith material, `src/oss/` owns open-source material, `src/snippets/` owns reusable MDX, and `src/code-samples/` owns executable examples. |
| Site settings, navigation, and redirects | `src/docs.json` | Add or move a page deliberately in the reader-facing navigation; directory layout alone does not make a page discoverable. |
| Package registry and integration presentation inputs | `packages.yml` plus its consumers | Change metadata at the registry, then regenerate download, partner-package, and integration outputs. |
| Route shaping, language variants, preprocessing, and copied build content | `pipeline/` | Change implementation and focused tests together, then rebuild. |
| Deployment output | `build/` | Regenerate with `make build` or `make dev`; never patch it. |
| Always-applicable authoring rules | `AGENTS.md` | Keep the instruction copies named there synchronized when their mirrored sections change. |
| Task-specific agent procedures | `.agents/skills/<name>/SKILL.md` | Edit the canonical skill; run `make skills` to refresh Claude Code's local symlink view. |
| Automation and maintenance checks | `scripts/`, `Makefile`, `.github/workflows/`, and focused tests | Treat workflow, script, input data, and test as one operational contract. |
| Release-watch service | `docs-release-watch/` | Deploy independently with `uv run mda deploy`; it is not a Mintlify build input. |
| External API reference | Upstream reference generation service | Report defects through the repository's reference-docs issue template; there is no local reference build output to edit. |

`src/docs.json` independently owns Mintlify settings and reader-facing product/menu navigation. Its product labels do not mirror source directories: lifecycle menus can combine `src/oss/` and `src/langsmith/`. `src/index.mdx` is the home page, while `navigation.products` determines placement. Adding an MDX file without registering it in `docs.json` does not make it discoverable.

## Preprocessing and cross-references

`pipeline/preprocessors/link_map.py` is the durable map for `@[name]` references. It assembles Python and JavaScript scopes, prefixes relative targets with the corresponding external reference host, and preserves absolute URLs. `handle_auto_links.py` converts resolved entries to Markdown links, logs unknown names, and falls back from the special `global` scope to Python with an error log. `scripts/check_cross_refs.py` chooses defaults from source paths, changes scope inside `:::python` and `:::js` fences, and requires shared references to resolve in every applicable scope.

Change the map and focused preprocessing/check tests together. The map is not generated from `reference.langchain.com`; that site is an external boundary.

## Generated-artifact control flow

```mermaid
flowchart TD
    Samples["Runnable programs in src/code-samples"] --> Extract["extract_code_snippets.py"]
    Extract --> Intermediate["Ignored src/code-samples-generated"]
    Intermediate --> SnippetMDX["generate_code_snippet_mdx.py"]
    SnippetMDX --> Snippets["Committed src/snippets/code-samples"]
    Inventory["src/langsmith/egress-ip-addresses.json"] --> Egress["generate_egress_ip_tables.py"]
    Egress --> Tables["Marked generated blocks in cloud.mdx and cloud-platform-features.mdx"]
    Packages["packages.yml"] --> Downloads["download and partner-table generators"]
    Downloads --> PackageMDX["Committed integration and provider MDX"]
    OpenAPI["langsmith-platform-openapi.json"] --> MintAPI["Mintlify deployment endpoint pages"]
```

This diagram shows which committed files are generated views and which inputs must be changed instead.

### Runnable examples and snippets

`src/code-samples/` is the executable owner. `make test-code-samples` runs samples; `make code-snippets` extracts marked regions to the ignored `src/code-samples-generated/` intermediate and renders committed MDX under `src/snippets/code-samples/`. The extractor supports Python, TypeScript, Java, Kotlin, Go, and shell markers, including removal markers and code-group metadata, and fails on unclosed markers rather than emitting a partial example. Edit and test the program, regenerate the display snippets, and commit the rendered MDX—not the intermediate.

The sample harness is operationally separate from rendering. It supports `FILES`, `CODE_SAMPLE_PATHS`, four workers by default, opt-in `CODE_SAMPLE_TRACING=1`, bounded timeouts and rate-limit retries, and ordered serial chains for samples sharing datasets, experiments, or hub prompts. Trace collection is locked so parallel samples do not clobber the shared manifest.

### Egress inventory and public JSON

`src/langsmith/egress-ip-addresses.json` is the durable inventory for two generated documentation tables and the public JSON artifact. The generator accepts only schema version 1 with distinct global IPv4 `/32` records and the closed `service`, `cloud`, `region`, and `cidr` fields. It computes a SHA-256 version from canonical addresses, replaces exactly one marked block in each owning page, and makes `--check` fail on inventory-version or table drift. The builder copies the JSON bytes to the unversioned `build/langsmith/egress-ip-addresses.json`; that published file is a view, not a second data store.

```bash
uv run python scripts/generate_egress_ip_tables.py
uv run python scripts/generate_egress_ip_tables.py --check
```

Change the JSON inventory and regenerate both pages together. Do not hand-edit the tables or the build artifact.

### Package metadata and integration tables

`packages.yml` is a package metadata registry, not an API-reference source. Rows carry package identity, repositories, provider-page and JavaScript mappings, integration/highlighting/reference-doc policy, and machine-maintained download timestamps. The scheduled download workflow refreshes stale counts, generates the partner package table and integration download snippets, flags qualifying external integrations, and uploads the changed YAML and MDX as an artifact before creating a PR. The partner table applies its own exclusions and a 100,000-download inclusion threshold, bypassed for highlighted packages. Change the registry or generator policy, then review regenerated MDX.

### OpenAPI-generated endpoint pages

Mintlify generates endpoint pages from OpenAPI declarations at deployment time. Those pages are neither authored MDX nor local pipeline output. The committed `src/langsmith/langsmith-platform-openapi.json` is refreshed daily by a workflow running `process_langsmith_openapi.py`; it fetches the platform specification, filters fleet/internal endpoints, applies public-documentation processing, and opens or updates a refresh PR. Change the refreshed input or processing policy; never edit generated endpoint pages. `make check-openapi` validates the Agent Server specification after a build.

## Agent instructions and release watch

`AGENTS.md` owns always-applicable rules: do not edit `build/`, update `src/docs.json` for new pages, use valid frontmatter and supported icons, and test examples. It also identifies instruction files that must be synchronized. `.agents/skills/` supplies opt-in task procedures; most agents read it directly, while Claude Code uses the symlinks created by `make skills`. Skills should link to `AGENTS.md` rather than duplicate global invariants.

`docs-release-watch/` is a separately deployed Managed Deep Agent. Its product registry scopes OpenWiki, Deep Agents Python, Deep Agents Code, and Deep Agents JS by upstream repository, release tag prefix, source path, documentation path, language scope, and memory file. For releases 7–30 days old, the read-only Sonnet research phase uses release diffs, tagged source files, and docs coverage checks. The Opus shipping agent can then create one Linear DOC issue and one draft documentation PR per evidenced feature. Write tools re-verify citations and surgical edits; humans review draft PRs. Extending coverage means changing the product registry, matching product skill, and schedule prompt, then redeploying.

## External version checks and focused verification

`scripts/check_version_claims.py` resolves MDX package specifiers to PyPI or npm using syntax, nearby labels, conditional fences, and page-language defaults. Registry failures are unresolved; non-advisory runs fail only when a successfully fetched release set proves that a version is absent. The pull-request workflow checks only changed `src` MDX files selected from the merge base. The scheduled sweep checks all pages with `--advisory-only`, publishes its report, and does not fail the job for stale text or unavailable registries.

Focused tests under `tests/unit_tests/` protect builder transformations and maintenance invariants, including version claims, egress validation, and generated artifact convergence. Add or update a focused test when changing a generator, validator, or preprocessing rule.

## Safe-change checklist

1. **Page or route:** edit the owner in `src/`, update `src/docs.json`, and preserve redirects.
2. **Build behavior:** change `pipeline/`, add focused tests, rebuild, and run link checks.
3. **Cross-reference:** update `link_map.py` and run `make check-cross-refs`.
4. **Code sample:** modify and test `src/code-samples/`, run `make code-snippets`, and commit generated MDX.
5. **Egress:** edit the JSON inventory, regenerate, and run `--check`.
6. **Package metadata:** edit `packages.yml` or its generator and review generated MDX.
7. **OpenAPI:** update the specification or processor/workflow boundary, not generated endpoint pages.
8. **Agent procedure:** choose `AGENTS.md` for a global rule or `.agents/skills/` for an opt-in procedure, then maintain mirrors.
9. **Release watch:** update registry, skill, and schedule, then run `uv run mda deploy`.

## Related pages

- [Build system](/openwiki/architecture/build-system.md)
- [Preprocessing](/openwiki/concepts/preprocessing.md)
- [Mintlify integration](/openwiki/integrations/mintlify.md)
- [Reference docs](/openwiki/integrations/reference-docs.md)
- [Code sample lifecycle](/openwiki/workflows/code-sample-lifecycle.md)
