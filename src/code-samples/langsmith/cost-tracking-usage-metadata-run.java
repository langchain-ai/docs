///usr/bin/env jbang "$0" "$@" ; exit $?
//DEPS com.langchain.smith:langsmith-java:0.1.0-alpha.25

// :snippet-start: cost-tracking-usage-metadata-run-java
// :codegroup-tab: Java
// :codegroup-fence-mods: expandable wrap
import com.langchain.smith.client.LangsmithClient;
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient;
import com.langchain.smith.tracing.RunTree;
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

class CostTrackingUsageMetadataRun {
  public static void main(String[] args) throws InterruptedException {
    if (System.getenv("LANGSMITH_API_KEY") == null
        || System.getenv("LANGSMITH_API_KEY").isBlank()) {
      System.out.println(
          "[cost-tracking-usage-metadata-run] Skipping (LANGSMITH_API_KEY is not set).");
      return;
    }

    LangsmithClient langsmith = LangsmithOkHttpClient.fromEnv();
    ExecutorService executor = Executors.newSingleThreadExecutor();

    try {
      List<Map<String, String>> inputs =
          Arrays.asList(
              message("system", "You are a helpful assistant."),
              message("user", "I'd like to book a table for two."));

      Map<String, Object> metadata = new HashMap<>();
      metadata.put("ls_provider", "my_provider");
      metadata.put("ls_model_name", "my_model");

      Function<List<Map<String, String>>, Map<String, String>> chatModel =
          Tracing.traceFunction(
              messages -> {
                Map<String, String> assistantMessage =
                    message(
                        "assistant",
                        "Sure, what time would you like to book the table for?");

                Map<String, Object> inputTokenDetails = new HashMap<>();
                inputTokenDetails.put("cache_read", 10);

                Map<String, Object> tokenUsage = new HashMap<>();
                tokenUsage.put("input_tokens", 27);
                tokenUsage.put("output_tokens", 13);
                tokenUsage.put("total_tokens", 40);
                tokenUsage.put("input_token_details", inputTokenDetails);

                RunTree run = Tracing.getCurrentRunTree();
                if (run != null) {
                  run.getMetadata().put("usage_metadata", tokenUsage);
                }

                return assistantMessage;
              },
              TraceConfig.builder()
                  .name("chat_model")
                  .runType(RunType.LLM)
                  .client(langsmith)
                  .executor(executor)
                  .metadata(metadata)
                  .build());

      chatModel.apply(inputs);
    } finally {
      executor.shutdown();
      if (!executor.awaitTermination(10, TimeUnit.SECONDS)) {
        throw new IllegalStateException("Timed out waiting for LangSmith traces to submit");
      }
    }
  }

  private static Map<String, String> message(String role, String content) {
    Map<String, String> message = new HashMap<>();
    message.put("role", role);
    message.put("content", content);
    return message;
  }
}
// :snippet-end:
