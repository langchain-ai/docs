///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.0.21
//DEPS com.langchain.smith:langsmith-java:0.1.0-alpha.25

// :snippet-start: ls-metadata-parameters-basic-kt
// :codegroup-tab: Kotlin
import com.langchain.smith.tracing.RunType
import com.langchain.smith.tracing.TraceConfig
import com.langchain.smith.tracing.traceable
// :remove-start:
fun callCustomApi(prompt: String): String = "example response"

fun main() {
    if (System.getenv("LANGSMITH_API_KEY").isNullOrBlank()) {
        println("[ls-metadata-parameters-basic] Skipping (LANGSMITH_API_KEY is not set).")
        return
    }
// :remove-end:

val myCustomLlm =
    traceable(
        { prompt: String -> callCustomApi(prompt) },
        TraceConfig.builder()
            .runType(RunType.LLM)
            .metadata(
                mapOf(
                    "ls_provider" to "my_provider",
                    "ls_model_name" to "my_custom_model",
                ),
            )
            .build(),
    )

// :remove-start:
println(myCustomLlm("hello"))
}
// :remove-end:
// :snippet-end:
