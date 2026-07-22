///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.2.0
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.18

// :snippet-start: runs-retrieve-not-found-before-kt
// :codegroup-tab: Before
import com.langchain.smith.client.LangsmithClient
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient
import com.langchain.smith.errors.NotFoundException
// :remove-start:
import java.util.UUID
// :remove-end:

// :remove-start:
fun main() {
    if (System.getenv("LANGSMITH_API_KEY").isNullOrBlank()) {
        println("[smithdb-runs-retrieve-not-found-before] Skipping (LANGSMITH_API_KEY is not set).")
        return
    }

// :remove-end:
val client: LangsmithClient = LangsmithOkHttpClient.fromEnv()

var runId = "<run-id>"
// :remove-start:
runId = UUID.randomUUID().toString()
// :remove-end:
try {
    client.runs().retrieve(runId)
} catch (e: NotFoundException) {
    println("Run $runId not found")
}
// :remove-start:
}
// :remove-end:
// :snippet-end:
