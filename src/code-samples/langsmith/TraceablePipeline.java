///usr/bin/env jbang "$0" "$@" ; exit $?
//DEPS com.langchain.smith:langsmith-java:0.1.0-alpha.25
//DEPS com.openai:openai-java:4.30.0

// :snippet-start: traceable-pipeline-java
// :codegroup-tab: Java
import com.langchain.smith.tracing.RunType;
import com.langchain.smith.tracing.TraceConfig;
import com.langchain.smith.tracing.Tracing;
import com.openai.client.OpenAIClient;
import com.openai.client.okhttp.OpenAIOkHttpClient;
import com.openai.models.ChatModel;
import com.openai.models.chat.completions.ChatCompletion;
import com.openai.models.chat.completions.ChatCompletionCreateParams;
import com.openai.models.chat.completions.ChatCompletionMessageParam;
import com.openai.models.chat.completions.ChatCompletionSystemMessageParam;
import com.openai.models.chat.completions.ChatCompletionUserMessageParam;
import java.util.Arrays;
import java.util.List;
import java.util.function.Function;

public class TraceablePipeline {
  public static void main(String[] args) {
    // :remove-start:
    if (System.getenv("LANGSMITH_API_KEY") == null
        || System.getenv("LANGSMITH_API_KEY").isBlank()
        || System.getenv("OPENAI_API_KEY") == null
        || System.getenv("OPENAI_API_KEY").isBlank()) {
      System.out.println(
          "[traceable-pipeline] Skipping (LANGSMITH_API_KEY and OPENAI_API_KEY required).");
      return;
    }
    // :remove-end:
    new TraceablePipelineRunner().run();
  }

  private static final class TraceablePipelineRunner {
    private final OpenAIClient openai = OpenAIOkHttpClient.fromEnv();

    private final Function<String, List<ChatCompletionMessageParam>> formatPrompt =
        Tracing.traceFunction(
            subject ->
                Arrays.asList(
                    ChatCompletionMessageParam.ofSystem(
                        ChatCompletionSystemMessageParam.builder()
                            .content("You are a helpful assistant.")
                            .build()),
                    ChatCompletionMessageParam.ofUser(
                        ChatCompletionUserMessageParam.builder()
                            .content("What's a good name for a store that sells " + subject + "?")
                            .build())),
            TraceConfig.builder().name("format_prompt").build());

    private final Function<List<ChatCompletionMessageParam>, ChatCompletion> invokeLlm =
        Tracing.traceFunction(
            messages ->
                openai.chat()
                    .completions()
                    .create(
                        ChatCompletionCreateParams.builder()
                            .model(ChatModel.GPT_5_CHAT_LATEST)
                            .messages(messages)
                            .temperature(0.0)
                            .build()),
            TraceConfig.builder().name("invoke_llm").runType(RunType.LLM).build());

    private final Function<ChatCompletion, String> parseOutput =
        Tracing.traceFunction(
            response -> response.choices().get(0).message().content().orElse(""),
            TraceConfig.builder().name("parse_output").build());

    private final Function<String, String> runPipeline =
        Tracing.traceFunction(
            subject -> parseOutput.apply(invokeLlm.apply(formatPrompt.apply(subject))),
            TraceConfig.builder().name("run_pipeline").build());

    void run() {
      runPipeline.apply("colorful socks");
    }
  }
}

// :snippet-end:
