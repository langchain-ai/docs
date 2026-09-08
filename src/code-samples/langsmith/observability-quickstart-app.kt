///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.0.21
//DEPS com.langchain.smith:langsmith-java:0.1.0-alpha.25
//DEPS com.openai:openai-java:4.30.0

// :snippet-start: observability-quickstart-app-kt
// :codegroup-tab: Kotlin
import com.langchain.smith.tracing.RunType
import com.langchain.smith.tracing.TraceConfig
import com.langchain.smith.tracing.traceable
import com.langchain.smith.wrappers.openai.wrapOpenAI
import com.openai.client.okhttp.OpenAIOkHttpClient
import com.openai.models.ChatModel
import com.openai.models.chat.completions.ChatCompletionCreateParams
import com.openai.models.chat.completions.ChatCompletionMessageParam
import com.openai.models.chat.completions.ChatCompletionSystemMessageParam
import com.openai.models.chat.completions.ChatCompletionUserMessageParam
import kotlin.jvm.optionals.getOrNull

// :remove-start:
fun main() {
if (System.getenv("LANGSMITH_API_KEY").isNullOrBlank()
    || System.getenv("OPENAI_API_KEY").isNullOrBlank()
) {
    println("[observability-quickstart-app] Skipping (LANGSMITH_API_KEY and OPENAI_API_KEY required).")
    return
}
// :remove-end:
val client = wrapOpenAI(OpenAIOkHttpClient.fromEnv())

val getContext =
    traceable(
        { _: String -> "LangSmith traces are stored for 14 days on the Developer plan." },
        TraceConfig.builder().name("get_context").runType(RunType.TOOL).build(),
    )

val assistant =
    traceable(
        { question: String ->
            val context = getContext(question)
            val response =
                client.chat().completions().create(
                    ChatCompletionCreateParams.builder()
                        .model(ChatModel.GPT_5_CHAT_LATEST)
                        .addMessage(
                            ChatCompletionMessageParam.ofSystem(
                                ChatCompletionSystemMessageParam.builder()
                                    .content("Answer using the context below.\n\nContext: $context")
                                    .build(),
                            ),
                        )
                        .addMessage(
                            ChatCompletionMessageParam.ofUser(
                                ChatCompletionUserMessageParam.builder()
                                    .content(question)
                                    .build(),
                            ),
                        )
                        .build(),
                )
            response.choices()[0].message().content().getOrNull().orEmpty()
        },
        TraceConfig.builder().name("assistant").build(),
    )

println(assistant("How long are LangSmith traces stored?"))
// :remove-start:
}
// :remove-end:
// :snippet-end:

