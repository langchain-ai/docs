///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.2.0
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.14

// :snippet-start: runs-add-to-queue-before-kt
// :codegroup-tab: Before
import com.langchain.smith.client.LangsmithClient
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient
import com.langchain.smith.models.annotationqueues.AnnotationQueueAnnotationQueuesParams
import com.langchain.smith.models.annotationqueues.runs.RunCreateParams
import com.langchain.smith.models.runs.RunQueryV2Params
import com.langchain.smith.models.sessions.SessionListParams

// :remove-start:
fun main() {
    if (System.getenv("LANGSMITH_API_KEY").isNullOrBlank()) {
        println("[smithdb-runs-add-to-queue-before] Skipping (LANGSMITH_API_KEY is not set).")
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
    AnnotationQueueAnnotationQueuesParams.builder().name("docs-smithdb-migration").build()
).id()
// :remove-end:
val runs = client.runs().queryV2(
    RunQueryV2Params.builder()
        .addProjectId(projectId)
        .addSelect(RunQueryV2Params.Select.ID)
        .pageSize(5L)
        .build()
).items()

client.annotationQueues().runs().create(
    RunCreateParams.builder()
        .queueId(queueId)
        .bodyOfRunsUuidArray(runs.map { it.id().get() })
        .build()
)
// :remove-start:
}
// :remove-end:
// :snippet-end:
