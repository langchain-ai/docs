///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.2.0
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.18

// :snippet-start: feedback-create-after-kt
// :codegroup-tab: After
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
        println("[smithdb-feedback-create-after] Skipping (LANGSMITH_API_KEY is not set).")
        return
    }

// :remove-end:
val client: LangsmithClient = LangsmithOkHttpClient.fromEnv()

var runId = "<run-id>"
var sessionId = "<session-id>"
// :remove-start:
val project = client.sessions()
    .list(SessionListParams.builder().name("default").limit(1L).build())
    .items().first()
sessionId = project.id()
runId = client.runs()
    .query(RunQueryParams.builder().addSession(project.id()).limit(1L).build())
    .items().first().id()
// :remove-end:
client.feedback().create(
    FeedbackCreateSchema.builder()
        .runId(runId)
        .key("user_feedback")
        .score(1.0)
        .sessionId(sessionId)
        .build()
)
// :remove-start:
}
// :remove-end:
// :snippet-end:
