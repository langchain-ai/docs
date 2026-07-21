///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.2.0
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.18

// :snippet-start: runs-query-boolean-filters-before-kt
// :codegroup-tab: Before
import com.langchain.smith.client.LangsmithClient
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient
import com.langchain.smith.models.runs.RunQueryParams
import com.langchain.smith.models.sessions.SessionListParams

// :remove-start:
fun main() {
    if (System.getenv("LANGSMITH_API_KEY").isNullOrBlank()) {
        println("[smithdb-runs-query-boolean-filters-before] Skipping (LANGSMITH_API_KEY is not set).")
        return
    }

// :remove-end:
val client: LangsmithClient = LangsmithOkHttpClient.fromEnv()

val project = client.sessions().list(
    SessionListParams.builder().name("default").limit(1L).build()
).items().first()
val filterStr = "and(gt(start_time, \"2023-07-15T12:34:56Z\")," +
    " or(neq(status, \"error\")," +
    "    and(eq(feedback_key, \"Correctness\"), eq(feedback_score, 0.0))))"
val runs = client.runs().query(
    RunQueryParams.builder().addSession(project.id()).filter(filterStr).build()
).items()
// :remove-start:
}
// :remove-end:
// :snippet-end:
