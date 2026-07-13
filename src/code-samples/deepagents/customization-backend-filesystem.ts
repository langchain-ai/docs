// :snippet-start: backend-filesystem-js
import { createDeepAgent, FilesystemBackend } from "deepagents";

const agent = createDeepAgent({
  model: "openai:gpt-5.5",
  backend: new FilesystemBackend({ rootDir: ".", virtualMode: true }),
});
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
// :remove-end:
