// :snippet-start: langgraph-functional-api-interrupt-stream-js
import { MemorySaver, entrypoint, interrupt, task } from "@langchain/langgraph";

const writeEssay = task("writeEssay", async (topic: string) => {
  // This is a placeholder for a long-running task.
  await new Promise((resolve) => setTimeout(resolve, 1000));
  return `An essay about topic: ${topic}`;
});

const workflow = entrypoint(
  { checkpointer: new MemorySaver(), name: "workflow" },
  async (topic: string) => {
    const essay = await writeEssay(topic);
    const isApproved = interrupt({
      // Any json-serializable payload provided to interrupt as argument.
      // It will be surfaced on the client side as an Interrupt when streaming data
      // from the workflow.
      essay, // The essay to review.
      // You can add any additional information that you need.
      // For example, introduce a key called "action" with some instructions.
      action: "Please approve/reject the essay",
    });

    return {
      essay, // The essay that was generated
      isApproved, // Response from human review
    };
  },
);

const threadId = "functional-api-thread";
const config = {
  configurable: {
    thread_id: threadId,
  },
};

const stream = await workflow.streamEvents("cat", { ...config, version: "v3" });
const initialChunks: Record<string, unknown>[] = [];
for await (const snapshot of stream.values) {
  console.log(snapshot);
  if (snapshot && typeof snapshot === "object") {
    initialChunks.push(snapshot as Record<string, unknown>);
  }
}
// { __interrupt__: [Interrupt({ value: { essay: "An essay about topic: cat", ... } })] }
// :snippet-end:

// :snippet-start: langgraph-functional-api-interrupt-resume-js
import { Command } from "@langchain/langgraph";

// Get review from a user (e.g., via a UI)
// In this case, we're using a bool, but this can be any json-serializable value.
const humanReview = true;

const resumedStream = await workflow.streamEvents(
  new Command({ resume: humanReview }),
  { ...config, version: "v3" },
);
const resumedChunks: Record<string, unknown>[] = [];
for await (const snapshot of resumedStream.values) {
  console.log(snapshot);
  if (snapshot && typeof snapshot === "object") {
    resumedChunks.push(snapshot as Record<string, unknown>);
  }
}
// { essay: "An essay about topic: cat", isApproved: true }
// :snippet-end:

// :remove-start:
const sawInterrupt = initialChunks.some((chunk) => "__interrupt__" in chunk);
if (!sawInterrupt) {
  throw new Error(
    `Expected interrupt chunk, got ${JSON.stringify(initialChunks)}`,
  );
}
const interruptChunk = initialChunks.find((chunk) => "__interrupt__" in chunk);
const interrupts = interruptChunk?.__interrupt__;
const essay =
  Array.isArray(interrupts) &&
  interrupts[0] &&
  typeof interrupts[0] === "object" &&
  interrupts[0] !== null &&
  "value" in interrupts[0]
    ? (interrupts[0] as { value?: { essay?: string } }).value?.essay
    : undefined;
if (essay !== "An essay about topic: cat") {
  throw new Error(
    `Expected essay in interrupt value, got ${JSON.stringify(initialChunks)}`,
  );
}

const sawApproved = resumedChunks.some((chunk) => {
  if (chunk.isApproved === true) {
    return true;
  }
  if (
    "workflow" in chunk &&
    typeof chunk.workflow === "object" &&
    chunk.workflow !== null &&
    "isApproved" in chunk.workflow
  ) {
    return (chunk.workflow as { isApproved?: unknown }).isApproved === true;
  }
  return false;
});
if (!sawApproved) {
  throw new Error(
    `Expected isApproved=true, got ${JSON.stringify(resumedChunks)}`,
  );
}
console.log("✓ langgraph-functional-api-interrupt-stream-js");
// :remove-end:
