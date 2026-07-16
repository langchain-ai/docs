
///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.2.0
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.12

// :snippet-start: traces-list-runs-basic-after-kt
// :codegroup-tab: After
import java.time.OffsetDateTime

import com.langchain.smith.client.LangsmithClient
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient
import com.langchain.smith.models.sessions.SessionListParams
import com.langchain.smith.models.traces.TraceListRunsParams
import com.langchain.smith.models.traces.TraceQueryParams
import kotlin.jvm.optionals.getOrNull

// :remove-start:
fun main() {
    if (System.getenv("LANGSMITH_API_KEY").isNullOrBlank()) {
        println("[smithdb-traces-list-runs-basic-after] Skipping (LANGSMITH_API_KEY is not set).")
        return
    }
// :remove-end:
val client: LangsmithClient = LangsmithOkHttpClient.fromEnv()

val project = client.sessions().list(
    SessionListParams.builder().name("default").limit(1L).build()
).items().first()

var traceId = "<trace-id>"
// :remove-start:
traceId = client.traces().query(
    TraceQueryParams.builder()
        .projectId(project.id())
        .minStartTime(OffsetDateTime.parse("2026-07-01T00:00:00Z"))
        .maxStartTime(OffsetDateTime.parse("2026-07-31T23:59:59Z"))
        .build()
).items().first().rootRun().get().traceId().get()
// :remove-end:

val response = client.traces().listRuns(
    traceId,
    TraceListRunsParams.builder()
        .projectId(project.id())
        .addSelect(TraceListRunsParams.Select.NAME)
        .addSelect(TraceListRunsParams.Select.RUN_TYPE)
        .addSelect(TraceListRunsParams.Select.STATUS)
        .build()
)
for (run in response.items().getOrNull() ?: emptyList()) {
    println("${run.name().getOrNull()} ${run.runType().getOrNull()} ${run.status().getOrNull()}")
}
// :remove-start:
}
// :remove-end:
// :snippet-end:
