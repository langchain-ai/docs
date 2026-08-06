///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.0.21
//DEPS com.langchain.smith:langsmith-java:0.1.0-alpha.25

// :snippet-start: cost-tracking-llm-cost-direct-kt
// :codegroup-tab: Kotlin
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient
import com.langchain.smith.tracing.RunType
import com.langchain.smith.tracing.TraceConfig
import com.langchain.smith.tracing.getCurrentRunTree
import com.langchain.smith.tracing.traceable
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit

// :remove-start:
fun main() {
    if (System.getenv("LANGSMITH_API_KEY").isNullOrBlank()) {
        println("[cost-tracking-llm-cost-direct] Skipping (LANGSMITH_API_KEY is not set).")
        return
    }

// :remove-end:
val langsmith = LangsmithOkHttpClient.fromEnv()
val executor = Executors.newSingleThreadExecutor()

fun message(role: String, content: String) = mapOf("role" to role, "content" to content)

try {
    val messages =
        listOf(
            message("system", "You are a helpful assistant."),
            message("user", "I'd like to book a table for two."),
        )

    val chatModel =
        traceable(
            { _: List<Map<String, String>> ->
                val usageMetadata =
                    mapOf(
                        "input_cost" to 1.1e-6,
                        "input_cost_details" to mapOf("cache_read" to 2.3e-7),
                        "output_cost" to 5.0e-6,
                    )
                getCurrentRunTree()?.metadata?.put("usage_metadata", usageMetadata)
                message(
                    "assistant",
                    "Sure, what time would you like to book the table for?",
                )
            },
            TraceConfig.builder()
                .name("chat_model")
                .runType(RunType.LLM)
                .client(langsmith)
                .executor(executor)
                .metadata(
                    mapOf(
                        "ls_provider" to "my_provider",
                        "ls_model_name" to "my_model",
                    ),
                )
                .build(),
        )

    chatModel(messages)
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
