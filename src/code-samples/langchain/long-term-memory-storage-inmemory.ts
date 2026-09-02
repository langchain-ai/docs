// :snippet-start: long-term-memory-storage-inmemory-js
import { InMemoryStore } from "@langchain/langgraph";

const embed = (texts: string[]): number[][] => {
  // Replace with an actual embedding function or LangChain embeddings object
  return texts.map(() => [1.0, 2.0]);
};

// InMemoryStore saves data to an in-memory dictionary. Use a DB-backed store in production use.
const store = new InMemoryStore({ index: { embed, dims: 2 } });
const userId = "my-user";
const applicationContext = "chitchat";
const namespace = [userId, applicationContext];

await store.put(namespace, "a-memory", {
  rules: [
    "User likes short, direct language",
    "User only speaks English & TypeScript",
  ],
  "my-key": "my-value",
});

// get the "memory" by ID
const item = await store.get(namespace, "a-memory");

// search for "memories" within this namespace, filtering on content equivalence, sorted by vector similarity
const items = await store.search(namespace, {
  filter: { "my-key": "my-value" },
  query: "language preferences",
});
// :snippet-end:

// :remove-start:
async function main() {
  // Verify the operations work
  if (!item) {
    throw new Error("Item should not be null");
  }
  if (item.value["my-key"] !== "my-value") {
    throw new Error('Expected my-key to be "my-value"');
  }
  if (!item.value["rules"]) {
    throw new Error("Expected rules to exist");
  }
  if ((item.value["rules"] as string[]).length !== 2) {
    throw new Error("Expected 2 rules");
  }

  // Verify search returns results
  if (items.length === 0) {
    throw new Error("Expected search to return results");
  }
  if (items[0].value["my-key"] !== "my-value") {
    throw new Error('Expected search result my-key to be "my-value"');
  }

  console.log("✓ InMemoryStore operations work correctly");
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => {
    console.error(error);
    process.exit(1);
  });
}
// :remove-end:
