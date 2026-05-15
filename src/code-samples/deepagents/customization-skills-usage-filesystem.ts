// :snippet-start: skills-usage-filesystem-js
import { createCodeInterpreterMiddleware } from "@langchain/quickjs";
import { createDeepAgent, FilesystemBackend } from "deepagents";
import { MemorySaver } from "@langchain/langgraph";

const checkpointer = new MemorySaver();
const backend = new FilesystemBackend({ rootDir: process.cwd() });

// KEEP MODEL
const agent = await createDeepAgent({
  model: "google-genai:gemini-3.1-pro-preview",
  backend,
  skills: ["./examples/skills/"],
  interruptOn: {
    read_file: true,
    write_file: true,
    delete_file: true,
  },
  checkpointer, // Required!
  middleware: [createCodeInterpreterMiddleware({ skillsBackend: backend })],
});

const config = { configurable: { thread_id: `thread-${Date.now()}` } };
const result = await agent.invoke(
  { messages: [{ role: "user", content: "what is langraph?" }] },
  config,
);
// :snippet-end:

// :remove-start:
if (!agent) throw new Error("agent not created");
if (!result) throw new Error("result empty");
// :remove-end:
