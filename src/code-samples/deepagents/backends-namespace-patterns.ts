// :snippet-start: backends-namespace-patterns-js
import { StoreBackend } from "deepagents";

// Per-user: derive from the authenticated Agent Server user
const perUserBackend = new StoreBackend({
  namespace: ({ config }) => [String(config?.configurable?.langgraph_auth_user_id)],  // [!code highlight]
});

// Per-assistant: use the resolved assistant id
const perAssistantBackend = new StoreBackend({
  namespace: ({ assistantId }) => [assistantId ?? "default"],  // [!code highlight]
});

// Static namespace when the scope is known at construction time
const orgId = "acme";
const userId = "user-1";
const staticBackend = new StoreBackend({
  namespace: ["memories", orgId, userId, "filesystem"],  // [!code highlight]
});
// :snippet-end:

// :remove-start:
if (!perUserBackend || !perAssistantBackend || !staticBackend) {
  throw new Error("expected StoreBackend instances");
}
console.log("✓ backends-namespace-patterns validated");
// :remove-end:
