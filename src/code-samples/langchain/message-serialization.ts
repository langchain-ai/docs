// :snippet-start: message-serialization-js
import { HumanMessage } from "@langchain/core/messages";
import { load } from "@langchain/core/load";

const message = new HumanMessage("What is the capital of France?");

// Serialize to a plain object
const serialized = message.toJSON();

// Deserialize back to a message object
const restored = await load<HumanMessage>(JSON.stringify(serialized));
// :snippet-end:

// :remove-start:
async function main() {
  if (typeof serialized !== "object" || serialized === null) {
    throw new Error(`Expected plain object, got ${typeof serialized}`);
  }
  if (!(restored instanceof HumanMessage)) {
    throw new Error(`Expected HumanMessage, got ${restored?.constructor?.name}`);
  }
  if (restored.content !== message.content) {
    throw new Error(
      `Expected content "${message.content}", got "${restored.content}"`,
    );
  }
  console.log("✓ Message serialization round-trip works");
}
main();
// :remove-end:
