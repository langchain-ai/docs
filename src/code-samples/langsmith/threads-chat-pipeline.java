///usr/bin/env jbang "$0" "$@" ; exit $?
//DEPS com.langchain.smith:langsmith-java:0.1.0-alpha.25
//DEPS com.openai:openai-java:4.30.0

// :snippet-start: threads-chat-pipeline-java
// :codegroup-tab: Java
// :codegroup-fence-mods: expandable wrap
import com.langchain.smith.client.LangsmithClient;
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient;
import com.langchain.smith.tracing.TraceConfig;
import com.langchain.smith.tracing.Tracing;
import com.langchain.smith.wrappers.openai.OpenAITracing;
import com.openai.client.OpenAIClient;
import com.openai.client.okhttp.OpenAIOkHttpClient;
import com.openai.models.ChatModel;
import com.openai.models.chat.completions.ChatCompletion;
import com.openai.models.chat.completions.ChatCompletionAssistantMessageParam;
import com.openai.models.chat.completions.ChatCompletionCreateParams;
import com.openai.models.chat.completions.ChatCompletionMessageParam;
import com.openai.models.chat.completions.ChatCompletionUserMessageParam;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.function.Function;

class ThreadsChatPipeline {
  private static final String THREAD_ID = "01990f3e-7f97-74c5-a9b6-8d3f7e8e2f11";

  private static final class OpenAiResources {
    private static final LangsmithClient langsmith = LangsmithOkHttpClient.fromEnv();
    private static final ExecutorService executor = Executors.newSingleThreadExecutor();
    private static final Map<String, Object> threadMetadata = new HashMap<>();

    static {
      threadMetadata.put("thread_id", THREAD_ID);
    }

    private static final OpenAIClient openai =
        OpenAITracing.wrapOpenAI(
            OpenAIOkHttpClient.fromEnv(),
            TraceConfig.builder()
                .client(langsmith)
                .executor(executor)
                .metadata(threadMetadata)
                .build());

    private static final List<ChatCompletionMessageParam> threadHistory = new ArrayList<>();

    static final Function<ChatRequest, Map<String, List<ChatCompletionMessageParam>>> CHAT_PIPELINE =
        Tracing.traceFunction(
            request -> {
              List<ChatCompletionMessageParam> allMessages = new ArrayList<>();
              if (request.getChatHistory()) {
                allMessages.addAll(threadHistory);
              }
              allMessages.addAll(request.getMessages());

              ChatCompletion chatCompletion =
                  openai
                      .chat()
                      .completions()
                      .create(
                          ChatCompletionCreateParams.builder()
                              .model(ChatModel.GPT_5_CHAT_LATEST)
                              .messages(allMessages)
                              .build());

              String content = chatCompletion.choices().get(0).message().content().orElse("");
              List<ChatCompletionMessageParam> fullConversation = new ArrayList<>(allMessages);
              fullConversation.add(
                  ChatCompletionMessageParam.ofAssistant(
                      ChatCompletionAssistantMessageParam.builder().content(content).build()));
              threadHistory.clear();
              threadHistory.addAll(fullConversation);

              return Collections.singletonMap("messages", fullConversation);
            },
            TraceConfig.builder()
                .name("Chat Bot")
                .client(langsmith)
                .executor(executor)
                .metadata(threadMetadata)
                .build());

    private OpenAiResources() {}

    static ExecutorService executor() {
      return executor;
    }
  }

  static Function<ChatRequest, Map<String, List<ChatCompletionMessageParam>>> chatPipeline() {
    return OpenAiResources.CHAT_PIPELINE;
  }

  public static void main(String[] args) throws InterruptedException {
    // :remove-start:
    if (System.getenv("LANGSMITH_API_KEY") == null
        || System.getenv("LANGSMITH_API_KEY").isBlank()
        || System.getenv("OPENAI_API_KEY") == null
        || System.getenv("OPENAI_API_KEY").isBlank()) {
      System.out.println(
          "[threads-chat-pipeline] Skipping (LANGSMITH_API_KEY and OPENAI_API_KEY required).");
      return;
    }
    // :remove-end:
    try {
      List<ChatCompletionMessageParam> messages =
          Collections.singletonList(
              ChatCompletionMessageParam.ofUser(
                  ChatCompletionUserMessageParam.builder()
                      .content("Hi, my name is Sally")
                      .build()));
      chatPipeline().apply(new ChatRequest(messages, false));
    } finally {
      OpenAiResources.executor().shutdown();
      if (!OpenAiResources.executor().awaitTermination(10, TimeUnit.SECONDS)) {
        throw new IllegalStateException("Timed out waiting for LangSmith traces to submit");
      }
    }
  }

  static class ChatRequest {
    private final List<ChatCompletionMessageParam> messages;
    private final boolean getChatHistory;

    ChatRequest(List<ChatCompletionMessageParam> messages, boolean getChatHistory) {
      this.messages = messages;
      this.getChatHistory = getChatHistory;
    }

    List<ChatCompletionMessageParam> getMessages() {
      return messages;
    }

    boolean getChatHistory() {
      return getChatHistory;
    }
  }
}
// :snippet-end:

/** Compile-only helpers so continuation fragments stay valid Java and extract as snippets. */
final class ThreadsContinuationHarness {
  private ThreadsContinuationHarness() {}

  static void continueWhatIsMyName() {
    // :snippet-start: threads-continue-name-java
    // :codegroup-tab: Java
    List<ChatCompletionMessageParam> messages =
        Collections.singletonList(
            ChatCompletionMessageParam.ofUser(
                ChatCompletionUserMessageParam.builder()
                    .content("What is my name")
                    .build()));

    ThreadsChatPipeline.chatPipeline().apply(new ThreadsChatPipeline.ChatRequest(messages, true));
    // :snippet-end:
  }

  static void continueFirstMessage() {
    // :snippet-start: threads-continue-first-message-java
    // :codegroup-tab: Java
    List<ChatCompletionMessageParam> messages =
        Collections.singletonList(
            ChatCompletionMessageParam.ofUser(
                ChatCompletionUserMessageParam.builder()
                    .content("What was the first message I sent you?")
                    .build()));

    ThreadsChatPipeline.chatPipeline().apply(new ThreadsChatPipeline.ChatRequest(messages, true));
    // :snippet-end:
  }
}
