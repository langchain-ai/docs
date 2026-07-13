///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.2.0
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.13

// :snippet-start: experiment-runs-query-lookup-experiment-id-kt
import com.langchain.smith.client.LangsmithClient
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient
import com.langchain.smith.models.sessions.SessionListParams

// :remove-start:
fun main() {
    if (false) {
// :remove-end:
val client: LangsmithClient = LangsmithOkHttpClient.fromEnv()
val experimentId = client.sessions()
    .list(SessionListParams.builder().name("my-experiment").build())
    .items()
    .first()
    .id()
// :remove-start:
    }
}
// :remove-end:
// :snippet-end:
