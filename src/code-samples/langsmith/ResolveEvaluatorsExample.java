///usr/bin/env jbang "$0" "$@" ; exit $?
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.26

// :snippet-start: resolve-evaluators-java
// :codegroup-tab: Java
import com.langchain.smith.address.EvaluatorAddress;
import com.langchain.smith.client.LangsmithClient;
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient;
import com.langchain.smith.models.runs.RunQueryV2Params;
import java.time.OffsetDateTime;
// :remove-start:
import com.langchain.smith.models.sessions.SessionCreateParams;
// :remove-end:

public class ResolveEvaluatorsExample {
  public static void main(String[] args) {
    LangsmithClient client = LangsmithOkHttpClient.fromEnv();
    EvaluatorAddress evaluators = new EvaluatorAddress();
    // :remove-start:
    // Evaluator traces go to the workspace's project named "evaluators".
    client.sessions().create(SessionCreateParams.builder().name("evaluators").upsert(true).build());
    // :remove-end:

    String projectId = client.sessions().resolve(evaluators.toApiAddress()).sessionId();

    client
        .runs()
        .queryV2(
            RunQueryV2Params.builder()
                .addProjectId(projectId)
                .minStartTime(OffsetDateTime.now().minusMonths(1))
                .build())
        .items()
        .forEach(run -> System.out.println(run.id().get()));
    // :remove-start:
    System.out.println("✓ resolve-evaluators validated");
    // :remove-end:
  }
}
// :snippet-end:
