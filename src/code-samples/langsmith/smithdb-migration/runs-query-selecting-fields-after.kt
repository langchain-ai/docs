///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.2.0
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.11

// :snippet-start: runs-query-selecting-fields-after-kt
// :codegroup-tab: After
import com.langchain.smith.client.LangsmithClient
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient
import com.langchain.smith.models.runs.RunQueryV2Params
import com.langchain.smith.models.sessions.SessionListParams

// :remove-start:
fun main() {
    if (System.getenv("LANGSMITH_API_KEY").isNullOrBlank()) {
        println("[smithdb-runs-query-selecting-fields-after] Skipping (LANGSMITH_API_KEY is not set).")
        return
    }

// :remove-end:
val client: LangsmithClient = LangsmithOkHttpClient.fromEnv()

val project = client.sessions().list(
    SessionListParams.builder().name("default").limit(1L).build()
).items().first()
// must explicitly list every field needed; default returns only id
val runs = client.runs().queryV2(
    RunQueryV2Params.builder()
        .addProjectId(project.id())
        .addSelect(RunQueryV2Params.Select.ID)
        .addSelect(RunQueryV2Params.Select.NAME)
        .addSelect(RunQueryV2Params.Select.RUN_TYPE)
        .addSelect(RunQueryV2Params.Select.STATUS)
        .addSelect(RunQueryV2Params.Select.START_TIME)
        .addSelect(RunQueryV2Params.Select.INPUTS)
        .addSelect(RunQueryV2Params.Select.ERROR)
        .build()
).items()
for (run in runs) {
    println("${run.id()} ${run.name()} ${run.runType()} ${run.status()} ${run.startTime()} ${run.inputs()} ${run.error()}")
    // :remove-start:
    break
    // :remove-end:
}
// :remove-start:
}
// :remove-end:
// :snippet-end:
