///usr/bin/env jbang "$0" "$@" ; exit $?
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.26

// :snippet-start: resolve-agent-java
// :codegroup-tab: Java
import com.langchain.smith.address.AgentAddress;
import com.langchain.smith.client.LangsmithClient;
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient;
import com.langchain.smith.models.runs.RunQueryV2Params;
import java.time.OffsetDateTime;
// :remove-start:
import com.langchain.smith.tracing.TraceConfig;
import com.langchain.smith.tracing.Tracing;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
// :remove-end:

public class ResolveAgentExample {
  public static void main(String[] args) throws Exception {
    LangsmithClient client = LangsmithOkHttpClient.fromEnv();
    AgentAddress agent = new AgentAddress("checkout", "production");
    // :remove-start:
    AgentSeeder.seed(client, agent);
    // :remove-end:

    String projectId = client.sessions().resolve(agent.toApiAddress()).sessionId();

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
    System.out.println("✓ resolve-agent validated");
    // :remove-end:
  }
}
// :snippet-end:

// :remove-start:
class AgentSeeder {
  // An agent exists once it has received a trace, and ingestion is asynchronous.
  static void seed(LangsmithClient client, AgentAddress agent) throws Exception {
    ExecutorService executor = Executors.newSingleThreadExecutor();
    TraceConfig config =
        TraceConfig.builder()
            .client(client)
            .executor(executor)
            .name("docs-resolve-an-agent-seed")
            .address(agent)
            .tracingEnabled(true)
            .build();
    Tracing.traceFunction((String input) -> input, config).apply("seed");
    executor.shutdown();
    executor.awaitTermination(30, TimeUnit.SECONDS);
    client.runs().flush();

    long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(120);
    while (true) {
      try {
        client.sessions().resolve(agent.toApiAddress());
        return;
      } catch (RuntimeException e) {
        if (System.nanoTime() > deadline) {
          throw e;
        }
        Thread.sleep(3000);
      }
    }
  }
}
// :remove-end:
