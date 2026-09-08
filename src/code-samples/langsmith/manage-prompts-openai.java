///usr/bin/env jbang "$0" "$@" ; exit $?
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.4
//DEPS com.openai:openai-java:4.30.0

// :snippet-start: manage-prompts-openai-java
// :codegroup-tab: Java
import static com.langchain.smith.prompts.PromptConverters.convertToOpenAIParams;
import com.langchain.smith.client.LangsmithClient;
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient;
import com.langchain.smith.prompts.Prompt;
import com.langchain.smith.prompts.PromptClient;
import com.langchain.smith.prompts.PromptValue;
import com.openai.client.OpenAIClient;
import com.openai.client.okhttp.OpenAIOkHttpClient;
import com.openai.models.ChatModel;
import com.openai.models.chat.completions.ChatCompletion;
import java.util.Map;

// :remove-start:
class ManagePromptsOpenAI {
  public static void main(String[] args) {
    if (System.getenv("LANGSMITH_API_KEY") == null
        || System.getenv("LANGSMITH_API_KEY").isBlank()
        || System.getenv("OPENAI_API_KEY") == null
        || System.getenv("OPENAI_API_KEY").isBlank()) {
      System.out.println(
          "[manage-prompts-openai] Skipping (LANGSMITH_API_KEY and OPENAI_API_KEY required).");
      return;
    }
// :remove-end:
LangsmithClient client = LangsmithOkHttpClient.fromEnv();
PromptClient promptClient = PromptClient.create(client);
OpenAIClient openai = OpenAIOkHttpClient.fromEnv();

Prompt prompt = promptClient.pull("jacob/joke-generator");
PromptValue formattedPrompt = prompt.invoke(Map.of("topic", "cats"));

ChatCompletion completion = openai.chat().completions().create(
    convertToOpenAIParams(formattedPrompt)
        .model(ChatModel.GPT_4_1_MINI)
        .build()
);
// :remove-start:
    System.out.println("[manage-prompts-openai] Done.");
  }
}
// :remove-end:
// :snippet-end:
