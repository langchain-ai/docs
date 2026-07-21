///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.2.0
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.18

// :snippet-start: runs-geturl-after-kt
// :codegroup-tab: After
import com.langchain.smith.client.LangsmithClient
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient
import com.langchain.smith.models.runs.RunGetUrlParams
// :remove-start:
import java.time.OffsetDateTime

import com.langchain.smith.models.runs.RunQueryV2Params
import com.langchain.smith.models.sessions.SessionListParams
// :remove-end:

fun main() {
    val client: LangsmithClient = LangsmithOkHttpClient.fromEnv()

    var runId = "<run-id>"
    // :remove-start:
    val project = client.sessions().list(
        SessionListParams.builder().name("default").limit(1L).build()
    ).items().first()
    val foundRun = client.runs().queryV2(
        RunQueryV2Params.builder()
            .addProjectId(project.id())
            .minStartTime(OffsetDateTime.now().minusMonths(1))
            .pageSize(1L)
            .build()
    ).items().first()
    runId = foundRun.id().get()
    // :remove-end:
    val run = client.runs().retrieve(runId)

    val response = client.runs().getUrl(
        run.id(),
        RunGetUrlParams.builder()
            .projectId(run.sessionId())
            .traceId(run.traceId())
            .startTime(run.startTime().get().toString()) // Optional, but speeds up retrieval
            .build()
    )
    println(response.url().get())
}
// :snippet-end:
