///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.0.21
//DEPS com.langchain.smith:langsmith-java:0.1.0-alpha.25

// :snippet-start: cost-tracking-tool-cost-output-kt
// :codegroup-tab: Kotlin
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient
import com.langchain.smith.tracing.RunType
import com.langchain.smith.tracing.TraceConfig
import com.langchain.smith.tracing.traceable
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit

// :remove-start:
fun main() {
    if (System.getenv("LANGSMITH_API_KEY").isNullOrBlank()) {
        println("[cost-tracking-tool-cost-output] Skipping (LANGSMITH_API_KEY is not set).")
        return
    }
// :remove-end:
val langsmith = LangsmithOkHttpClient.fromEnv()
val executor = Executors.newSingleThreadExecutor()

try {
    val getWeather =
        traceable(
            { city: String ->
                mapOf(
                    "temperature_f" to 68,
                    "condition" to "sunny",
                    "city" to city,
                    "usage_metadata" to mapOf("total_cost" to 0.0015),
                )
            },
            TraceConfig.builder()
                .name("get_weather")
                .runType(RunType.TOOL)
                .client(langsmith)
                .executor(executor)
                .build(),
        )

    val toolResponse = getWeather("San Francisco")
} finally {
    executor.shutdown()
    check(executor.awaitTermination(10, TimeUnit.SECONDS)) {
        "Timed out waiting for LangSmith traces to submit"
    }
}
// :remove-start:
}
// :remove-end:
// :snippet-end:
