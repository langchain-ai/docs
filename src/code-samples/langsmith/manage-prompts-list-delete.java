///usr/bin/env jbang "$0" "$@" ; exit $?
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.4

// :snippet-start: manage-prompts-list-delete-java
// :codegroup-tab: Java
import com.langchain.smith.client.LangsmithClient;
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient;
import com.langchain.smith.models.repos.RepoDeleteParams;
import com.langchain.smith.models.repos.RepoListPage;
import com.langchain.smith.models.repos.RepoListParams;
import com.langchain.smith.models.repos.RepoWithLookups;

// :remove-start:
class ManagePromptsListDelete {
  public static void main(String[] args) {
    if (System.getenv("LANGSMITH_API_KEY") == null
        || System.getenv("LANGSMITH_API_KEY").isBlank()) {
      System.out.println(
          "[manage-prompts-list-delete] Skipping (LANGSMITH_API_KEY is not set).");
      return;
    }
    try {
// :remove-end:
LangsmithClient client = LangsmithOkHttpClient.fromEnv();

// List all prompts in my workspace
RepoListPage prompts = client.repos().list();
for (RepoWithLookups prompt : prompts.repos()) {
    System.out.println(prompt.repoHandle());
}

// List my private prompts that include "joke"
RepoListPage jokePrompts = client.repos().list(
    RepoListParams.builder()
        .query("joke")
        .isPublic(RepoListParams.IsPublic.FALSE)
        .build()
);

// Delete a prompt
client.repos().delete(
    RepoDeleteParams.builder()
        .owner("-")
        .repo("joke-generator")
        .build()
);
// :remove-start:
      System.out.println("[manage-prompts-list-delete] Done.");
    } catch (Exception e) {
      System.out.println("[manage-prompts-list-delete] Skipping (" + e.getMessage() + ").");
    }
  }
}
// :remove-end:
// :snippet-end:
