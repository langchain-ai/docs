---
type: workflow guide
title: Local Development Workflow
description: Set up and operate the local documentation build and Mintlify preview loop. Covers full and incremental builds, recovery from generated-output drift, Mint working-directory rules, and focused validation.
tags: [local-development, documentation, mintlify, build-system, workflow]
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
verified:
  - by: openwiki/0.4.3
    at: 2026-09-19T08:18:43.281Z
generated: { by: "openwiki/0.4.3", at: "2026-09-19T08:18:43.281Z" }
---

# Local Development Workflow

The local loop has a strict input/output boundary: author documentation, navigation, and assets in `src/`; the Python pipeline generates the Mintlify-facing `build/` tree. `build/` is disposable output. Never edit it directly: a full build removes and recreates it.

## First-time setup

The checkout requires Python 3.13 or later, Node.js, and `uv`. Install Python dependency groups, project npm dependencies, the global Mintlify CLI, and local Claude Code skill links:

```bash
git clone https://github.com/langchain-ai/docs.git
cd docs
make install
```

`make install` runs `uv sync --all-groups`, `npm install`, and `npm install -g mint@latest`; it also invokes `make skills`. That target links each canonical `.agents/skills/<name>/` directory into gitignored `.claude/skills/`, preserves non-symlink personal entries, and removes stale symlinks. Re-run `make skills` after pulling a newly added or renamed skill.

If the `docs` console script is unavailable after installation, open a new shell. Confirm the separate global executable with `mint --version`.

## Choose an entrypoint

Use Make targets for normal checkout work. `make dev` and `make build` run `npm install` first and invoke the pipeline with the repository root on `PYTHONPATH`.

```bash
make dev                         # full build, watch, and local preview
make build                       # full build, then exit
uv run pipeline dev              # direct development command
uv run pipeline dev --skip-build # reuse a suitable existing build tree
uv run pipeline build            # direct one-shot build
```

The CLI exposes `docs build --watch`, but the build command does not inspect command arguments and returns after one build. Use `dev` for supported watch behavior.

## Start the edit–preview loop

```bash
make dev
```

Unless `--skip-build` is set, development mode first performs a full build. It then watches `src/` recursively and starts `mint dev --port 3000` from `build/`. Open <http://localhost:3000> and check the rendered route, navigation, formatting, and links.

```mermaid
flowchart TD
  Start["make dev"] --> Decide{"Skip initial build"}
  Decide -->|"No"| Full["Full build to build"]
  Decide -->|"Yes"| Existing["Use existing build tree"]
  Full --> Services["Start watcher and Mint dev"]
  Existing --> Services
  Services --> Edit["Save a supported src file"]
  Edit --> Filter{"Ignored or unsupported"}
  Filter -->|"Yes"| Ignore["Ignore event"]
  Filter -->|"No"| Queue["Queue changed path"]
  Queue --> Delay["Debounce for 0.2 seconds"]
  Delay --> Rebuild["Incrementally rebuild files"]
  Rebuild --> Touch["Touch generated output"]
  Touch --> Preview["Mint detects update"]
```

This flow shows the clean full-build reset followed by focused updates during a preview session.

### Startup, failure, and shutdown

An initial-build failure returns failure before the watcher or Mint process starts. `--skip-build` deliberately bypasses that guard and only warns when `build/` does not exist, so use it only after a brief interruption with a suitable generated tree. If `mint` cannot start, the command exits with installation guidance. After startup, a nonzero Mint exit, a cancelled watcher, or an unexpected watcher stop makes development mode fail.

Press Ctrl+C to stop. The command signals watcher shutdown, cancels a pending debounced rebuild, terminates Mint, waits up to five seconds, then kills Mint if necessary. It cancels and joins the watcher, Mint wait, and log-forwarding tasks. On Windows Mint is launched through a shell for `.CMD` compatibility; Unix uses direct execution.

## What an incremental update does

The watcher uses `watchdog` events from `src/`. Create and modify events for builder-supported extensions are queued; this includes Markdown and MDX, JSON, images and video, YAML, styles, JavaScript/JSX/TSX, text, HTML, and fonts. It ignores editor backups ending in `~`, `.bak`, or `.orig`, plus hidden temporary files ending in `.tmp`, `.temp`, or `.swp`.

Queued paths are deduplicated in a set. Every event resets a 0.2-second debounce task, which batches rapid writes. One path rebuilds on one worker; a larger batch uses a `ThreadPoolExecutor` with at most four workers and reports progress. The watcher then touches emitted files so Mint notices their timestamps and hot-reloads. Versioned OSS content can touch both Python and JavaScript outputs, while OpenWiki and Deep Agents Code use one unversioned output.

A deletion is intentionally less complete: the watcher removes only the source-relative path under `build/` when it exists. It does not apply the builder's routing map, so routed output can remain until a full build.

## Know when to reset with a full build

`make build` runs the full `DocumentationBuilder.build_all()` lifecycle without watching. The builder clears `build/`, emits Python and JavaScript OSS variants, builds unversioned Deep Agents Code, OpenWiki, and LangSmith content plus managed Deep Agents variants, copies shared files and npm snippet components, and generates LLM artifacts.

Incremental watcher builds call the per-file path. They do not rerun whole-tree shared-file collection, npm snippet overlays, or LLM artifact generation. Run `make build` after navigation, routing, shared-asset, snippet-component, broad preprocessing, deletion, or other cross-file changes, and whenever the preview looks stale. Fix authored input or generator configuration and rebuild—never patch `build/`.

For routing and preprocessing details, see [Build System Architecture](/openwiki/architecture/build-system.md). For the renderer-facing contract, see [Mintlify Integration](/openwiki/integrations/mintlify.md).

## Validate the change

Choose the narrowest check that establishes the changed boundary:

| Change boundary | Command | What it checks |
| --- | --- | --- |
| Pipeline, preprocessing, routing, or watcher behavior | `make test` | Pytest with network sockets disabled except Unix sockets. Focus the watcher suite with `make test TEST_FILE=tests/unit_tests/test_watcher.py`. |
| Python tooling and spelling | `make lint` | Ruff format/check, `ty`, and Codespell on `src`. |
| Markdown style | `make lint_md` | Markdownlint below `src`; use `make lint_md_fix` to apply its fixes. |
| Prose | `make lint_prose` | Installs the Vale version pinned in `.mise.toml` to `.bin/vale`, then checks `src` or `FILES`. |
| Generated links, redirects, and anchors | `make broken-links-with-anchors` | Builds first, runs Mint from `build/` with `--check-anchors` and `--check-redirects`, and filters known non-actionable reports. |
| Source `@[ref]` references | `make check-cross-refs` | Checks source references separately from Mint's built-site check. |

The focused watcher tests currently cover backup and temporary-file filtering. Add focused tests when changing event filtering, rebuilding, routing, or shutdown behavior. See [Testing Overview](/openwiki/testing/test-overview.md) for the wider validation model.

## Run Mint safely and recover from common problems

Run raw `mint` commands from `build/`, not the project root. From the root, Mintlify can scan `.venv` package files and parse Python-package Markdown as MDX. Prefer the wrappers, which build and use the generated working directory:

```bash
make broken-links
make broken-links-with-anchors
```

For a raw command, use:

```bash
cd build
mint broken-links
```

Both link-check targets pass `--check-redirects`, filter known deployment-generated and standalone-snippet reports, and fail on remaining indented link lines; the anchor target additionally passes `--check-anchors`. The same working-directory rule applies to raw export and OpenAPI commands. If Mint reports compatibility errors, update it with `mint update` or `npm install -g mint@latest`.

When Mint warns that a new navigation page does not exist, ensure `src/docs.json` lists the root `index` route without an extension:

```json
{
  "group": "New group",
  "pages": ["new-group/index", "new-group/other-page"]
}
```

### Recovery checklist

1. Re-run `make install` if Python dependencies, npm packages, Mint, or Claude Code skill links are missing.
2. For a failed initial build or suspicious preview, run `make build` and correct `src/` or pipeline configuration.
3. If Mint exits, read its forwarded logs, update Mint when needed, and restart `make dev`.
4. For navigation, generated artifacts, routing, or deletion behavior that an incremental update cannot explain, run a full build.
5. Run raw Mint commands only after `cd build`; otherwise use the Make target.

## Related pages

- [Quickstart](/openwiki/quickstart.md)
- [Build System Architecture](/openwiki/architecture/build-system.md)
- [Mintlify Integration](/openwiki/integrations/mintlify.md)
- [Documentation CLI Tools](/openwiki/operations/cli-tools.md)
- [Testing Overview](/openwiki/testing/test-overview.md)
