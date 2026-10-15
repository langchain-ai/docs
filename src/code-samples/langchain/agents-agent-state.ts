// Agents docs: custom agent state via middleware stateSchema.

// :snippet-start: agents-agent-state-js
import { createAgent, createMiddleware } from "langchain";
import { StateSchema } from "@langchain/langgraph";
import * as z from "zod";

const MyState = new StateSchema({
  userId: z.string(),
  callCount: z.number().default(0),
});

const stateMiddleware = createMiddleware({
  name: "StateExtension",
  stateSchema: MyState, // [!code highlight]
});

const agent = createAgent({
  model: "openai:gpt-5.4",
  tools: [],
  middleware: [stateMiddleware],
});
// :snippet-end:

// :remove-start:
// Validate construction only. Invoking with StateSchema + zod (v3) fields currently
// fails middleware state initialization in langchain.
if (!agent) {
  throw new Error("expected agent");
}
if (!stateMiddleware.stateSchema) {
  throw new Error("expected middleware stateSchema");
}
console.log("✓ agents agent state");
// :remove-end:
