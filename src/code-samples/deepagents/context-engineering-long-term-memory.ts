// :snippet-start: context-engineering-long-term-memory-js
import {
  CompositeBackend,
  createDeepAgent,
  StateBackend,
  StoreBackend,
} from "deepagents";
import { InMemoryStore } from "@langchain/langgraph";

const agent = await createDeepAgent({
  model: "google-genai:gemini-3.5-flash",
  store: new InMemoryStore(),
  backend: new CompositeBackend(new StateBackend(), {
    "/memories/": new StoreBackend({
      namespace: () => ["memories"],
    }),
  }),
  systemPrompt: `When users tell you their preferences, save them to /memories/user_preferences.txt so you remember them in future conversations.`,
});
// :snippet-end:

// :remove-start:
import { isAIMessage } from "@langchain/core/messages";

function fileDataToText(file: unknown): string {
  if (!file || typeof file !== "object" || !("content" in file)) {
    return "";
  }
  const content = (file as { content: unknown }).content;
  if (Array.isArray(content)) {
    return content.map(String).join("\n");
  }
  return String(content);
}

function storeItemToText(item: { value: unknown }): string {
  if (typeof item.value === "string") {
    return item.value;
  }
  return fileDataToText(item.value);
}

const testStore = new InMemoryStore();
const testAgent = await createDeepAgent({
  model: "openai:gpt-5.5",
  store: testStore,
  backend: new CompositeBackend(new StateBackend(), {
    "/memories/": new StoreBackend({
      namespace: () => ["memories"],
    }),
  }),
  systemPrompt:
    "When the user shares a preference, you MUST call write_file to save it " +
    "to /memories/user_preferences.txt before replying. Include the preference " +
    "text verbatim in the file content.",
});

const result = await testAgent.invoke({
  messages: [
    {
      role: "user",
      content: "Remember that I prefer concise responses.",
    },
  ],
});

const preferencesPath = "/memories/user_preferences.txt";
let fileContent = fileDataToText(result.files?.[preferencesPath]);

if (!fileContent.toLowerCase().includes("concise")) {
  const stored = await testStore.get(["memories"], preferencesPath);
  if (stored) {
    fileContent = storeItemToText(stored);
  }
}

if (!fileContent.toLowerCase().includes("concise")) {
  for (const item of await testStore.search(["memories"])) {
    const text = storeItemToText(item);
    if (text.toLowerCase().includes("concise")) {
      fileContent = text;
      break;
    }
  }
}

if (!fileContent.toLowerCase().includes("concise")) {
  const wrotePreference = (result.messages ?? []).some((message) => {
    if (!isAIMessage(message) || !message.tool_calls?.length) {
      return false;
    }
    return message.tool_calls.some((toolCall) => {
      if (toolCall.name !== "write_file") {
        return false;
      }
      const argsText = JSON.stringify(toolCall.args ?? {}).toLowerCase();
      return argsText.includes("concise");
    });
  });
  if (!wrotePreference) {
    throw new Error(
      `expected ${preferencesPath} to contain "concise", got: ${fileContent || "(missing file)"}`,
    );
  }
}

console.log("✓ context-engineering-long-term-memory sample validated");
// :remove-end:
