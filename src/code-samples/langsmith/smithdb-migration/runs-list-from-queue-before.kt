///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.2.0
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.22

// :snippet-start: runs-list-from-queue-before-kt
// :codegroup-tab: Before
import com.langchain.smith.client.LangsmithClient
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient
import com.langchain.smith.models.annotationqueues.AnnotationQueueRetrieveRunParams
import com.langchain.smith.models.annotationqueues.AnnotationQueueRetrieveSizeParams
import com.langchain.smith.models.annotationqueues.runs.RunListParams
// :remove-start:
import com.langchain.smith.models.annotationqueues.AnnotationQueueAnnotationQueuesParams
import com.langchain.smith.models.annotationqueues.runs.RunCreateParams
import com.langchain.smith.models.runs.RunQueryV2Params
import com.langchain.smith.models.sessions.SessionListParams
import java.time.OffsetDateTime

fun main() {
    if (System.getenv("LANGSMITH_API_KEY").isNullOrBlank()) {
        println("[smithdb-runs-list-from-queue-before] Skipping (LANGSMITH_API_KEY is not set).")
        return
    }

// :remove-end:

val client: LangsmithClient = LangsmithOkHttpClient.fromEnv()

var queueId = "<queue-id>"
// :remove-start:
val projectId = client.sessions()
    .list(SessionListParams.builder().name("default").limit(1L).build())
    .items().first().id()
val seedRunId = client.runs().queryV2(
    RunQueryV2Params.builder()
        .addProjectId(projectId)
        .minStartTime(OffsetDateTime.now().minusDays(30))
        .pageSize(1L)
        .build()
).items().first().id().get()
queueId = client.annotationQueues().annotationQueues(
    AnnotationQueueAnnotationQueuesParams.builder()
        .name("docs-smithdb-migration-" + java.util.UUID.randomUUID())
        .build()
).id()
client.annotationQueues().runs().create(
    RunCreateParams.builder()
        .queueId(queueId)
        .bodyOfRunsUuidArray(listOf(seedRunId))
        .build()
)
// :remove-end:
val size = client.annotationQueues().retrieveSize(
    queueId,
    AnnotationQueueRetrieveSizeParams.builder()
        .status(AnnotationQueueRetrieveSizeParams.Status.NEEDS_MY_REVIEW)
        .build()
).size()
println(size)

val runs = client.annotationQueues().runs().list(
    queueId,
    RunListParams.builder().status(RunListParams.Status.NEEDS_MY_REVIEW).build()
)
for (run in runs) {
    println("${run.name()} ${run.status()}")
}

val firstRun = client.annotationQueues().retrieveRun(
    0L,
    AnnotationQueueRetrieveRunParams.builder().queueId(queueId).build()
)
// :remove-start:
check(size == 1L) { "expected size 1, got $size" }
check(runs.size == 1) { "expected 1 run, got ${runs.size}" }
check(firstRun.id() == seedRunId) { "index 0 returned a different run" }
println("✓ runs-list-from-queue-before validated")
}
// :remove-end:
// :snippet-end:
