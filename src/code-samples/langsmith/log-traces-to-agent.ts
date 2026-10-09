// :snippet-start: trace-agent-js
import { AgentAddress } from "langsmith";
import { traceable } from "langsmith/traceable";

const handleOrder = traceable(
  async (orderId: string) => ({ orderId, status: "charged" }),
  { name: "handle_order", address: new AgentAddress("checkout", "production") },
);
// :snippet-end:

// :remove-start:
const result = await handleOrder("A-1");
if (result.status !== "charged") {
  throw new Error(`unexpected result: ${JSON.stringify(result)}`);
}
console.log("✓ trace-agent validated");
// :remove-end:
