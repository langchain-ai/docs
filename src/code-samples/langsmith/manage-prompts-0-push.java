///usr/bin/env jbang "$0" "$@" ; exit $?
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.4

// :snippet-start: manage-prompts-push-java
// :codegroup-tab: Java
import com.langchain.smith.client.LangsmithClient;
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient;
import com.langchain.smith.core.JsonValue;
import com.langchain.smith.models.commits.CommitCreateParams;
import com.langchain.smith.models.repos.RepoCreateParams;
import java.util.List;
import java.util.Map;

// :remove-start:
class ManagePromptsPush {
  public static void main(String[] args) {
    if (System.getenv("LANGSMITH_API_KEY") == null
        || System.getenv("LANGSMITH_API_KEY").isBlank()) {
      throw new IllegalStateException("LANGSMITH_API_KEY must be set to run this sample.");
    }
    try {
// :remove-end:
LangsmithClient client = LangsmithOkHttpClient.fromEnv();

// :remove-start:
      try {
        client.repos().delete(
            com.langchain.smith.models.repos.RepoDeleteParams.builder()
                .owner("-")
                .repo("joke-generator")
                .build()
        );
      } catch (Exception ignored) {
        // Prompt may not exist yet.
      }
// :remove-end:

client.repos().create(
    RepoCreateParams.builder()
        .repoHandle("joke-generator")
        .isPublic(false)
        .build()
);

Map<String, Object> manifest = Map.of(
    "lc", 1,
    "type", "constructor",
    "id", List.of("langchain_core", "prompts", "prompt", "PromptTemplate"),
    "kwargs", Map.of(
        "template", "tell me a joke about {topic}",
        "input_variables", List.of("topic")
    )
);

client.commits().create(
    CommitCreateParams.builder()
        .owner("-")
        .repo("joke-generator")
        .manifest(JsonValue.from(manifest))
        .build()
);
// :remove-start:
      client.repos().delete(
          com.langchain.smith.models.repos.RepoDeleteParams.builder()
              .owner("-")
              .repo("joke-generator")
              .build()
      );
      System.out.println("[manage-prompts-push] Done.");
    } catch (Exception e) {
      System.out.println("[manage-prompts-push] Skipping (" + e.getMessage() + ").");
    }
  }
}
// :remove-end:
// :snippet-end:
