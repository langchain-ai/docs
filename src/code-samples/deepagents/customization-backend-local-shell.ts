// :snippet-start: backend-local-shell-js
import { createDeepAgent, LocalShellBackend } from "deepagents";

const backend = new LocalShellBackend({ workingDirectory: "." });
// KEEP MODEL
const agent = createDeepAgent({
  model: "google_genai:gemini-3.1-pro-preview",
  backend,
});
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
// :remove-end:
