// :remove-start:
import {
  AgentAddress as SeedAgentAddress,
  Client as SeedClient,
} from "langsmith";
import { traceable } from "langsmith/traceable";

// An agent exists once it has received a trace, and ingestion is asynchronous.
async function seedAgent(
  seedClient: SeedClient,
  address: SeedAgentAddress,
  timeoutMs = 120_000,
): Promise<void> {
  const seed = traceable(async () => "ok", {
    name: "docs-resolve-an-agent-seed",
    client: seedClient,
    tracingEnabled: true,
    address,
  });
  await seed();
  await seedClient.awaitPendingTraceBatches();

  const deadline = Date.now() + timeoutMs;
  for (;;) {
    try {
      await seedClient.sessions.resolve(address.toApiAddress());
      return;
    } catch (error) {
      const status = (error as { status?: number }).status;
      if (status !== 404 || Date.now() > deadline) {
        throw error;
      }
      await new Promise((resolve) => setTimeout(resolve, 3000));
    }
  }
}
// :remove-end:

// :snippet-start: resolve-agent-js
import { AgentAddress, Client } from "langsmith";

const client = new Client();
const agent = new AgentAddress("checkout", "production");
// :remove-start:
await seedAgent(client, agent);
// :remove-end:

const project = await client.sessions.resolve(agent.toApiAddress());

for await (const run of client.runs.query({
  project_ids: [project.session_id],
})) {
  console.log(run.id);
}
// :snippet-end:

// :remove-start:
console.log("✓ resolve-agent validated");
// :remove-end:
