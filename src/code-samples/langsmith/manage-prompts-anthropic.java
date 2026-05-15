///usr/bin/env jbang "$0" "$@" ; exit $?
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.4
//DEPS com.anthropic:anthropic-java:2.31.0

// :snippet-start: manage-prompts-anthropic-java
// :codegroup-tab: Java
import static com.langchain.smith.prompts.PromptConverters.convertToAnthropicParams;
import com.anthropic.client.AnthropicClient;
import com.anthropic.client.okhttp.AnthropicOkHttpClient;
import com.anthropic.models.messages.Message;
import com.anthropic.models.messages.Model;
import com.langchain.smith.client.LangsmithClient;
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient;
import com.langchain.smith.prompts.Prompt;
import com.langchain.smith.prompts.PromptClient;
import com.langchain.smith.prompts.PromptValue;
import java.util.Map;

// :remove-start:
class ManagePromptsAnthropic {
  public static void main(String[] args) {
    if (System.getenv("LANGSMITH_API_KEY") == null
        || System.getenv("LANGSMITH_API_KEY").isBlank()
        || System.getenv("ANTHROPIC_API_KEY") == null
        || System.getenv("ANTHROPIC_API_KEY").isBlank()) {
      System.out.println(
          "[manage-prompts-anthropic] Skipping (LANGSMITH_API_KEY and ANTHROPIC_API_KEY required).");
      return;
    }
    try {
// :remove-end:
LangsmithClient client = LangsmithOkHttpClient.fromEnv();
PromptClient promptClient = PromptClient.create(client);
AnthropicClient anthropic = AnthropicOkHttpClient.fromEnv();

Prompt prompt = promptClient.pull("jacob/joke-generator");
PromptValue formattedPrompt = prompt.invoke(Map.of("topic", "cats"));

Message message = anthropic.messages().create(
    convertToAnthropicParams(formattedPrompt)
        .model(Model.CLAUDE_SONNET_4_5)
        .maxTokens(1024)
        .build()
);
// :remove-start:
      System.out.println("[manage-prompts-anthropic] Done.");
    } catch (Exception e) {
      System.out.println("[manage-prompts-anthropic] Skipping (" + e.getMessage() + ").");
    }
  }
}
// :remove-end:
// :snippet-end:
