///usr/bin/env jbang "$0" "$@" ; exit $?
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.4

// :snippet-start: manage-prompts-pull-java
// :codegroup-tab: Java
import com.langchain.smith.client.LangsmithClient;
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient;
// :remove-start:
import com.langchain.smith.core.JsonValue;
import com.langchain.smith.models.commits.CommitCreateParams;
import com.langchain.smith.models.commits.CommitWithLookups;
import com.langchain.smith.models.repos.RepoCreateParams;
import com.langchain.smith.models.repos.RepoDeleteParams;
// :remove-end:
import com.langchain.smith.prompts.Prompt;
import com.langchain.smith.prompts.PromptClient;
import com.langchain.smith.prompts.PromptValue;
// :remove-start:
import java.util.List;
// :remove-end:
import java.util.Map;

// :remove-start:
class ManagePromptsPull {

  /**
   * Ensures {@code joke-generator} exists with a single head commit (same manifest as the push
   * sample) so pulls below hit a known-good revision. Matches {@code manage-prompts-0-push.java}.
   */
  private static String seedJokeGeneratorForPullSample(LangsmithClient client) {
    try {
      client.repos()
          .delete(
              RepoDeleteParams.builder().owner("-").repo("joke-generator").build());
    } catch (Exception ignored) {
      // Prompt may not exist yet.
    }
    client.repos()
        .create(
            RepoCreateParams.builder().repoHandle("joke-generator").isPublic(false).build());
    Map<String, Object> manifest =
        Map.of(
            "lc", 1,
            "type", "constructor",
            "id", List.of("langchain_core", "prompts", "prompt", "PromptTemplate"),
            "kwargs",
                Map.of(
                    "template", "tell me a joke about {topic}",
                    "input_variables", List.of("topic")));
    return client
        .commits()
        .create(
            CommitCreateParams.builder()
                .owner("-")
                .repo("joke-generator")
                .manifest(JsonValue.from(manifest))
                .build())
        .commit()
        .flatMap(CommitWithLookups::commitHash)
        .orElseThrow(() -> new IllegalStateException("commit hash missing from create response"));
  }

  public static void main(String[] args) {
    if (System.getenv("LANGSMITH_API_KEY") == null
        || System.getenv("LANGSMITH_API_KEY").isBlank()) {
      System.out.println("[manage-prompts-pull] Skipping (LANGSMITH_API_KEY is not set).");
      return;
    }
    try {
// :remove-end:
LangsmithClient client = LangsmithOkHttpClient.fromEnv();
PromptClient promptClient = PromptClient.create(client);
// :remove-start:
final String demoPinnedCommitHash = ManagePromptsPull.seedJokeGeneratorForPullSample(client);
// :remove-end:

Prompt prompt = promptClient.pull("joke-generator");
PromptValue formattedPrompt = prompt.invoke(Map.of("topic", "cats"));
// Use formattedPrompt with your model provider — see "Use a prompt without LangChain" below.
// :snippet-end:

// :snippet-start: manage-prompts-pull-commit-java
// :codegroup-tab: Java
String commitHash = "12344e88";
// :remove-start:
// Pin the commit created in seedJokeGeneratorForPullSample (see manage-prompts-0-push.java).
commitHash = demoPinnedCommitHash;
// :remove-end:
Prompt promptAtCommit = promptClient.pull("joke-generator:" + commitHash);
// :snippet-end:

// :snippet-start: manage-prompts-pull-public-java
// :codegroup-tab: Java
Prompt publicPrompt = promptClient.pull("efriis/my-first-prompt");
// :remove-start:
      System.out.println("[manage-prompts-pull] Done.");
    } catch (Exception e) {
      System.out.println("[manage-prompts-pull] Skipping (" + e.getMessage() + ").");
    }
  }
}
// :remove-end:
// :snippet-end:
