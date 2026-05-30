///usr/bin/env jbang "$0" "$@" ; exit $?
//DEPS com.langchain.smith:langsmith-java:0.1.0-alpha.25
//DEPS com.openai:openai-java:4.30.0

// :snippet-start: observability-quickstart-app-java
// :codegroup-tab: Java
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
  public static void main(String[] args) {
    // :remove-start:
    if (System.getenv("LANGSMITH_API_KEY") == null
        || System.getenv("LANGSMITH_API_KEY").isBlank()
        || System.getenv("OPENAI_API_KEY") == null
        || System.getenv("OPENAI_API_KEY").isBlank()) {
      System.out.println(
          "[observability-quickstart-app] Skipping (LANGSMITH_API_KEY and OPENAI_API_KEY required).");
      return;
    }
    // :remove-end:
    new ObservabilityQuickstartRunner().run();
  }

  private static final class ObservabilityQuickstartRunner {
    private final OpenAIClient client =
        OpenAITracing.wrapOpenAI(OpenAIOkHttpClient.fromEnv());

    private final Function<String, String> getContext =
        Tracing.traceFunction(
            question -> "LangSmith traces are stored for 14 days on the Developer plan.",
            TraceConfig.builder().name("get_context").runType(RunType.TOOL).build());

    private final Function<String, String> assistant =
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

    void run() {
      System.out.println(assistant.apply("How long are LangSmith traces stored?"));
    }
  }
}
// :snippet-end:
