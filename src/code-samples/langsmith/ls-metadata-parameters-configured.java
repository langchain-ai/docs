///usr/bin/env jbang "$0" "$@" ; exit $?
//DEPS com.langchain.smith:langsmith-java:0.1.0-alpha.25

// :snippet-start: ls-metadata-parameters-configured-java
// :codegroup-tab: Java
import com.langchain.smith.tracing.RunType;
import com.langchain.smith.tracing.TraceConfig;
import com.langchain.smith.tracing.Tracing;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Function;

// :remove-start:
class LsMetadataParametersConfigured {
  static String callLlm(List<Map<String, String>> messages) {
    return "example response";
  }

  public static void main(String[] args) {
    if (System.getenv("LANGSMITH_API_KEY") == null
        || System.getenv("LANGSMITH_API_KEY").isBlank()) {
      System.out.println(
          "[ls-metadata-parameters-configured] Skipping (LANGSMITH_API_KEY is not set).");
      return;
    }
// :remove-end:
Map<String, Object> metadata = new HashMap<>();
metadata.put("ls_provider", "openai");
metadata.put("ls_model_name", "gpt-5.4");
metadata.put("ls_temperature", 0.7);
metadata.put("ls_max_tokens", 4096);
metadata.put("ls_stop", Collections.singletonList("END"));

Map<String, Object> invocationParams = new HashMap<>();
invocationParams.put("top_p", 0.9);
invocationParams.put("frequency_penalty", 0.5);
metadata.put("ls_invocation_params", invocationParams);

Function<List<Map<String, String>>, String> myConfiguredLlm =
    Tracing.traceFunction(
        messages -> callLlm(messages),
        TraceConfig.builder()
            .runType(RunType.LLM)
            .metadata(metadata)
            .build());

// :remove-start:
    System.out.println(
        myConfiguredLlm.apply(
            List.of(Map.of("role", "user", "content", "Hello"))));
  }
}
// :remove-end:
// :snippet-end:
