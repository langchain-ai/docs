---
type: documentation code-sample workflow
title: Code Sample Lifecycle
description: How executable documentation samples are marked, tested, extracted, and rendered as generated MDX. Covers the MCP multimodal, tool-error, and metadata examples, hidden harnesses, trace-publication constraints, and safe regeneration.
tags: [code-samples, documentation, mdx, testing, tracing, mcp]
verified:
  - by: openwiki/0.4.3
    at: 2026-09-19T08:18:43.281Z
sources:
  - id: openwiki-source-ddbddbe474c8dc57119458d7
    resource: repo://.agents/skills/docs-code-samples/SKILL.md
  - id: openwiki-source-751a704f6f25787856371177
    resource: repo://.github/workflows/test-code-samples-linear.yml
  - id: openwiki-source-97746d8f3662d803e625550e
    resource: repo://.github/workflows/test-code-samples.yml
  - id: openwiki-source-ea70eb6c045047448e446296
    resource: repo://.gitignore
  - id: openwiki-source-012f2c78e3b1446dfc35803f
    resource: repo://Makefile
  - id: openwiki-source-2654e40275744504b4ca7e2b
    resource: repo://scripts/code_sample_tracing.py
  - id: openwiki-source-fd0cb9d6fca56bf4963559e9
    resource: repo://scripts/extract_code_snippets.py
  - id: openwiki-source-560bf24db9566b97ee19e383
    resource: repo://scripts/generate_code_snippet_mdx.py
  - id: openwiki-source-2b15ecffacad911ef9db112f
    resource: repo://scripts/test_code_samples.py
  - id: openwiki-source-2b3973f7b179794fb4534f89
    resource: repo://src/code-samples/go.mod
  - id: openwiki-source-4da1d93ce5e2fa6e9d44047c
    resource: repo://src/code-samples/go.sum
  - id: openwiki-source-53420d9e834269902e815090
    resource: repo://src/code-samples/langchain/mcp-multimodal-tool-content.py
  - id: openwiki-source-d8bc8e4e9d711cf2bbb48a0e
    resource: repo://src/code-samples/langchain/mcp-tool-results.py
  - id: openwiki-source-eb4eef69988e60f56a6075f4
    resource: repo://src/snippets/code-samples/mcp-tool-errors-py.mdx
  - id: openwiki-source-b68d7bad2afd9a38e8c331d5
    resource: repo://tests/unit_tests/test_generate_code_snippet_mdx.py
generated: { by: "openwiki/0.4.3", at: "2026-09-19T08:18:43.281Z" }
---

## Ownership and lifecycle

Runnable programs under `src/code-samples/` are the editable source of truth. They contain one or more marked regions that become documentation snippets, while the whole source file is executed by its language toolchain. `src/code-samples-generated/` is a gitignored extraction intermediate; committed `src/snippets/code-samples/` MDX is a derivative. Change the source, validate it, run regeneration, and review the resulting MDX diff rather than hand-editing a generated snippet.

```mermaid
flowchart TD
  Source["Runnable source sample"] --> Execute["Run selected source file"]
  Execute --> Result{"Process succeeded"}
  Result -->|"yes"| Extract["Extract marked regions"]
  Extract --> Intermediate["Ignored intermediate files"]
  Intermediate --> Render["Generate snippet MDX"]
  Render --> Review["Review committed derivative diff"]
  Result -->|"tracing enabled"| Markers{"Exactly one marker"}
  Markers -->|"yes"| Publish["Share qualifying trace"]
  Publish --> Manifest["Trace-link manifest"]
  Manifest --> Render
  Markers -->|"no"| Exclude["Record multi-snippet exclusion"]
```

This is the source-to-snippet lifecycle. Trace sharing is a separate, credentialed publication path and does not make a multi-snippet source trace-eligible.

## Authoring visible code and hidden execution harnesses

Supported sample extensions are `.py`, `.ts`, `.java`, `.kt`, `.go`, and `.sh`. Mark a visible region with matching `:snippet-start: <id>` and `:snippet-end:` comment lines: use `#` in Python and shell, and `//` in TypeScript, Java, Kotlin, and Go. The line-based extractor accepts indented markers, removes matched `:remove-start:` / `:remove-end:` regions, dedents the body, normalizes output newlines, and fails on an unclosed marker.

Each ID must end with the source-language output suffix: `-py`, `-js`, `-java`, `-kt`, `-go`, or `-sh`. That suffix selects the MDX fence language; an extracted file with a mismatched ID suffix is skipped by the generator. The ID also becomes the MDX basename, so it must be unique and stable.

A remove block is for test-only imports, local servers, assertions, credentials-only setup, or an execution tail that should not be shown. It does **not** isolate its code from the program: the source file runs as a whole. Keep it after the visible setup whenever possible, and never succeed by exiting before the snippet executes. In TypeScript, all visible regions and remove blocks share module scope, so independently runnable examples with duplicate imports or top-level bindings need separate files.

Optional presentation directives belong at the very start of an extracted body. `:codegroup-tab:` supplies a CodeGroup tab title and `:codegroup-fence-mods:` supplies fence modifiers; generation strips both directives from displayed code.

### MCP examples: source structure is the contract

`mcp-multimodal-tool-content.py` is a one-snippet Python sample. Its visible function adapts an MCP server, invokes an agent, and reads `ToolMessage.content_blocks`, showing text and standardized image data. Its trailing hidden harness creates a local FastMCP image tool, executes the visible function, and, if model-side image processing rejects the tiny fixture, directly invokes the adapted tool before asserting that an image block exists. This preserves a runnable validation path while documenting the agent-facing content-block API rather than the fixture mechanics.

`mcp-tool-results.py` deliberately has **two** visible snippets in one executable file:

- `mcp-tool-errors-py` demonstrates that a server-side tool error is exposed as a `ToolMessage` whose `status` is `"error"`; transport failures remain exceptions.
- `mcp-tool-metadata-py` reads nested MCP adapter metadata defensively and returns `False` when annotations are absent.

One hidden FastMCP calculator harness exercises the error path, accepts either the failed tool message or a model response mentioning the error, then directly inspects the adapted tool's server metadata and calls `is_destructive`. Because the trace collector counts markers per **source file**, this useful collocation makes the file ineligible for a public trace link; splitting it is required only if trace publication is desired.

The committed `mcp-tool-errors-py.mdx` is currently stale relative to its source: it retains an older user prompt, while the source now uses the explicit `"Use the divide tool to calculate 10 divided by 0."` request. The new metadata marker likewise requires regeneration to produce its `mcp-tool-metadata-py.mdx` derivative. Do not patch either generated result manually; regenerate from the runnable source.

## Test first, then regenerate

Use a focused live check for changed samples, then regenerate both MCP derivatives together:

```bash
make test-code-samples FILES="src/code-samples/langchain/mcp-multimodal-tool-content.py src/code-samples/langchain/mcp-tool-results.py"
make code-snippets
make test TEST_FILE=tests/unit_tests/test_generate_code_snippet_mdx.py
```

`FILES` is a space-separated explicit list. Missing, unsupported, or out-of-tree entries are warned about and skipped. Without it, the runner recursively selects eligible samples (excluding `node_modules` and `__pycache__`) in Python, TypeScript, Java, Kotlin, Go, and shell order. The runner uses `uv run python`, `npx tsx`, JBang with Java 21, `go run`, or `bash`; its default per-file timeout is 1,200 seconds and is configurable through `CODE_SAMPLE_TIMEOUT_SECONDS`. Samples inherit the environment and can require provider credentials, network access, or `POSTGRES_URI`.

A nonzero exit, timeout, missing executable, or trace-collection error fails the run. The exception is a recognizable LangSmith HTTP 429: it is retried three total times with 15-second waits and then reported as skipped rather than failed. A skipped sample is not proof of validity and does not collect a trace.

`make code-snippets` first extracts and then generates MDX. Extraction writes `<source-stem>.snippet.<snippet-id>.<extension>` beneath the ignored intermediate directory; generation scans every existing intermediate and writes `<snippet-id>.mdx` under `src/snippets/code-samples/`. A full extraction clears supported intermediates before rebuilding them.

For fast iteration, `CODE_SNIPPET_SOURCES` can restrict extraction to existing supported files beneath `src/code-samples/`, for example:

```bash
CODE_SNIPPET_SOURCES="src/code-samples/langchain/mcp-tool-results.py" make code-snippets
```

This only replaces intermediates for the selected source stem; MDX generation still scans all remaining intermediates. It is appropriate for a focused source update such as the MCP file, but a full `make code-snippets` is the safe repository-wide reconciliation before committing generated output.

## Rendering behavior and focused unit coverage

Generation normally emits a language fence. For eligible Python and TypeScript agent model strings it can instead generate a seven-provider Deep Agents CodeGroup. `# KEEP MODEL` or `// KEEP MODEL` immediately before a model occurrence prevents replacement. Embeddings constructors, model IDs containing `embedding`, and provider-specific constructors such as `ChatOpenAI` are deliberately excluded so generated variants remain runnable. The focused generator unit tests protect these boundaries: a RAG sample keeps its embedding model across all tabs while varying the agent model, and excluded or kept models remain a single block.

The generator loads `src/code-samples/trace-links.json` and appends or replaces a `View example trace` Card only when the manifest contains a URL for the snippet. Regeneration also removes a stale trailing trace CTA when no URL exists.

## Trace publication and CI

`make update-code-sample-traces` is intentionally different from ordinary testing. It requires `LANGSMITH_API_KEY`, sets tracing, uses `LANGSMITH_PROJECT` or `docs-code-samples`, runs the samples, shares qualifying LangSmith runs publicly, updates the trace manifest, and regenerates MDX. Use it only with authorized credentials and public-safe sample data.

Only a successful source with exactly one snippet marker can acquire a link. The collector polls for a recent agent-like root run, shares it, and stores URL, source, run identifiers, name, and update time. For multiple markers it records the source and IDs under `skipped_multi_snippet` and removes stale entries for those IDs. Thus `mcp-tool-results.py` remains fully testable and generates two MDX files, but cannot receive a trace card as currently structured.

The **Test Code Samples** workflow skips fork pull requests because samples can need secrets. Internal PRs run changed eligible samples; manual and monthly scheduled runs run all samples and are the only CI runs that enable trace collection. After a successful full run and snippet regeneration, CI updates or creates `chore/refresh-code-sample-traces` only if the manifest or generated snippets differ. A separate workflow opens a Linear issue only for a failed or cancelled scheduled run.

## Safe change checklist

1. Edit the runnable file under `src/code-samples/`; do not edit snippet MDX as the primary change.
2. Use complete, language-correct markers and unique language-suffixed IDs. Multiple Python snippets may share one harness when they represent one topic.
3. Place a trailing remove-block harness that actually executes or asserts the visible behavior; do not short-circuit the sample.
4. For the MCP error/metadata file, retain both markers and its shared calculator harness unless the desired change is specifically to split it for trace eligibility.
5. Run the focused sample command, `make code-snippets`, and review both the updated error MDX and newly generated metadata MDX. Use a full regeneration before depending on complete repository output.
6. Run `tests/unit_tests/test_generate_code_snippet_mdx.py` when changing renderer or model-CodeGroup behavior.
7. Treat trace refresh as public publication, not as routine local validation.

## Related pages

- [GitHub Actions and CI/CD](/openwiki/integrations/github-actions.md)
- [Adding and Maintaining Documentation Pages](/openwiki/operations/adding-pages.md)
- [Documentation CLI Tools](/openwiki/operations/cli-tools.md)
- [Quickstart](/openwiki/quickstart.md)
- [Testing Overview](/openwiki/testing/test-overview.md)
