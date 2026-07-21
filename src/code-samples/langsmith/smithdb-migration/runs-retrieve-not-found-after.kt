///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.2.0
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.18

// :snippet-start: runs-retrieve-not-found-after-kt
// :codegroup-tab: After
import java.time.OffsetDateTime

import com.langchain.smith.client.LangsmithClient
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient
import com.langchain.smith.errors.NotFoundException
import com.langchain.smith.models.runs.RunRetrieveV2Params
import com.langchain.smith.models.sessions.SessionListParams
// :remove-start:
import java.util.UUID
// :remove-end:

// :remove-start:
fun main() {
    if (System.getenv("LANGSMITH_API_KEY").isNullOrBlank()) {
        println("[smithdb-runs-retrieve-not-found-after] Skipping (LANGSMITH_API_KEY is not set).")
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
runId = UUID.randomUUID().toString()
startTime = OffsetDateTime.now().toString()
// :remove-end:
try {
    client.runs().retrieveV2(
        runId,
        RunRetrieveV2Params.builder()
            .projectId(project.id())
            .startTime(OffsetDateTime.parse(startTime))
            .build()
    )
} catch (e: NotFoundException) {
    println("Run $runId not found")
}
// :remove-start:
}
// :remove-end:
// :snippet-end:
