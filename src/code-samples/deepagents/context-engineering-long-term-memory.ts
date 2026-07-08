// :snippet-start: context-engineering-long-term-memory-js
import {
  CompositeBackend,
  createDeepAgent,
  StateBackend,
  StoreBackend,
} from "deepagents";
import { InMemoryStore } from "@langchain/langgraph-checkpoint";

const agent = await createDeepAgent({
  model: "google-genai:gemini-3.5-flash",
  store: new InMemoryStore(),
  backend: new CompositeBackend(new StateBackend(), {
    "/memories/": new StoreBackend(),
  }),
  systemPrompt: `When users tell you their preferences, save them to /memories/user_preferences.txt so you remember them in future conversations.`,
});
// :snippet-end:

// :remove-start:
const result = await agent.invoke({
  messages: [
    {
      role: "user",
      content: "Remember that I prefer concise responses.",
    },
  ],
});
const preferencesPath = "/memories/user_preferences.txt";
const preferencesFile = result.files?.[preferencesPath];
const fileContent =
  preferencesFile &&
  typeof preferencesFile === "object" &&
  "content" in preferencesFile
    ? String(preferencesFile.content)
    : "";

if (!fileContent.toLowerCase().includes("concise")) {
  throw new Error(
    `expected ${preferencesPath} to contain "concise", got: ${fileContent || "(missing file)"}`,
  );
}

console.log("✓ context-engineering-long-term-memory sample validated");
// :remove-end:
