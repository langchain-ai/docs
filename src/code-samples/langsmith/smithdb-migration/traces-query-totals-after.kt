
///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.2.0
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.18

// :snippet-start: traces-query-totals-after-kt
// :codegroup-tab: After
import java.time.OffsetDateTime

import com.langchain.smith.client.LangsmithClient
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient
import com.langchain.smith.models.runs.RunSelectField
import com.langchain.smith.models.sessions.SessionListParams
import com.langchain.smith.models.traces.TraceQueryParams
import kotlin.jvm.optionals.getOrNull

// :remove-start:
fun main() {
    if (System.getenv("LANGSMITH_API_KEY").isNullOrBlank()) {
        println("[smithdb-traces-query-totals-after] Skipping (LANGSMITH_API_KEY is not set).")
        return
    }
// :remove-end:
val client: LangsmithClient = LangsmithOkHttpClient.fromEnv()

val project = client.sessions().list(
    SessionListParams.builder().name("default").limit(1L).build()
).items().first()

val traces = client.traces().query(
    TraceQueryParams.builder()
        .projectId(project.id())
        .minStartTime(OffsetDateTime.parse("2026-07-01T00:00:00Z"))
        .maxStartTime(OffsetDateTime.parse("2026-07-31T23:59:59Z"))
        .addSelect(RunSelectField.NAME)
        .addSelect(RunSelectField.TOTAL_TOKENS)
        .addSelect(RunSelectField.TOTAL_COST)
        .build()
).items()

var count = 0
for (trace in traces) {
    count++
    val aggregates = trace.traceAggregates().getOrNull()
    if (aggregates != null) {
        println("${trace.rootRun().get().name().getOrNull()} ${aggregates.totalTokens().getOrNull()} ${aggregates.totalCost().getOrNull()}")
    }
    if (count >= 5) break
}
// :remove-start:
}
// :remove-end:
// :snippet-end:
