
///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.2.0
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.18

// :snippet-start: threads-stats-first-start-time-before-kt
// :codegroup-tab: Before
// :remove-start:
import java.time.OffsetDateTime
// :remove-end:

import com.langchain.smith.client.LangsmithClient
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient
import com.langchain.smith.models.runs.RunQueryParams
import com.langchain.smith.models.runs.RunStatsParams
import com.langchain.smith.models.runs.RunStatsQueryParams
import com.langchain.smith.models.sessions.SessionListParams
// :remove-start:
import com.langchain.smith.models.threads.ThreadQueryParams
// :remove-end:
import kotlin.jvm.optionals.getOrNull

// :remove-start:
fun main() {
    if (System.getenv("LANGSMITH_API_KEY").isNullOrBlank()) {
        println("[smithdb-threads-stats-first-start-time-before] Skipping (LANGSMITH_API_KEY is not set).")
        return
    }
// :remove-end:
val client: LangsmithClient = LangsmithOkHttpClient.fromEnv()

val project = client.sessions().list(
    SessionListParams.builder().name("default").limit(1L).build()
).items().first()

var threadId = "<thread-id>"
// :remove-start:
threadId = client.threads().query(
    ThreadQueryParams.builder()
        .projectId(project.id())
        .minStartTime(OffsetDateTime.parse("2026-07-01T00:00:00Z"))
        .maxStartTime(OffsetDateTime.parse("2026-07-31T23:59:59Z"))
        .build()
).items().first().threadId().get()
// :remove-end:
val threadFilter = "eq(thread_id, \"$threadId\")"

val statsResponse = client.runs().stats(
    RunStatsParams.builder()
        .runStatsQueryParams(
            RunStatsQueryParams.builder()
                .addSession(project.id())
                .filter(threadFilter)
                .isRoot(true)
                .build()
        )
        .build()
)
val runCount = statsResponse.runStats().get().runCount().getOrNull()

// RunStatsQueryParams has no "first_start_time" field — a second call,
// sorted ascending, is needed to find the thread's earliest run.
val firstRun = client.runs().query(
    RunQueryParams.builder()
        .addSession(project.id())
        .filter(threadFilter)
        .isRoot(true)
        .order(RunQueryParams.Order.ASC)
        .limit(1L)
        .build()
).runs().first()
println("$runCount ${firstRun.startTime().getOrNull()}")
// :remove-start:
}
// :remove-end:
// :snippet-end:
