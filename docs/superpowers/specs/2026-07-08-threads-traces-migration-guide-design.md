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

**Schema audit (2026-07-08):** every field list in this plan was independently re-verified against each SDK repo's GitHub HEAD — `langsmith-sdk` (Python/TS, self-verified byte-for-byte against local clone, zero drift), `langsmith-go`, and `langsmith-java` (both via dedicated subagents using `gh api .../contents/<path>`, no local clone read). `langchainplus`/`langchainplus-2` was excluded from this pass per instruction. Headline result: **all 4 languages' v2 request/response schemas are field-for-field identical** (same Stainless generation, same OpenAPI spec, only naming convention differs: `snake_case` wire/Python/TS, `camelCase` Go/Java getters, `PascalCase` Go struct fields). Exact confirmed field counts:

| Method | Request fields | Response fields |
|---|---|---|
| `threads.query` | 6 (`cursor`, `filter`, `max_start_time`, `min_start_time`, `page_size`, `project_id`) | `ThreadListItem`: 19 |
| `threads.list_traces` | 5 + 21-value select enum | `ThreadTraceListItem`: 21 |
| `threads.stats` | 2 (`session_id`, `selects`) + 17-value select enum | `ThreadStatsResponse`: 17 |
| `traces.query` | 9 + 44-value select enum | `Trace` (2 fields) + `TraceAggregates` (3 fields) |
| `traces.list_runs` | 6 (incl. `accept`→header) + same 44-value enum | `TraceListRunsResponse`: 1 field (`items: Run[]`) |

Old (v1) equivalents, also now exact: the generic run-query params (`RunQueryParams`/`RunQueryV1Params`, byte-identical to each other in both Go and Java) have **24 fields**; the generic run-stats params (`RunStatsQueryParams`) have **23 fields**, more than the "~15" this plan originally estimated — the extra ones (`group_by`, `groups`, `include_details`, `data_source_type`, `execution_order`, `search_filter`, `skip_pagination`, `use_experimental_search`) exist but are irrelevant to scoping stats to one thread. The v1 stats response (`RunStats`/`RunStatsResponseRunStats`) has **28 fields**, independently confirmed identical between Go and Java — this corroborates the original `smith-backend/app/schemas.py` finding from a second, SDK-only source, so that citation is no longer load-bearing (kept below for the original context, but the Go/Java structs are now the primary source).

**Resolved (2026-07-08):** re-read the Go `RunSchema` struct directly from GitHub HEAD (`run.go:696,722,734`) — `CompletionCost`/`PromptCost`/`TotalCost` are genuinely `float64` (`json:"total_cost" api:"nullable"`), not a subagent-summary error. So this is a real, if minor, cross-language codegen inconsistency (same OpenAPI field, Go decodes it as a float, Java's stricter codegen keeps it a `String`) — not a documentation bug. The existing `Runs: query` Go tab's "Unchanged" note for `run.TotalCost` is correct as shipped; the Java tab's `String`→`Double` note is also correct. No change needed to either table.

**Implementation fact (Python async):** `Client.threads`/`Client.traces` (`python/langsmith/client.py:1491,1497`) return `AsyncThreadsResource`/`AsyncTracesResource` — async-only, even on the synchronous `Client`. Every Python "After" example must wrap in `async def main(): ... asyncio.run(main())`, use `await client.aread_project(...)` to resolve the project, `async for` to consume paginated calls (`query`, `list_traces`), and `await` eager calls (`stats`, `list_runs`) — matching the existing `runs-retrieve-by-id-after.py`/`runs-query-fetch-by-id-after.py` convention exactly. "Before" (v1) examples stay plain sync, since `list_threads`/`read_thread`/`get_run_stats`/`list_runs` are genuinely sync-only methods. **Decision: no `<Note>` callout about this quirk in the rendered guide** — user declined; just get every example's async/await right.

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
- `project_id` XOR `project_name` (v1) → `project_id` only (v2); resolve name via `aread_project` first, same pattern as `Runs: query`.
- `start_time` (single-sided, defaults to 1 day ago) → `min_start_time`/`max_start_time` (v2 has **no default** — must pass explicitly, opposite direction from the `Runs: query` warning about the 24h default).
- `offset`+`limit` (v1 offset pagination) → `cursor`+`page_size` (v2 cursor pagination).
- `filter` (v1, evaluated against runs) → `filter` (v2, evaluated against each thread's root run) — same syntax, different evaluation target worth calling out.

**Query parameters — Go/Java tabs:** no query params to map (there was no dedicated method); describe the old approach narratively (`RunService.Query` with `is_root=true`, manual grouping by `thread_id` metadata client-side) same as the Traces sections below.

**Response fields — the interesting part:**
- Python's v1 `ListThreadsItem`: only `thread_id`, `runs` (full embedded `Run[]`), `count`, `min_start_time`, `max_start_time`. No token/cost/latency/feedback fields at all.
- TS's v1 `ListThreadsItem`: *claims* `total_tokens`, `total_cost`, `latency_p50`, `latency_p99`, `feedback_stats` — but the implementation hardcodes them to `0`/`null`, never computes them (`js/src/client.ts:3308-3314`). **Call this out as a real v1 bug being fixed**, not a rename — v2 actually computes these.
- v2's `ThreadListItem` never embeds the full run list (that's what `threads.list_traces` is for) but adds real `feedback_stats`, `latency_p50`/`latency_p99`, cost/token sums with per-category `_details`, `first_trace_id`/`last_trace_id`, `first_inputs`/`last_outputs` previews, `last_error`, `num_errored_turns`.

**Examples:** 2 examples — "List threads in a project" (Before: `list_threads`/`listThreads`, generic grouping for Go/Java; After: `threads.query`), plus a second showing `filter` narrowing threads by a root-run attribute (e.g. `eq(status, "error")`).

### Threads: list traces

**Method name:** Python `client.read_thread()` / TS `client.readThread()` → `client.threads.list_traces()` / `client.threads.listTraces()`. Go/Java: generic `list_runs`-with-`thread_id`-filter fallback → `Threads.ListTraces()` / `threads().listTraces()`.

**Query parameters:** `read_thread`'s `is_root` (default `True`, can be set `False` to get descendant runs too) has no v2 equivalent — `list_traces` always returns traces (root runs) only, matching its name. **Confirmed via the schema audit**: `read_thread`'s `order` (asc/desc) has no v2 equivalent either — `ThreadListTracesParams` has exactly 5 fields (`project_id`, `cursor`, `filter`, `page_size`, `selects`) across Python/Go/Java, no sort/order field at all — mark as `(not available)`, no longer an open item. `select` (v1 arbitrary run field list) → `selects` (v2 `ThreadTraceSelectField`, 21-value uppercase enum, confirmed identical across all 4 languages).

**Response fields:** v1 returns full `Run` objects (iterator); v2 returns lightweight `ThreadTraceListItem` — preview fields instead of full `inputs`/`outputs`, no embedded child runs. Reuse the same "Response fields" framing pattern as `Runs: query`'s Python tab (`selects` controls what's populated).

**Examples:** 2 examples — "List a thread's traces," plus a second showing `selects` picking specific fields (e.g. token/cost totals) instead of the `trace_id`-only default.

### Threads: stats

**Method name:** the generic stats endpoint exists in all 4 languages (confirmed: Go `RunService.Stats`, Java `RunService.stats`, alongside Python `client.get_run_stats()` / TS `client.getRunStats()`) → `client.threads.stats()` / `Threads.Stats()` / `threads().stats()`. So, like `traces.query`/`traces.list_runs`, all 4 language tabs get a real (if generic) Before method — no `(not available)` needed anywhere in this table after all.

**Query parameters:** v1's `RunStatsQueryParams` has **23 generic filter/grouping params** (confirmed via Go/Java schema audit — larger than this plan's original "~15" estimate): `id`, `trace`, `parent_run`, `run_type`, `session`/`project_ids`, `reference_example`, `start_time`, `end_time`, `error`, `query`, `filter`, `trace_filter`, `tree_filter`, `is_root`, `data_source_type`, `execution_order`, `search_filter`, `select`, `skip_pagination`, `use_experimental_search`, plus 3 grouping-only params with no relevance here (`group_by`, `groups`, `include_details`) and a Go-only `skip_prev_cursor`. Only `filter`+`is_root`+`session`/`project_ids` are actually used to scope to one thread. v2 takes `thread_id` (path) + `session_id` + `selects` (required, at least one value, confirmed identical 17-value enum across all 4 languages). Frame the mapping narratively rather than a full 23-row table, since only 3 of those v1 params matter for this use case.

**Response fields — confirmed via `smith-backend/app/schemas.py:760` `RunStats`, independently corroborated by Go's `RunStatsResponseRunStats` and Java's `RunStats` (identical 28-field set in both, verified against GitHub HEAD, no `langchainplus` dependency):**

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

Note for implementation: v1's stats response is actually a union of two shapes (a flat `RunStats` and a grouped-by-key map variant, used when `group_by`/`groups` params are set). Only the flat variant is relevant here, since scoping to a single thread never uses grouping — no need to document the grouped variant in this section.

**Examples:** 2 examples — "Compute stats for a thread" (with a `<Warning>` about `threads.stats` aggregates being eventually consistent, per the `langsmith-sdk` PR #3164 description), plus a second contrasting the old two-call `get_run_stats`-plus-`first_start_time`-lookup workaround against the single new call, leaning on the field-mapping table above.

### Traces: query

**Method name:** `client.list_runs(is_root=True)` (generic, all 4 languages) → `client.traces.query()`.

**Query parameters:** real mapping exists here too (this isn't "no predecessor," it's "no dedicated wrapper") — `session`/`project_id(s)` unchanged in spirit, `filter` → `trace_filter` (now explicitly scoped to root runs only), new: `tree_filter`, `trace_ids` fast-path, `selects` routing to `trace_aggregates` vs `root_run` (confirmed: v2's request has exactly 9 fields, `selects` uses a 44-value enum, identical across all 4 languages). `min_start_time` defaults to 24h ago (a real behavior change from v1's no-default full scan — same warning pattern as `Runs: query`).

**Response fields:** `root_run` (same shape as `Runs: query`'s response fields table — reuse/reference it) + new `trace_aggregates` (`total_tokens`, `total_cost`, `first_token_time` summed across the *whole* trace, not just the root run — the reason this method exists).

**Examples:** 2 examples — "List traces with trace-wide totals" (Before: root run query + N+1 per-trace sum; After: `traces.query` with `trace_aggregates`), plus a second showing `trace_filter`/`trace_ids` narrowing (root-run-only filter vs the fast-path UUID list).

### Traces: list runs

**Method name:** `client.list_runs(trace_id=...)` (generic) → `client.traces.list_runs()`.

**Query parameters:** closest thing to a "boring" migration in this set — `trace_id` unchanged (now path param), `project_id` newly required (SmithDB partition key), `min_start_time`/`max_start_time` newly required together (also partition-routing), `filter`/`selects` same shape as `Runs: query` (confirmed: v2 request has 6 fields including `accept`→header, `selects` uses the same 44-value enum as `traces.query`).

**Response fields:** `{items: [...]}` list of `Run` — same shape as `Runs: query`'s response fields table.

**Examples:** 2 examples — "List a trace's runs," plus a second showing `filter` narrowing to a run subset within the trace (e.g. `eq(run_type, "llm")`).

## New example in `Runs: query`

Append two new examples to the existing `### Examples` list in `runs-query.mdx` (currently 9 examples), after the last one:

**Example 1 — `#### List root runs as traces`:** the plain mechanical swap, no aggregation involved — Before: `client.list_runs(is_root=True)`; After: `client.traces.query(...)`. The on-ramp: "if you're listing root runs to represent traces, this is the dedicated method for it."

**Example 2 — `#### Get trace-wide totals without extra queries`:** the actual payoff — Before: the `is_root=True` root-run query plus a per-trace N+1 `list_runs(trace_id=...)` query to sum descendant tokens/cost (already drafted in the reverted prototype — reusable as-is); After: one `client.traces.query(...)` call with `trace_aggregates` already computed. Both examples deliberately switch resource from `runs` to `traces` in the After tab — not a `runs.query` variant, since that's the whole point.

**Discoverability hook:** immediately after the code tabs, a `<Tip>` callout: *"See [Traces: query](#traces-query) and [Traces: list runs](#traces-list-runs) below for the full set of trace-oriented methods."* — plain kebab-case slugs (lowercase, spaces to hyphens, punctuation stripped) match the anchor convention already used elsewhere in this docs repo, e.g. `administration-overview.mdx`'s `## Personal Access Tokens (PATs)` → `#personal-access-tokens-pats` and `add-auth-server.mdx`'s `[above](#setup-auth-provider)`. So `#traces-query`/`#traces-list-runs` should be correct for headings `## Traces: query`/`## Traces: list runs`. **User will verify empirically against the local docs preview once these headings actually exist in the file** — reminder for implementation: confirm the live anchors before finalizing this callout, don't just trust the convention.

## File/pipeline changes (mechanical, same pattern as the reverted prototype)

- Raw code samples under `docs/src/code-samples/langsmith/smithdb-migration/`: Python combined before/after via `:snippet-start:`/`:snippet-end:` markers, TS/Go/Java/cURL as separate before/after files — now including Go and Java, which the reverted prototype didn't have.
- `make code-snippets` compiles them into `docs/src/snippets/code-samples/smithdb-migration/*.mdx`.
- 5 new resource snippets under `docs/src/snippets/langsmith/smithdb-migration/` (`threads-query.mdx`, `threads-list-traces.mdx`, `threads-stats.mdx`, `traces-query.mdx`, `traces-list-runs.mdx`), imported into `docs/src/langsmith/smithdb-sdk-migration.mdx` after `Runs: retrieve`.
- One new example block added directly into the existing `runs-query.mdx`, plus its 2 new code-sample files (5 languages × before/after, or 4 + combined Python = 9 files, matching the existing per-example file count in that section).

## Example testing

**All new examples must pass the docs repo's existing snippet-testing framework — same rigor as every existing example, no exceptions.**

`make test-code-samples` (`scripts/test_code_samples.py`) executes every raw file under `src/code-samples/` directly against a real LangSmith backend: Python via `uv run python`, TypeScript via `npx tsx`, Go via `go run`, Java/Kotlin via `jbang`, bash via `bash`. This means every code sample — both Before and After — must be a genuinely runnable program, not illustrative pseudo-code. `FILES="..."` scopes a run to specific files.

This has a concrete consequence for placeholder IDs (`<thread-id>`, `<trace-id>`, etc.), verified by reading two existing examples end-to-end (`runs-query-fetch-by-id` and `runs-retrieve-by-id`) at GitHub HEAD:

- **Lazy/paginated methods** (`threads.query`, `threads.list_traces`, `traces.query` — all return a paginator/generator that makes no HTTP request until iterated): a placeholder ID is safe to leave in the rendered snippet, *as long as the visible code never iterates the result*. This is exactly what `runs-query-fetch-by-id-before.py` already does — `client.list_runs(id=["<run-id-1>", "<run-id-2>"])` is called but never consumed, so the generator body never runs and no real request is sent.
- **Eager/point-lookup methods** (`threads.stats`, `traces.list_runs` — both return a plain response object immediately, no laziness) do issue a real HTTP request the moment they're called. A literal placeholder ID would make that request fail in CI. The existing `runs-retrieve-by-id` example (itself an eager point-lookup, `client.runs.retrieve(run_id, ...)`) solves this with `:remove-start:`/`:remove-end:` marker blocks: the *rendered* snippet shows a clean `run_id = "<run-id>"` placeholder, but the *executed* file has a hidden block immediately after it that resolves a real ID (query the "default" project, then query for a real run, take its ID) and overwrites the placeholder before the real call runs. This pattern is already implemented across all 5 languages: `runs-retrieve-by-id-after.py`/`.ts`/`.go`/`.sh` (and presumably `.kt` — not fetched, but the `:remove-start:`/`:remove-end:` marker syntax is documented in `scripts/extract_code_snippets.py` as supported for Kotlin too).

**Applying this to the new sections:**
- `Threads: query`, `Threads: list traces`, `Traces: query` examples can use placeholder IDs directly, following the `runs-query-fetch-by-id` pattern — construct, don't consume, where a placeholder is involved.
- `Threads: stats` and `Traces: list runs` examples need a hidden resolution block per language, mirroring `runs-retrieve-by-id` exactly: resolve the "default" project, then issue one real (paginated, actually-iterated-in-the-hidden-block) call to `threads.query`/`traces.query` to get one real `thread_id`/`trace_id`, then substitute it in before the real `stats`/`list_runs` call. This adds a small bootstrap block to those two sections' examples that isn't shown to the reader — expected overhead, not a shortcut to avoid.
- The new `Runs: query` cross-reference example (trace reconstruction) should follow whichever pattern matches its own Before/After calls — the Before (`is_root=True` root-run query, consumed) and After (`traces.query`, consumed to demonstrate `trace_aggregates`) both need real, iterated results to be a meaningful example, so this one needs live data to exist in the test project, same requirement as every other consumed-and-printed example already in the file (e.g. `runs-query-list-all`).

**Commands to run during implementation** (not yet run — this plan doesn't touch code): `make test-code-samples FILES="<new files>"` scoped to just the new/changed files first, then a full `make test-code-samples` pass before considering the work done, matching how this repo already gates content.

**Resolved:** user will provide a `LANGSMITH_API_KEY` pointed at a live backend with real threads/traces/runs data under a "default" project — no longer a blocking dependency.

## Validation

- `make check-cross-refs` (catches broken imports/links — already caught one bad link in the reverted prototype).
- `markdownlint` on changed/new files.
- Manual read-through per section against the fact tables above before considering it done — every field list in this plan is now source-confirmed against GitHub HEAD (SDK repos only).
- **All examples must be tested through the docs repo's existing snippet-testing framework** — see the "Example testing" section above.

## Open items (all resolved 2026-07-08, kept for the record)

1. ~~Go `run.TotalCost` typing~~ — resolved: confirmed `float64` directly from `run.go:696,722,734` at GitHub HEAD; the existing Go tab's "Unchanged" note is correct, no change needed.
2. ~~Mintlify anchor-slug behavior~~ — convention identified (plain kebab-case, matching other pages in this repo); user will do the final empirical check against the local preview once the new headings exist. **Reminder for implementation: don't skip this check.**
3. ~~Example count per new section~~ — resolved: 2 examples each (see per-section plans above).
4. ~~Test credentials~~ — resolved: user will provide `LANGSMITH_API_KEY` for a backend with real thread/trace/run data.
