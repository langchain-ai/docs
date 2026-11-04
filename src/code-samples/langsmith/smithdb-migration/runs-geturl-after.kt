///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.2.0
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.22

// :snippet-start: runs-geturl-after-kt
// :codegroup-tab: After
import com.langchain.smith.client.LangsmithClient
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient
import com.langchain.smith.models.runs.RunGetUrlParams
import com.langchain.smith.models.runs.RunRetrieveV2Params
// :remove-start:
import java.time.OffsetDateTime

import com.langchain.smith.models.runs.RunQueryV2Params
import com.langchain.smith.models.sessions.SessionListParams
// :remove-end:

fun main() {
    val client: LangsmithClient = LangsmithOkHttpClient.fromEnv()

    var runId = "<run-id>"
    var projectId = "<project-id>"
    // :remove-start:
    projectId = client.sessions().list(
        SessionListParams.builder().name("default").limit(1L).build()
    ).items().first().id()
    val foundRun = client.runs().queryV2(
        RunQueryV2Params.builder()
            .addProjectId(projectId)
            .minStartTime(OffsetDateTime.now().minusMonths(1))
            .pageSize(1L)
            .build()
    ).items().first()
    runId = foundRun.id().get()
    // :remove-end:
    val run = client.runs().retrieveV2(
        runId,
        RunRetrieveV2Params.builder()
            .projectId(projectId)
            .addSelect(RunRetrieveV2Params.Select.ID)
            .addSelect(RunRetrieveV2Params.Select.PROJECT_ID)
            .addSelect(RunRetrieveV2Params.Select.TRACE_ID)
            .addSelect(RunRetrieveV2Params.Select.START_TIME)
            .build()
    )

    val response = client.runs().getUrl(
        run.id().get(),
        RunGetUrlParams.builder()
            .projectId(run.projectId().get())
            .traceId(run.traceId().get())
            .startTime(run.startTime().get().toString()) // Optional, but speeds up retrieval
            .build()
    )
    println(response.url().get())
}
// :snippet-end:
