///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.2.0
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.18

// :snippet-start: runs-add-to-queue-after-kt
// :codegroup-tab: After
import com.langchain.smith.client.LangsmithClient
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient
import com.langchain.smith.models.annotationqueues.AnnotationQueueAnnotationQueuesParams
import com.langchain.smith.models.annotationqueues.runs.RunCreateByKeyParams
import com.langchain.smith.models.runs.RunQueryParams
import com.langchain.smith.models.sessions.SessionListParams

// :remove-start:
fun main() {
    if (System.getenv("LANGSMITH_API_KEY").isNullOrBlank()) {
        println("[smithdb-runs-add-to-queue-after] Skipping (LANGSMITH_API_KEY is not set).")
        return
    }

// :remove-end:
val client: LangsmithClient = LangsmithOkHttpClient.fromEnv()

var queueId = "<queue-id>"
var projectId = "<project-id>"
// :remove-start:
projectId = client.sessions()
    .list(SessionListParams.builder().name("default").limit(1L).build())
    .items().first().id()
queueId = client.annotationQueues().annotationQueues(
    AnnotationQueueAnnotationQueuesParams.builder()
        .name("docs-smithdb-migration-" + java.util.UUID.randomUUID())
        .build()
).id()
// :remove-end:
val runs = client.runs().query(
    RunQueryParams.builder().session(listOf(projectId)).limit(5L).build()
).items()

val params = RunCreateByKeyParams.builder().queueId(queueId)
for (run in runs) {
    params.addBody(
        RunCreateByKeyParams.Body.builder()
            .runId(run.id())
            .sessionId(run.sessionId())
            .startTime(run.startTime().get())
            .build()
    )
}
client.annotationQueues().runs().createByKey(params.build())
// :remove-start:
}
// :remove-end:
// :snippet-end:
