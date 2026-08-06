///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.0.21
//DEPS com.langchain.smith:langsmith-java:0.1.0-alpha.25
//DEPS com.openai:openai-java:4.30.0

// :snippet-start: traceable-pipeline-kt
// :codegroup-tab: Kotlin
import com.langchain.smith.tracing.RunType
import com.langchain.smith.tracing.TraceConfig
import com.langchain.smith.tracing.traceable
import com.openai.client.okhttp.OpenAIOkHttpClient
import com.openai.models.ChatModel
import com.openai.models.chat.completions.ChatCompletion
import com.openai.models.chat.completions.ChatCompletionCreateParams
import com.openai.models.chat.completions.ChatCompletionMessageParam
import com.openai.models.chat.completions.ChatCompletionSystemMessageParam
import com.openai.models.chat.completions.ChatCompletionUserMessageParam
import kotlin.jvm.optionals.getOrNull

// :remove-start:
fun main() {
    if (System.getenv("OPENAI_API_KEY").isNullOrBlank()) {
        println("[traceable-pipeline] Skipping (OPENAI_API_KEY is not set).")
        return
    }
// :remove-end:
val openai = OpenAIOkHttpClient.fromEnv()

val formatPrompt =
    traceable(
        { subject: String ->
            listOf(
                ChatCompletionMessageParam.ofSystem(
                    ChatCompletionSystemMessageParam.builder()
                        .content("You are a helpful assistant.")
                        .build(),
                ),
                ChatCompletionMessageParam.ofUser(
                    ChatCompletionUserMessageParam.builder()
                        .content("What's a good name for a store that sells $subject?")
                        .build(),
                ),
            )
        },
        TraceConfig.builder().name("format_prompt").build(),
    )

val invokeLlm =
    traceable(
        { messages: List<ChatCompletionMessageParam> ->
            openai.chat().completions().create(
                ChatCompletionCreateParams.builder()
                    .model(ChatModel.GPT_5_CHAT_LATEST)
                    .messages(messages)
                    .temperature(0.0)
                    .build(),
            )
        },
        TraceConfig.builder().name("invoke_llm").runType(RunType.LLM).build(),
    )

val parseOutput =
    traceable(
        { response: ChatCompletion ->
            response.choices()[0].message().content().getOrNull().orEmpty()
        },
        TraceConfig.builder().name("parse_output").build(),
    )

val runPipeline =
    traceable(
        { subject: String -> parseOutput(invokeLlm(formatPrompt(subject))) },
        TraceConfig.builder().name("run_pipeline").build(),
    )

println(runPipeline("colorful socks"))
// :remove-start:
}
// :remove-end:
// :snippet-end:

