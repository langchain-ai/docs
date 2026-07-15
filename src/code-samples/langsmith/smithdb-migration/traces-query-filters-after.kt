
///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.2.0
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.12

// :snippet-start: traces-query-filters-after-kt
// :codegroup-tab: After
import java.time.OffsetDateTime

import com.langchain.smith.client.LangsmithClient
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient
import com.langchain.smith.models.sessions.SessionListParams
import com.langchain.smith.models.traces.TraceQueryParams

// :remove-start:
fun main() {
    if (System.getenv("LANGSMITH_API_KEY").isNullOrBlank()) {
        println("[smithdb-traces-query-filters-after] Skipping (LANGSMITH_API_KEY is not set).")
        return
    }
// :remove-end:
val client: LangsmithClient = LangsmithOkHttpClient.fromEnv()

val project = client.sessions().list(
    SessionListParams.builder().name("default").limit(1L).build()
).items().first()

val minStart = OffsetDateTime.parse("2026-07-01T00:00:00Z")
val maxStart = OffsetDateTime.parse("2026-07-31T23:59:59Z")

// trace_filter is implicitly root-run-only — no is_root needed.
val errorTraces = client.traces().query(
    TraceQueryParams.builder()
        .projectId(project.id())
        .minStartTime(minStart)
        .maxStartTime(maxStart)
        .traceFilter("eq(status, \"error\")")
        .build()
).items().take(5)
for (trace in errorTraces) {
    println(trace.rootRun().get().traceId().get())
}

// traceIds is a fast-path when you already know which traces you want.
var traceId = "<trace-id>"
// :remove-start:
traceId = client.traces().query(
    TraceQueryParams.builder()
        .projectId(project.id())
        .minStartTime(minStart)
        .maxStartTime(maxStart)
        .build()
).items().first().rootRun().get().traceId().get()
// :remove-end:
val knownTraces = client.traces().query(
    TraceQueryParams.builder()
        .projectId(project.id())
        .minStartTime(minStart)
        .maxStartTime(maxStart)
        .traceIds(listOf(traceId))
        .build()
).items()
for (trace in knownTraces) {
    println(trace.rootRun().get().traceId().get())
}
// :remove-start:
}
// :remove-end:
// :snippet-end:
