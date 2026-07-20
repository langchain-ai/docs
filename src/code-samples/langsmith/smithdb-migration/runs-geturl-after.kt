///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.2.0
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.18

// :snippet-start: runs-geturl-after-kt
// :codegroup-tab: After
import com.langchain.smith.client.LangsmithClient
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient
import com.langchain.smith.models.runs.RunGetUrlParams
import com.langchain.smith.models.runs.RunQueryV2Params
import com.langchain.smith.models.sessions.SessionListParams

fun main() {
    val client: LangsmithClient = LangsmithOkHttpClient.fromEnv()

    val project = client.sessions().list(
        SessionListParams.builder().name("default").limit(1L).build()
    ).items().first()

    val run = client.runs().queryV2(
        RunQueryV2Params.builder()
            .addProjectId(project.id())
            .addSelect(RunQueryV2Params.Select.ID)
            .addSelect(RunQueryV2Params.Select.TRACE_ID)
            .addSelect(RunQueryV2Params.Select.START_TIME)
            .pageSize(1L)
            .build()
    ).items().first()

    val response = client.runs().getUrl(
        run.id().get(),
        RunGetUrlParams.builder()
            .projectId(project.id())
            .traceId(run.traceId().get())
            .startTime(run.startTime().get().toString())
            .build()
    )
    println(response.url().get())
}
// :snippet-end:
