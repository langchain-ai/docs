// :snippet-start: acp-custom-backend-js
import { DeepAgentsServer } from "deepagents-acp";
import { CompositeBackend, FilesystemBackend, StateBackend } from "deepagents";

const server = new DeepAgentsServer({
  agents: {
    name: "custom-agent",
    backend: new CompositeBackend(new StateBackend(), {
      "/workspace/": new FilesystemBackend({ rootDir: "./workspace" }),
    }),
  },
});
// :snippet-end:
// :remove-start:
if (!server) {
  throw new Error("server not created");
}
console.log("✓ acp-custom-backend sample validated");
process.exit(0);
// :remove-end:

await server.start();
