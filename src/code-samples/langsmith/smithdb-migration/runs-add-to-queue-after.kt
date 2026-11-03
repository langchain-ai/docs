///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.2.0
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.22

// :snippet-start: runs-add-to-queue-after-kt
// :codegroup-tab: After
import com.langchain.smith.client.LangsmithClient
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient
import com.langchain.smith.models.annotationqueues.AnnotationQueueAnnotationQueuesParams
import com.langchain.smith.models.annotationqueues.items.ItemCreateParams
import com.langchain.smith.models.runs.RunQueryV2Params
import com.langchain.smith.models.runs.RunSelectField
import com.langchain.smith.models.sessions.SessionListParams
import java.time.OffsetDateTime

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
val runs = client.runs().queryV2(
    RunQueryV2Params.builder()
        .addProjectId(projectId)
        .minStartTime(OffsetDateTime.now().minusDays(30))
        .addSelect(RunSelectField.ID)
        .addSelect(RunSelectField.PROJECT_ID)
        .addSelect(RunSelectField.START_TIME)
        .pageSize(5L)
        .build()
).items()

val params = ItemCreateParams.builder().queueId(queueId)
for (run in runs) {
    params.addItem(
        ItemCreateParams.Item.builder()
            .itemType(ItemCreateParams.Item.ItemType.RUN)
            .runId(run.id().get())
            .projectId(run.projectId().get())
            .startTime(run.startTime().get())
            .build()
    )
}
client.annotationQueues().items().create(params.build())
// :remove-start:
}
// :remove-end:
// :snippet-end:
