// :snippet-start: backend-filesystem-js
import { createDeepAgent, FilesystemBackend } from "deepagents";

// KEEP MODEL
const agent = createDeepAgent({
  model: "google_genai:gemini-3.1-pro-preview",
  backend: new FilesystemBackend({ rootDir: ".", virtualMode: true }),
});
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
// :remove-end:
