///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.2.0
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.18

// :snippet-start: feedback-create-before-kt
// :codegroup-tab: Before
import com.langchain.smith.client.LangsmithClient
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient
import com.langchain.smith.models.feedback.FeedbackCreateSchema
// :remove-start:
import com.langchain.smith.models.runs.RunQueryParams
import com.langchain.smith.models.sessions.SessionListParams
// :remove-end:

// :remove-start:
fun main() {
    if (System.getenv("LANGSMITH_API_KEY").isNullOrBlank()) {
        println("[smithdb-feedback-create-before] Skipping (LANGSMITH_API_KEY is not set).")
        return
    }

// :remove-end:
val client: LangsmithClient = LangsmithOkHttpClient.fromEnv()

var runId = "<run-id>"
// :remove-start:
val project = client.sessions()
    .list(SessionListParams.builder().name("default").limit(1L).build())
    .items().first()
runId = client.runs()
    .query(RunQueryParams.builder().addSession(project.id()).limit(1L).build())
    .items().first().id()
// :remove-end:
client.feedback().create(
    FeedbackCreateSchema.builder()
        .runId(runId)
        .key("user_feedback")
        .score(1.0)
        .build()
)
// :remove-start:
}
// :remove-end:
// :snippet-end:
