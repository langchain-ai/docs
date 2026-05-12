///usr/bin/env jbang "$0" "$@" ; exit $?
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.4

// :snippet-start: manage-prompts-pull-java
// :codegroup-tab: Java
import com.langchain.smith.client.LangsmithClient;
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient;
import com.langchain.smith.prompts.Prompt;
import com.langchain.smith.prompts.PromptClient;
import com.langchain.smith.prompts.PromptValue;
import java.util.Map;

// :remove-start:
class ManagePromptsPull {
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

Prompt prompt = promptClient.pull("joke-generator");
PromptValue formattedPrompt = prompt.invoke(Map.of("topic", "cats"));
// Use formattedPrompt with your model provider — see "Use a prompt without LangChain" below.
// :snippet-end:

// :snippet-start: manage-prompts-pull-commit-java
// :codegroup-tab: Java
Prompt promptAtCommit = promptClient.pull("joke-generator:12344e88");
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
