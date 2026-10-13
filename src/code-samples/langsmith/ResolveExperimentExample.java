///usr/bin/env jbang "$0" "$@" ; exit $?
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.26

// :snippet-start: resolve-experiment-java
// :codegroup-tab: Java
import com.langchain.smith.address.ExperimentAddress;
import com.langchain.smith.client.LangsmithClient;
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient;
import com.langchain.smith.models.runs.RunQueryV2Params;
import java.time.OffsetDateTime;
// :remove-start:
import com.langchain.smith.models.datasets.DatasetCreateParams;
import com.langchain.smith.models.sessions.SessionCreateParams;
import java.util.UUID;
// :remove-end:

public class ResolveExperimentExample {
  public static void main(String[] args) {
    LangsmithClient client = LangsmithOkHttpClient.fromEnv();
    String experimentId = "<experiment-id>";
    // :remove-start:
    var dataset =
        client
            .datasets()
            .create(
                DatasetCreateParams.builder()
                    .name("docs-resolve-an-agent-" + UUID.randomUUID().toString().substring(0, 8))
                    .build());
    var seeded =
        client
            .sessions()
            .create(
                SessionCreateParams.builder()
                    .name("docs-resolve-an-agent-" + UUID.randomUUID().toString().substring(0, 8))
                    .referenceDatasetId(dataset.id())
                    .build());
    experimentId = seeded.id();
    // :remove-end:
    ExperimentAddress experiment = new ExperimentAddress(experimentId);

    String projectId = client.sessions().resolve(experiment.toApiAddress()).sessionId();

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
    client.sessions().delete(experimentId);
    client.datasets().delete(dataset.id());
    System.out.println("✓ resolve-experiment validated");
    // :remove-end:
  }
}
// :snippet-end:
