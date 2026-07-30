
///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.2.0
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.18

// :snippet-start: traces-list-runs-basic-before-kt
// :codegroup-tab: Before
import com.langchain.smith.client.LangsmithClient
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient
import com.langchain.smith.models.runs.RunQueryParams
import com.langchain.smith.models.sessions.SessionListParams

// :remove-start:
fun main() {
    if (System.getenv("LANGSMITH_API_KEY").isNullOrBlank()) {
        println("[smithdb-traces-list-runs-basic-before] Skipping (LANGSMITH_API_KEY is not set).")
        return
    }
// :remove-end:
val client: LangsmithClient = LangsmithOkHttpClient.fromEnv()

val project = client.sessions().list(
    SessionListParams.builder().name("default").limit(1L).build()
).items().first()

var traceId = "<trace-id>"
// :remove-start:
traceId = client.runs().query(
    RunQueryParams.builder().addSession(project.id()).isRoot(true).limit(1L).build()
).runs().first().traceId()
// :remove-end:

val runs = client.runs().query(
    RunQueryParams.builder()
        .addSession(project.id())
        .trace(traceId)
        .build()
).runs()
for (run in runs) {
    println("${run.name()} ${run.runType()} ${run.status()}")
}
// :remove-start:
}
// :remove-end:
// :snippet-end:
