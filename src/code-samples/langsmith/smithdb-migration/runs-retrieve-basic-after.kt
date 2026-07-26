///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.2.0
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.18

// :snippet-start: runs-retrieve-basic-after-kt
// :codegroup-tab: After
import java.time.OffsetDateTime

import com.langchain.smith.client.LangsmithClient
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient
import com.langchain.smith.models.runs.RunRetrieveV2Params
import com.langchain.smith.models.sessions.SessionListParams
// :remove-start:
import com.langchain.smith.models.runs.RunQueryV2Params
import com.langchain.smith.models.runs.RunSelectField
// :remove-end:

// :remove-start:
fun main() {
    if (System.getenv("LANGSMITH_API_KEY").isNullOrBlank()) {
        println("[smithdb-runs-retrieve-basic-after] Skipping (LANGSMITH_API_KEY is not set).")
        return
    }

// :remove-end:
val client: LangsmithClient = LangsmithOkHttpClient.fromEnv()

val project = client.sessions().list(
    SessionListParams.builder().name("default").limit(1L).build()
).items().first()

var runId = "<run-id>"
var startTime = "<run-start-time-rfc3339>"
// :remove-start:
val maxStart = OffsetDateTime.now()
val foundRun = client.runs().queryV2(
    RunQueryV2Params.builder()
        .addProjectId(project.id())
        .minStartTime(maxStart.minusMonths(1))
        .maxStartTime(maxStart)
        .addSelect(RunSelectField.ID)
        .addSelect(RunSelectField.START_TIME)
        .pageSize(1L)
        .build()
).items().first()
runId = foundRun.id().get()
startTime = foundRun.startTime().get().toString()
// :remove-end:
val run = client.runs().retrieveV2(
    runId,
    RunRetrieveV2Params.builder()
        .projectId(project.id())
        .startTime(OffsetDateTime.parse(startTime))
        .addSelect(RunRetrieveV2Params.Select.NAME)
        .addSelect(RunRetrieveV2Params.Select.STATUS)
        .addSelect(RunRetrieveV2Params.Select.TOTAL_TOKENS)
        .build()
)
println("${run.name()} ${run.status()} ${run.totalTokens()}")
// :remove-start:
}
// :remove-end:
// :snippet-end:
