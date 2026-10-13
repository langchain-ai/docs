///usr/bin/env jbang "$0" "$@" ; exit $?
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.26

// :snippet-start: trace-agent-java
// :codegroup-tab: Java
import com.langchain.smith.address.AgentAddress;
import com.langchain.smith.tracing.TraceConfig;
import com.langchain.smith.tracing.Tracing;
import java.util.Map;
import java.util.function.Function;

public class TraceAgentExample {
  public static void main(String[] args) {
    Function<String, Map<String, String>> handleOrder =
        Tracing.traceFunction(
            orderId -> Map.of("order_id", orderId, "status", "charged"),
            TraceConfig.builder()
                .name("handle_order")
                .address(new AgentAddress("checkout", "production"))
                .build());

    handleOrder.apply("A-1");
    // :remove-start:
    System.out.println("✓ trace-agent validated");
    // :remove-end:
  }
}
// :snippet-end:
