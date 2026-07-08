# Design: Document Threads/Traces SDK methods in the SmithDB migration guide

## Context

LSDK-301 added 5 new v2 SDK methods across Python, TypeScript, Go, and Java:

| Method | Endpoint |
|---|---|
| `threads.query` | `POST /v2/threads/query` |
| `threads.list_traces` | `GET /v2/threads/{thread_id}/traces` |
| `threads.stats` | `GET /v2/threads/{thread_id}/stats` |
| `traces.query` | `POST /v2/traces/query` |
| `traces.list_runs` | `GET /v2/traces/{trace_id}/runs` |

All 4 SDKs have shipped them: Python `v0.10.0`, TypeScript `0.8.0`, Go `v0.18.0`, Java `v0.1.0-beta.12` (confirmed against GitHub, recorded in the [SDK Migration Tracker](https://app.notion.com/p/38e808527b17806c877bc543721cf833)).

This is LSDK-305: add them to `docs/src/langsmith/smithdb-sdk-migration.mdx`, following the existing pattern set by the `Runs: query` / `Runs: retrieve` sections in that same guide.

**Corrected framing (superseding an earlier draft of this plan):** these are not "brand new capabilities with no v1 equivalent." The Notion tracker's `SDKP old`/`SDKT old` columns, cross-checked against actual source, show real predecessors for 3 of the 5 methods:

| New method | Old method (Python / TS) | Old method (Go / Java) |
|---|---|---|
| `threads.query` | `client.list_threads()` / `client.listThreads()` | none — fall back to generic `list_runs`-based grouping |
| `threads.list_traces` | `client.read_thread()` / `client.readThread()` | none — same fallback |
| `threads.stats` | `client.get_run_stats()` / `client.getRunStats()` | none — same fallback |
| `traces.query` | `client.list_runs(is_root=True)` (generic, no dedicated wrapper) | same, generic |
| `traces.list_runs` | `client.list_runs(trace_id=...)` (generic, no dedicated wrapper) | same, generic |

Go and Java never had hand-rolled thread/stats convenience methods (confirmed: no `ListThreads`/`GetRunStats`/`ReadThread` or camelCase equivalents anywhere in either repo) — only Python and TypeScript did. So for the first 3 methods, Python/TS tabs get a real method-to-method migration table; Go/Java tabs fall back to the same generic-`list_runs`-plus-manual-reconstruction story that all 4 languages share for the last 2 methods.

## Goals

1. Five new sections in the migration guide, one per method, each following the **exact existing structure** used by `Runs: query`/`Runs: retrieve`: `## <Resource>: <method>` → `### Main changes` (`#### Method name`, `#### Query parameters`, `#### Response fields`, each a per-language `<Tabs>` block with Before/After tables) → `### Examples` (Before/After code tabs).
2. A new example inside the *existing* `Runs: query` section's `### Examples` list, demonstrating the `list_runs`-based trace-reconstruction workaround being replaced by `traces.query`/`traces.list_runs`, with a pointer to the new sections. Rationale (user's): customers currently using `list_runs` to approximate trace queries will naturally land on `Runs: query` first — this example is where they'll discover the dedicated methods exist.
3. All 5 new sections cover all 5 tabs (Python, TypeScript, Go, Java, cURL) — a step up from an earlier draft that only covered Python/TS/cURL, now that Go/Java are confirmed shipped.

## Non-goals

- No changes to `Runs: retrieve` or any other existing section beyond the one new example in `Runs: query`.
- Not attempting to fix or flag the v1 API's own bugs beyond documenting them accurately (e.g. TS `listThreads`'s hardcoded-zero aggregates) — that's a v1 SDK bug, not something this guide should try to work around.

## Section-by-section content plan

### Threads: query

**Method name**

| Before | After |
|---|---|
| Python: `client.list_threads()` | `client.threads.query()` |
| TypeScript: `client.listThreads()` | `client.threads.query()` |
| Go: *(no dedicated method — generic `RunService.Query` + manual grouping)* | `client.Threads.Query()` |
| Java: *(no dedicated method — generic `RunService.query()` + manual grouping)* | `client.threads().query()` |
| cURL: `POST /api/v1/runs/query` (`is_root=true`, manual grouping) | `POST /v2/threads/query` |

**Query parameters — key differences (Python/TS tabs, real mapping):**
- `project_id` XOR `project_name` (v1) → `project_id` only (v2); resolve name via `read_project` first, same pattern as `Runs: query`.
- `start_time` (single-sided, defaults to 1 day ago) → `min_start_time`/`max_start_time` (v2 has **no default** — must pass explicitly, opposite direction from the `Runs: query` warning about the 24h default).
- `offset`+`limit` (v1 offset pagination) → `cursor`+`page_size` (v2 cursor pagination).
- `filter` (v1, evaluated against runs) → `filter` (v2, evaluated against each thread's root run) — same syntax, different evaluation target worth calling out.

**Query parameters — Go/Java tabs:** no query params to map (there was no dedicated method); describe the old approach narratively (`RunService.Query` with `is_root=true`, manual grouping by `thread_id` metadata client-side) same as the Traces sections below.

**Response fields — the interesting part:**
- Python's v1 `ListThreadsItem`: only `thread_id`, `runs` (full embedded `Run[]`), `count`, `min_start_time`, `max_start_time`. No token/cost/latency/feedback fields at all.
- TS's v1 `ListThreadsItem`: *claims* `total_tokens`, `total_cost`, `latency_p50`, `latency_p99`, `feedback_stats` — but the implementation hardcodes them to `0`/`null`, never computes them (`js/src/client.ts:3308-3314`). **Call this out as a real v1 bug being fixed**, not a rename — v2 actually computes these.
- v2's `ThreadListItem` never embeds the full run list (that's what `threads.list_traces` is for) but adds real `feedback_stats`, `latency_p50`/`latency_p99`, cost/token sums with per-category `_details`, `first_trace_id`/`last_trace_id`, `first_inputs`/`last_outputs` previews, `last_error`, `num_errored_turns`.

**Examples:** 1 example — "List threads in a project" (Before: `list_threads`/`listThreads`, generic grouping for Go/Java; After: `threads.query`).

### Threads: list traces

**Method name:** Python `client.read_thread()` / TS `client.readThread()` → `client.threads.list_traces()` / `client.threads.listTraces()`. Go/Java: generic `list_runs`-with-`thread_id`-filter fallback → `Threads.ListTraces()` / `threads().listTraces()`.

**Query parameters:** `read_thread`'s `is_root` (default `True`, can be set `False` to get descendant runs too) has no v2 equivalent — `list_traces` always returns traces (root runs) only, matching its name. `order` (asc/desc) — check whether v2 has an equivalent; if not, note as `(not available)`. `select` (v1 arbitrary run field list) → `selects` (v2 `ThreadTraceSelectField` enum, uppercase).

**Response fields:** v1 returns full `Run` objects (iterator); v2 returns lightweight `ThreadTraceListItem` — preview fields instead of full `inputs`/`outputs`, no embedded child runs. Reuse the same "Response fields" framing pattern as `Runs: query`'s Python tab (`selects` controls what's populated).

**Examples:** 1 example — "List a thread's traces."

### Threads: stats

**Method name:** the generic stats endpoint exists in all 4 languages (confirmed: Go `RunService.Stats`, Java `RunService.stats`, alongside Python `client.get_run_stats()` / TS `client.getRunStats()`) → `client.threads.stats()` / `Threads.Stats()` / `threads().stats()`. So, like `traces.query`/`traces.list_runs`, all 4 language tabs get a real (if generic) Before method — no `(not available)` needed anywhere in this table after all.

**Query parameters:** v1 takes ~15 generic filter params (`id`, `trace`, `parent_run`, `run_type`, `project_names`/`project_ids`, `reference_example_ids`, `start_time`, `end_time`, `error`, `query`, `filter`, `trace_filter`, `tree_filter`, `is_root`, `data_source_type`) — only `filter`+`is_root`+`project_ids` are actually used to scope to one thread. v2 takes `thread_id` (path) + `session_id` + `selects` (required, at least one value). Frame the mapping narratively rather than a full 15-row table, since only 3 of those params matter for this use case.

**Response fields — confirmed via `smith-backend/app/schemas.py:760` `RunStats`:**

| v1 `RunStats` field | v2 `ThreadStatsResponse` field | Notes |
|---|---|---|
| `run_count` | `turns` | Renamed |
| `latency_p50` | `latency_p50_seconds` | Renamed, unit made explicit |
| `latency_p99` | `latency_p99_seconds` | Renamed |
| `last_run_start_time` | `last_start_time` | Renamed |
| `prompt_tokens`, `completion_tokens`, `total_tokens` | same names | Unchanged |
| `prompt_cost`, `completion_cost`, `total_cost` | same names | Unchanged |
| `prompt_token_details`, `completion_token_details`, `prompt_cost_details`, `completion_cost_details` | same names | Unchanged |
| `feedback_stats` | same name | Unchanged |
| *(not available — needed a second `runs/query` call sorted ascending, limit 1)* | `first_start_time` | New: no longer needs a second API call |
| *(not available)* | `last_end_time` | New |
| `first_token_p50`/`first_token_p99`, `median_tokens`, `completion_tokens_p50`/`prompt_tokens_p50`/`tokens_p99`/`completion_tokens_p99`/`prompt_tokens_p99`, `run_facets`, `error_rate`, `streaming_rate`, `cost_p50`/`cost_p99` | *(removed — no v2 equivalent)* | v1-only |

This table doubles as the single best piece of evidence that `threads.stats` is a real improvement, not just a rename — worth leading the section's example with the "used to need two API calls for `first_start_time`" fact.

**Examples:** 1 example — "Compute stats for a thread," with a `<Warning>` about `threads.stats` aggregates being eventually consistent (per the `langsmith-sdk` PR #3164 description).

### Traces: query

**Method name:** `client.list_runs(is_root=True)` (generic, all 4 languages) → `client.traces.query()`.

**Query parameters:** real mapping exists here too (this isn't "no predecessor," it's "no dedicated wrapper") — `session`/`project_id(s)` unchanged in spirit, `filter` → `trace_filter` (now explicitly scoped to root runs only), new: `tree_filter`, `trace_ids` fast-path, `selects` routing to `trace_aggregates` vs `root_run`. `min_start_time` defaults to 24h ago (a real behavior change from v1's no-default full scan — same warning pattern as `Runs: query`).

**Response fields:** `root_run` (same shape as `Runs: query`'s response fields table — reuse/reference it) + new `trace_aggregates` (`total_tokens`, `total_cost`, `first_token_time` summed across the *whole* trace, not just the root run — the reason this method exists).

**Examples:** 1-2 examples — at minimum "List traces with trace-wide totals" (Before: root run query + N+1 per-trace sum; After: `traces.query` with `trace_aggregates`).

### Traces: list runs

**Method name:** `client.list_runs(trace_id=...)` (generic) → `client.traces.list_runs()`.

**Query parameters:** closest thing to a "boring" migration in this set — `trace_id` unchanged (now path param), `project_id` newly required (SmithDB partition key), `min_start_time`/`max_start_time` newly required together (also partition-routing), `filter`/`selects` same shape as `Runs: query`.

**Response fields:** `{items: [...]}` list of `Run` — same shape as `Runs: query`'s response fields table.

**Examples:** 1 example — "List a trace's runs."

## New example in `Runs: query`

Append one new example to the existing `### Examples` list in `runs-query.mdx` (currently 9 examples), after the last one:

**Heading:** `#### Reconstruct a trace instead of grouping by trace_id`

**Before:** the `is_root=True` root-run query + per-trace N+1 `list_runs(trace_id=...)` query workaround (already drafted in the reverted prototype — reusable as-is).

**After:** switches to `client.traces.query(...)` — a deliberate resource switch, not a `runs.query` variant, since that's the whole point.

**Discoverability hook:** immediately after the code tabs, a `<Tip>` callout: *"See [Traces: query](#traces-query) and [Traces: list runs](#traces-list-runs) below for the full set of trace-oriented methods."* — anchor links need verification against Mintlify's actual heading-slug rules before use (flagged as a risk in an earlier round of this same guide; confirm during implementation rather than guess).

## File/pipeline changes (mechanical, same pattern as the reverted prototype)

- Raw code samples under `docs/src/code-samples/langsmith/smithdb-migration/`: Python combined before/after via `:snippet-start:`/`:snippet-end:` markers, TS/Go/Java/cURL as separate before/after files — now including Go and Java, which the reverted prototype didn't have.
- `make code-snippets` compiles them into `docs/src/snippets/code-samples/smithdb-migration/*.mdx`.
- 5 new resource snippets under `docs/src/snippets/langsmith/smithdb-migration/` (`threads-query.mdx`, `threads-list-traces.mdx`, `threads-stats.mdx`, `traces-query.mdx`, `traces-list-runs.mdx`), imported into `docs/src/langsmith/smithdb-sdk-migration.mdx` after `Runs: retrieve`.
- One new example block added directly into the existing `runs-query.mdx`, plus its 2 new code-sample files (5 languages × before/after, or 4 + combined Python = 9 files, matching the existing per-example file count in that section).

## Validation

- `make check-cross-refs` (catches broken imports/links — already caught one bad link in the reverted prototype).
- `markdownlint` on changed/new files.
- Manual read-through per section against the fact tables above before considering it done — the `order` param on `list_traces` (open item below) is the one mapping not yet double-checked against source line-by-line the way everything else in this plan was.

## Open items to confirm during implementation (not blocking plan approval)

1. Whether `threads.list_traces` v2 has an `order` equivalent to v1 `read_thread`'s `order` param — not yet checked.
2. Mintlify anchor-slug behavior for the `<Tip>` cross-link in `Runs: query` — needs verification, not assumption, before shipping literal `#threads-query`-style anchors.
3. Final count of examples per new section (plan assumes 1-2 each; existing `Runs: query` has 9 — new sections don't need to match that density, but should not be thinner than `Runs: retrieve`'s 2).
