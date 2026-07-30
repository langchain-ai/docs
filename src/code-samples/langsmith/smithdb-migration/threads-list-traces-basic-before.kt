
///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.2.0
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.18

// :snippet-start: threads-list-traces-basic-before-kt
// :codegroup-tab: Before
// :remove-start:
import java.time.OffsetDateTime
// :remove-end:

import com.langchain.smith.client.LangsmithClient
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient
import com.langchain.smith.models.runs.RunQueryParams
import com.langchain.smith.models.sessions.SessionListParams
// :remove-start:
import com.langchain.smith.models.threads.ThreadQueryParams
// :remove-end:

// :remove-start:
fun main() {
    if (System.getenv("LANGSMITH_API_KEY").isNullOrBlank()) {
        println("[smithdb-threads-list-traces-basic-before] Skipping (LANGSMITH_API_KEY is not set).")
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

val runs = client.runs().query(
    RunQueryParams.builder()
        .addSession(project.id())
        .isRoot(true)
        .filter("eq(thread_id, \"$threadId\")")
        .build()
).runs()
for (run in runs) {
    println("${run.id()} ${run.startTime().get()}")
    // :remove-start:
    break
    // :remove-end:
}
// :remove-start:
}
// :remove-end:
// :snippet-end:
