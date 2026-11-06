///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.2.0
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.22

// :snippet-start: runs-list-from-queue-after-kt
// :codegroup-tab: After
import com.langchain.smith.client.LangsmithClient
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient
import com.langchain.smith.models.annotationqueues.items.ItemListParams
import com.langchain.smith.models.annotationqueues.items.ItemRetrieveCountParams
import com.langchain.smith.models.runs.RunRetrieveV2Params
import java.time.OffsetDateTime
// :remove-start:
import com.langchain.smith.models.annotationqueues.AnnotationQueueAnnotationQueuesParams
import com.langchain.smith.models.annotationqueues.runs.RunCreateParams
import com.langchain.smith.models.runs.RunQueryV2Params
import com.langchain.smith.models.sessions.SessionListParams

fun main() {
    if (System.getenv("LANGSMITH_API_KEY").isNullOrBlank()) {
        println("[smithdb-runs-list-from-queue-after] Skipping (LANGSMITH_API_KEY is not set).")
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
val names = mutableListOf<String>()
// :remove-end:
val count = client.annotationQueues().items().retrieveCount(
    queueId,
    ItemRetrieveCountParams.builder().status("needs_my_review").build()
).count().get()
println(count)

// Items carry the run's lookup keys, not its contents.
val page = client.annotationQueues().items().list(
    queueId,
    ItemListParams.builder()
        .status(ItemListParams.Status.NEEDS_MY_REVIEW)
        .itemType(ItemListParams.ItemType.RUN)
        .build()
)
for (item in page.autoPager()) {
    val run = client.runs().retrieveV2(
        item.runId().get(),
        RunRetrieveV2Params.builder()
            .projectId(item.projectId().get())
            .startTime(OffsetDateTime.parse(item.startTime().get()))
            .addSelect(RunRetrieveV2Params.Select.NAME)
            .addSelect(RunRetrieveV2Params.Select.STATUS)
            .addSelect(RunRetrieveV2Params.Select.INPUTS)
            .addSelect(RunRetrieveV2Params.Select.OUTPUTS)
            .build()
    )
    println("${run.name().orElse("")} ${run.status().map { it.toString() }.orElse("")}")
    // :remove-start:
    names.add(run.name().orElse(""))
    // :remove-end:
}
// :remove-start:
check(count == 1L) { "expected count 1, got $count" }
check(names.size == 1 && names[0].isNotEmpty()) { "expected 1 named run, got $names" }
println("✓ runs-list-from-queue-after validated")
}
// :remove-end:
// :snippet-end:
