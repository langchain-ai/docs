///usr/bin/env jbang "$0" "$@" ; exit $?
//DEPS com.langchain.smith:langsmith-java:0.1.0-alpha.25

// :snippet-start: ls-metadata-parameters-basic-java
// :codegroup-tab: Java
import com.langchain.smith.tracing.RunType;
import com.langchain.smith.tracing.TraceConfig;
import com.langchain.smith.tracing.Tracing;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Function;

// :remove-start:
class LsMetadataParametersBasic {
  static String callCustomApi(String prompt) {
    return "example response";
  }

  public static void main(String[] args) {
    if (System.getenv("LANGSMITH_API_KEY") == null
        || System.getenv("LANGSMITH_API_KEY").isBlank()) {
      System.out.println(
          "[ls-metadata-parameters-basic] Skipping (LANGSMITH_API_KEY is not set).");
      return;
    }
// :remove-end:
Map<String, Object> metadata = new HashMap<>();
metadata.put("ls_provider", "my_provider");
metadata.put("ls_model_name", "my_custom_model");

Function<String, String> myCustomLlm =
    Tracing.traceFunction(
        prompt -> callCustomApi(prompt),
        TraceConfig.builder()
            .runType(RunType.LLM)
            .metadata(metadata)
            .build());

// :remove-start:
    System.out.println(myCustomLlm.apply("hello"));
  }
}
// :remove-end:
// :snippet-end:
