import { InMemoryStore } from "@langchain/langgraph";

const store = new InMemoryStore();

// Seed some data
await store.put(["alice", "memories"], "mem-1", { text: "Likes hiking" });
await store.put(["alice", "memories"], "mem-2", { text: "Dislikes loud music" });

// :snippet-start: store-list-namespace-search-js
// Return up to 100 items stored under ["alice", "memories"].
const items = await store.search(["alice", "memories"], { limit: 100 });
// :snippet-end:

// :snippet-start: store-list-namespace-paginate-js
const pageSize = 50;
let offset = 0;
while (true) {
  const page = await store.search(["alice", "memories"], { limit: pageSize, offset });
  if (page.length === 0) break;
  for (const item of page) {
    // ...
  }
  offset += pageSize;
}
// :snippet-end:

// :snippet-start: store-list-namespace-list-js
// All namespaces that start with ["alice"], truncated to two levels deep.
const namespaces = await store.listNamespaces({ prefix: ["alice"], maxDepth: 2 });
// :snippet-end:

// :remove-start:
async function main() {
  if (items.length !== 2) {
    throw new Error(`Expected 2 items, got ${items.length}`);
  }
  if (namespaces.length !== 1 || namespaces[0].join(",") !== "alice,memories") {
    throw new Error(`Unexpected namespaces: ${JSON.stringify(namespaces)}`);
  }
  console.log("✓ store list-namespace operations work correctly");
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => {
    console.error(error);
    process.exit(1);
  });
}
// :remove-end:
