///usr/bin/env jbang "$0" "$@" ; exit $?
//DEPS com.langchain.smith:langsmith-java:0.1.0-alpha.25
//DEPS com.openai:openai-java:4.30.0

// :snippet-start: observability-quickstart-app-java
import com.langchain.smith.tracing.RunType;
import com.langchain.smith.tracing.TraceConfig;
import com.langchain.smith.tracing.Tracing;
import com.langchain.smith.wrappers.openai.OpenAITracing;
import com.openai.client.OpenAIClient;
import com.openai.client.okhttp.OpenAIOkHttpClient;
import com.openai.models.ChatModel;
import com.openai.models.chat.completions.ChatCompletion;
import com.openai.models.chat.completions.ChatCompletionCreateParams;
import com.openai.models.chat.completions.ChatCompletionMessageParam;
import com.openai.models.chat.completions.ChatCompletionSystemMessageParam;
import com.openai.models.chat.completions.ChatCompletionUserMessageParam;
import java.util.function.Function;

class ObservabilityQuickstartApp {
  private static final OpenAIClient client =
      OpenAITracing.wrapOpenAI(OpenAIOkHttpClient.fromEnv());

  private static final Function<String, String> getContext =
      Tracing.traceFunction(
          question -> "LangSmith traces are stored for 14 days on the Developer plan.",
          TraceConfig.builder().name("get_context").runType(RunType.TOOL).build());

  private static final Function<String, String> assistant =
      Tracing.traceFunction(
          question -> {
            String context = getContext.apply(question);
            ChatCompletion response =
                client.chat()
                    .completions()
                    .create(
                        ChatCompletionCreateParams.builder()
                            .model(ChatModel.GPT_5_CHAT_LATEST)
                            .addMessage(
                                ChatCompletionMessageParam.ofSystem(
                                    ChatCompletionSystemMessageParam.builder()
                                        .content(
                                            "Answer using the context below.\n\nContext: " + context)
                                        .build()))
                            .addMessage(
                                ChatCompletionMessageParam.ofUser(
                                    ChatCompletionUserMessageParam.builder()
                                        .content(question)
                                        .build()))
                            .build());
            return response.choices().get(0).message().content().orElse("");
          },
          TraceConfig.builder().name("assistant").build());

  public static void main(String[] args) {
    if (System.getenv("OPENAI_API_KEY") == null || System.getenv("OPENAI_API_KEY").isBlank()) {
      System.out.println("[observability-quickstart-app] Skipping (OPENAI_API_KEY is not set).");
      return;
    }
    System.out.println(assistant.apply("How long are LangSmith traces stored?"));
  }
}
// :snippet-end:

