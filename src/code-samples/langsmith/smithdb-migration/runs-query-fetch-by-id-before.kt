///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.2.0
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.18

// :snippet-start: runs-query-fetch-by-id-before-kt
// :codegroup-tab: Before
import com.langchain.smith.client.LangsmithClient
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient
import com.langchain.smith.models.runs.RunQueryParams
import com.langchain.smith.models.sessions.SessionListParams

// :remove-start:
fun main() {
    if (System.getenv("LANGSMITH_API_KEY").isNullOrBlank()) {
        println("[smithdb-runs-query-fetch-by-id-before] Skipping (LANGSMITH_API_KEY is not set).")
        return
    }

// :remove-end:
val client: LangsmithClient = LangsmithOkHttpClient.fromEnv()

val project = client.sessions().list(
    SessionListParams.builder().name("default").limit(1L).build()
).items().first()
var runId1 = "<run-id-1>"
var runId2 = "<run-id-2>"
// :remove-start:
val foundRuns = client.runs().query(
    RunQueryParams.builder().addSession(project.id()).limit(2L).build()
).items()
runId1 = foundRuns[0].id()
runId2 = foundRuns[1].id()
// :remove-end:
val runs = client.runs().query(
    RunQueryParams.builder()
        .addSession(project.id())
        .addId(runId1)
        .addId(runId2)
        .build()
).items()
// :remove-start:
}
// :remove-end:
// :snippet-end:
