///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.2.0
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.18

// :snippet-start: runs-retrieve-basic-before-kt
// :codegroup-tab: Before
import com.langchain.smith.client.LangsmithClient
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient
// :remove-start:
import com.langchain.smith.models.runs.RunQueryParams
import com.langchain.smith.models.sessions.SessionListParams
// :remove-end:

// :remove-start:
fun main() {
    if (System.getenv("LANGSMITH_API_KEY").isNullOrBlank()) {
        println("[smithdb-runs-retrieve-basic-before] Skipping (LANGSMITH_API_KEY is not set).")
        return
    }

// :remove-end:
val client: LangsmithClient = LangsmithOkHttpClient.fromEnv()

var runId = "<run-id>"
// :remove-start:
val project = client.sessions().list(
    SessionListParams.builder().name("default").limit(1L).build()
).items().first()
val foundRun = client.runs().query(
    RunQueryParams.builder().addSession(project.id()).limit(1L).build()
).items().first()
runId = foundRun.id()
// :remove-end:
val run = client.runs().retrieve(runId)
println("${run.name()} ${run.status()} ${run.totalTokens()}")
// :remove-start:
}
// :remove-end:
// :snippet-end:
