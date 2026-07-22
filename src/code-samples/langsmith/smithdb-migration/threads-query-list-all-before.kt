
///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.2.0
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.18

// :snippet-start: threads-query-list-all-before-kt
// :codegroup-tab: Before
import com.langchain.smith.client.LangsmithClient
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient
import com.langchain.smith.models.runs.RunQueryParams
import com.langchain.smith.models.sessions.SessionListParams

// :remove-start:
fun main() {
    if (System.getenv("LANGSMITH_API_KEY").isNullOrBlank()) {
        println("[smithdb-threads-query-list-all-before] Skipping (LANGSMITH_API_KEY is not set).")
        return
    }
// :remove-end:
val client: LangsmithClient = LangsmithOkHttpClient.fromEnv()

val project = client.sessions().list(
    SessionListParams.builder().name("default").limit(1L).build()
).items().first()

// v1 has no dedicated thread grouping — the generic run query returns raw
// root runs, with no built-in way to bucket them by thread.
val rootRuns = client.runs().query(
    RunQueryParams.builder()
        .addSession(project.id())
        .isRoot(true)
        .build()
).runs()
for (run in rootRuns) {
    println("${run.traceId()} ${run.id()}")
    // :remove-start:
    break
    // :remove-end:
}
// :remove-start:
}
// :remove-end:
// :snippet-end:
