// :remove-start:
console.log("✓ acp-start-server sample validated");
process.exit(0);
// :remove-end:

// :snippet-start: acp-start-server-js
// :codegroup-fence-mods: icon="server"
import { startServer } from "deepagents-acp";

await startServer({
  agents: {
    name: "coding-assistant",
    description: "AI coding assistant with filesystem access",
  },
  workspaceRoot: process.cwd(),
});
// :snippet-end:
