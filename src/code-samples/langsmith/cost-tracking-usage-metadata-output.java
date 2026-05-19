///usr/bin/env jbang "$0" "$@" ; exit $?
//DEPS com.langchain.smith:langsmith-java:0.1.0-alpha.25

// :snippet-start: cost-tracking-usage-metadata-output-java
// :codegroup-tab: Java
// :codegroup-fence-mods: expandable wrap
import com.langchain.smith.client.LangsmithClient;
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient;
import com.langchain.smith.tracing.RunType;
import com.langchain.smith.tracing.TraceConfig;
import com.langchain.smith.tracing.Tracing;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.function.Function;

class CostTrackingUsageMetadataOutput {
  public static void main(String[] args) throws InterruptedException {
    if (System.getenv("LANGSMITH_API_KEY") == null
        || System.getenv("LANGSMITH_API_KEY").isBlank()) {
      System.out.println(
          "[cost-tracking-usage-metadata-output] Skipping (LANGSMITH_API_KEY is not set).");
      return;
    }

    LangsmithClient langsmith = LangsmithOkHttpClient.fromEnv();
    ExecutorService executor = Executors.newSingleThreadExecutor();

    try {
      List<Map<String, String>> messages =
          Arrays.asList(
              message("system", "You are a helpful assistant."),
              message("user", "I'd like to book a table for two."));

      Map<String, Object> metadata = new HashMap<>();
      metadata.put("ls_provider", "my_provider");
      metadata.put("ls_model_name", "my_model");

      Function<List<Map<String, String>>, Map<String, Object>> chatModel =
          Tracing.traceFunction(
              inputMessages -> output(),
              TraceConfig.builder()
                  .name("chat_model")
                  .runType(RunType.LLM)
                  .client(langsmith)
                  .executor(executor)
                  .metadata(metadata)
                  .build());

      chatModel.apply(messages);
    } finally {
      executor.shutdown();
      if (!executor.awaitTermination(10, TimeUnit.SECONDS)) {
        throw new IllegalStateException("Timed out waiting for LangSmith traces to submit");
      }
    }
  }

  private static Map<String, Object> output() {
    Map<String, Object> output = new HashMap<>();
    Map<String, Object> choice = new HashMap<>();
    choice.put(
        "message",
        message("assistant", "Sure, what time would you like to book the table for?"));
    output.put("choices", Arrays.asList(choice));

    Map<String, Object> inputTokenDetails = new HashMap<>();
    inputTokenDetails.put("cache_read", 10);

    Map<String, Object> usageMetadata = new HashMap<>();
    usageMetadata.put("input_tokens", 27);
    usageMetadata.put("output_tokens", 13);
    usageMetadata.put("total_tokens", 40);
    usageMetadata.put("input_token_details", inputTokenDetails);
    output.put("usage_metadata", usageMetadata);
    return output;
  }

  private static Map<String, String> message(String role, String content) {
    Map<String, String> message = new HashMap<>();
    message.put("role", role);
    message.put("content", content);
    return message;
  }
}
// :snippet-end:
