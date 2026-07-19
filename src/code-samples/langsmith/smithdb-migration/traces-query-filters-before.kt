
///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.2.0
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.12

// :snippet-start: traces-query-filters-before-kt
// :codegroup-tab: Before
import com.langchain.smith.client.LangsmithClient
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient
import com.langchain.smith.models.runs.RunQueryParams
import com.langchain.smith.models.sessions.SessionListParams

// :remove-start:
fun main() {
    if (System.getenv("LANGSMITH_API_KEY").isNullOrBlank()) {
        println("[smithdb-traces-query-filters-before] Skipping (LANGSMITH_API_KEY is not set).")
        return
    }
// :remove-end:
val client: LangsmithClient = LangsmithOkHttpClient.fromEnv()

val project = client.sessions().list(
    SessionListParams.builder().name("default").limit(1L).build()
).items().first()

// v1 has no root-run-only filter concept — isRoot plus a regular filter is
// the closest equivalent, still scanning every run to match.
val runs = client.runs().query(
    RunQueryParams.builder()
        .addSession(project.id())
        .isRoot(true)
        .filter("eq(status, \"error\")")
        .limit(5L)
        .build()
).runs()
for (run in runs) {
    println(run.traceId())
}
// :remove-start:
}
// :remove-end:
// :snippet-end:
