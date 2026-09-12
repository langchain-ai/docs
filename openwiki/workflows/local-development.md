---
type: workflow guide
title: Local Development Workflow
description: Set up the documentation toolchain, build the disposable Mintlify input tree, and run the local watched preview. This guide distinguishes the installed docs CLI from Make wrappers, explains incremental-build limits, and selects appropriate local validation.
tags: [local-development, documentation, mintlify, build-system, workflow]
verified:
  - by: openwiki/0.4.3
    at: 2026-09-12T08:18:19.154Z
sources:
  - id: openwiki-source-012f2c78e3b1446dfc35803f
    resource: repo://Makefile
  - id: openwiki-source-6e6efa1569f158fcdb678ef0
    resource: repo://pipeline/cli.py
  - id: openwiki-source-41f7c907e42a5efd3b3405cd
    resource: repo://pipeline/commands/build.py
  - id: openwiki-source-b481a230af378c0c50ed9994
    resource: repo://pipeline/commands/dev.py
  - id: openwiki-source-d0cdf44431684bdedf34705a
    resource: repo://pipeline/core/builder.py
  - id: openwiki-source-636af982f42ea94123d2d7e9
    resource: repo://pipeline/core/watcher.py
  - id: openwiki-source-05ccef8d4cf1698187f20464
    resource: repo://pyproject.toml
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
  - id: openwiki-source-16b92823fdcb07d686f2e27f
    resource: repo://tests/unit_tests/test_watcher.py
generated: { by: "openwiki/0.4.3", at: "2026-09-12T08:18:19.154Z" }
---

# Local Development Workflow

The local workflow has a strict source/output boundary: author content, navigation, and assets in `src/`; the Python pipeline generates the Mintlify-facing `build/` tree. `build/` is disposable output. Never edit it directly: a full build removes and recreates it.

## Prerequisites and setup

The checkout requires Python 3.13+, Node.js, and `uv`. Install the Python dependency groups, local npm dependencies, the global Mintlify CLI, and repository skills:

```bash
git clone https://github.com/langchain-ai/docs.git
cd docs
make install
```

`make install` runs `uv sync --all-groups`, `npm install`, `npm install -g mint@latest`, and the `skills` target. The project registers the `docs` console script. If `docs` is not available after installation, open a new shell; confirm the separately installed Mint executable with `mint --version`.

## Choose the right command layer

Use the installed **`docs` CLI** as the preferred direct entrypoint for documentation pipeline work. It is the project console script and dispatches to `pipeline.cli:main`:

```bash
docs dev                         # preferred direct edit-preview loop
docs dev --skip-build            # reuse an existing build tree
docs build                       # preferred direct clean, one-shot build
```

`uv run docs dev` and `uv run docs build` are useful when invoking the installed script through the project environment. `uv run pipeline dev` and `uv run pipeline build` invoke the same CLI module directly; the Make wrappers use this form after setting `PYTHONPATH`.

Use **Make wrappers** for setup and repository-defined validation, and when their npm-install behavior is useful:

```bash
make install                      # bootstrap dependencies and skills
make dev                          # npm install, then pipeline dev
make build                        # npm install, then pipeline build
make test                         # repository pytest policy
make broken-links-with-anchors    # build, then safe Mint validation
```

Thus `docs dev`/`docs build` are the preferred installed CLI commands, while `make dev`/`make build` are convenience wrappers—not a different build implementation. `make` is the authoritative interface for the lint, test, link, export, and other operational targets described below.

> **Do not rely on `docs build --watch`.** The parser accepts `--watch`, but `build_command` does not inspect it and performs one build before returning. `docs dev` (or its `make dev` wrapper) is the supported watcher entrypoint.

## Start the edit-preview loop

```bash
docs dev
```

Unless `--skip-build` is supplied, development mode runs the same full build used by `docs build`, then recursively watches `src/` and starts `mint dev --port 3000` with `build/` as its working directory. Review the rendered site at <http://localhost:3000>, including the route, navigation, formatting, and links.

```mermaid
flowchart TD
    Begin["docs dev"] --> Skip{"Skip initial build"}
    Skip -->|"No"| Full["Full build to build"]
    Skip -->|"Yes"| Existing["Use existing build tree"]
    Full --> Services["Start watcher and Mint dev"]
    Existing --> Services
    Services --> Edit["Save supported src file"]
    Edit --> Filter{"Ignored or unsupported"}
    Filter -->|"Yes"| Ignore["Ignore event"]
    Filter -->|"No"| Queue["Queue changed path"]
    Queue --> Delay["Debounce for 0.2 seconds"]
    Delay --> Rebuild["Incrementally rebuild files"]
    Rebuild --> Touch["Touch emitted output"]
    Touch --> Preview["Mint detects update"]
```

This shows the normal lifecycle: a full build establishes a coherent generated tree, then the watcher applies focused updates for the local preview.

### Startup, failure, and shutdown behavior

A normal dev start does not serve stale output after a failed initial build: it returns exit code 1 before it creates the watcher or Mint process. `--skip-build` intentionally bypasses that protection and only warns if `build/` is absent; use it only when a suitable generated tree already exists, for example after a brief interruption.

If the `mint` executable cannot be started, the command exits 1 and recommends `make install` or `npm install -g mint@latest`. Once Mint starts, its stdout is forwarded as info logs and stderr as error logs. Development waits until Mint exits or the watcher stops; a nonzero Mint exit, watcher cancellation, or unexpected watcher completion is a failure.

Press Ctrl+C to stop a session. The command shuts down the watcher, cancels pending debounced rebuild work, terminates Mint, waits up to five seconds, then kills Mint if it has not exited. It also cancels and gathers the watcher, process-wait, and log-forwarding tasks, avoiding a lingering local preview process.

## Watcher scope and incremental rebuilds

`watchdog` observes `src/` recursively. Create and modify events for builder-supported formats are queued: Markdown/MDX, JSON, images and video, YAML, CSS, JavaScript/JSX/TSX, text, HTML, and font files. Backup names ending in `~`, `.bak`, or `.orig`, and hidden temporary names ending in `.tmp`, `.temp`, or `.swp`, are ignored.

The watcher deduplicates pending paths in a set and resets a 0.2-second debounce timer for each event. A single file is built in a one-worker executor; a batch uses at most four workers and reports progress. Each batch then touches the applicable generated outputs so `mint dev` notices their timestamps. Ordinary OSS content can therefore refresh Python and JavaScript variants, while OpenWiki and Deep Agents Code content has one unversioned output.

Markdown rebuilds apply the same per-file preprocessing as a full build, including standard markdown preprocessing, language-specific snippet-import and route-link rewriting, `.md` to `.mdx` conversion, and source-link footer injection. This makes the watcher appropriate for ordinary content edits, but not a replacement for whole-tree generation.

### When a full build is mandatory

A full build clears `build/`, emits versioned OSS variants and unversioned content, creates Managed Deep Agents variants, copies shared files, overlays npm snippet components, then generates `llms.txt` and `llms-full.txt`. Incremental watcher builds only call the per-file path; they do **not** perform shared-file collection, npm overlay, or LLM-artifact generation.

Deletion is also intentionally limited. The watcher removes the source-relative path below `build/` when it exists rather than applying the builder’s full routing rules. Routed language variants or special outputs can therefore remain stale.

Run a full build whenever a change affects any of the following, then restart or continue `docs dev` to inspect the regenerated tree:

- routing or language-specific output behavior;
- `src/docs.json` navigation, redirects, or other site configuration;
- a deletion, rename, or move;
- shared assets or configuration, npm snippet components, or generated snippets;
- preprocessing that can affect other pages, link resolution, or derived `llms` artifacts; or
- any suspicious preview whose incremental state is difficult to explain.

```bash
docs build
# or, when the wrapper is desired:
make build
```

This recovery rule is deliberately conservative: fix source or pipeline inputs, never the generated files in `build/`.

## Local validation by change boundary

A rendered preview is necessary for presentation changes, but it is not sufficient validation for pipeline, routing, or site-wide behavior. Select checks by the affected boundary:

| Change boundary | Command | What it establishes |
| --- | --- | --- |
| Pipeline, preprocessing, routing, or watcher behavior | `make test` | Runs pytest with network sockets disabled except Unix sockets. Focus with `make test TEST_FILE=tests/unit_tests/test_watcher.py`. |
| Python tooling and source spelling | `make lint` | Runs Ruff format/check in diff mode, `ty check`, and Codespell on `src`. |
| Markdown/MDX style | `make lint_md` | Runs markdownlint over Markdown and MDX found below `src`; `make lint_md_fix` applies fixes. |
| Prose style | `make lint_prose` | Installs the Vale version pinned in `.mise.toml` into `.bin/vale` and checks `src`, or paths passed via `FILES`. |
| Generated internal links and anchors | `make broken-links-with-anchors` | Builds first, runs Mint against `build/` with `--check-anchors`, filters known non-actionable reports, then fails on remaining link lines. |
| Generated internal links without anchor checking | `make broken-links` | Uses the same build-and-filter boundary without `--check-anchors`. |
| Source `@[ref]` references | `make check-cross-refs` | Checks source references independently of Mint’s built-site check. |

Focused watcher tests cover backup and temporary-file filtering, including valid and edge-case names. Add focused tests when changing event filtering, debounce/rebuild behavior, routing, or shutdown behavior. See [Testing Overview](/openwiki/testing/test-overview.md) for broader test scope.

## Mintlify working-directory boundary

Prefer the Make wrappers for Mint validation. They build first and execute the raw Mint command from `build/`:

```bash
make broken-links
make broken-links-with-anchors
make check-openapi
make export
```

A raw `mint` command **must execute from `build/`**, never from the repository root. At the root, Mintlify can scan `.venv` files and parse Python package Markdown as MDX, causing parsing failures. When a raw command is necessary, change directories explicitly:

```bash
cd build
mint broken-links
```

The same rule applies to `mint export`, `mint openapi-check`, and comparable Mint operations. `make export` and `make check-openapi` already use `build/`. Offline export additionally requires a Mint CLI that supports `export`, Node LTS 20 or 22 rather than Node 25+, and an Enterprise Mintlify plan. `make htmltest` checks external URLs in the resulting export; it is not a substitute for `make broken-links-with-anchors`, because the export does not provide a reliable complete internal-page set.

If Mint reports compatibility errors, update the CLI:

```bash
mint update
# or
npm install -g mint@latest
```

If Mint warns that a new navigation page does not exist, inspect `src/docs.json`. A new group must include the root `index` route without a file extension:

```json
{
  "group": "New group",
  "pages": ["new-group/index", "new-group/other-page"]
}
```

## Recovery checklist

1. Verify Python, Node.js, `uv`, and global `mint`; rerun `make install` for missing dependencies.
2. For a failed initial build or suspicious generated state, run `docs build` (or `make build`) and correct inputs in `src/` or the pipeline.
3. For a Mint process failure, inspect the forwarded logs, update Mint if needed, and restart `docs dev`.
4. After routing, navigation, deletion, shared-output, or derived-artifact changes, perform a full build instead of trusting incremental state.
5. Use Make for the repository’s Mint checks; if invoking raw Mint, `cd build` first.

## Related pages

- [Quickstart](/openwiki/quickstart.md) for the concise contributor path.
- [Build System Architecture](/openwiki/architecture/build-system.md) for routing, preprocessing, and full-build ownership.
- [Mintlify Integration](/openwiki/integrations/mintlify.md) for renderer, navigation, OpenAPI, and export boundaries.
- [Documentation CLI Tools](/openwiki/operations/cli-tools.md) for the full command reference.
- [Testing Overview](/openwiki/testing/test-overview.md) for test and validation scope.
