///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.0.21
//DEPS com.langchain.smith:langsmith-java:0.1.0-alpha.25

// :snippet-start: ls-metadata-parameters-configured-kt
// :codegroup-tab: Kotlin
// :remove-start:
import com.langchain.smith.tracing.RunType
import com.langchain.smith.tracing.TraceConfig
import com.langchain.smith.tracing.traceable

fun callLlm(messages: List<Map<String, String>>): String = "example response"

fun main() {
    if (System.getenv("LANGSMITH_API_KEY").isNullOrBlank()) {
        println("[ls-metadata-parameters-configured] Skipping (LANGSMITH_API_KEY is not set).")
        return
    }

// :remove-end:
val myConfiguredLlm =
    traceable(
        { messages: List<Map<String, String>> -> callLlm(messages) },
        TraceConfig.builder()
            .runType(RunType.LLM)
            .metadata(
                mapOf(
                    "ls_provider" to "openai",
                    "ls_model_name" to "gpt-5.4",
                    "ls_temperature" to 0.7,
                    "ls_max_tokens" to 4096,
                    "ls_stop" to listOf("END"),
                    "ls_invocation_params" to
                        mapOf(
                            "top_p" to 0.9,
                            "frequency_penalty" to 0.5,
                        ),
                ),
            )
            .build(),
    )

// :remove-start:
    println(myConfiguredLlm(listOf(mapOf("role" to "user", "content" to "Hello"))))
}
// :remove-end:
// :snippet-end:
