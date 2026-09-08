// :snippet-start: langgraph-functional-api-interrupt-stream-js
import { MemorySaver, entrypoint, interrupt, task } from "@langchain/langgraph";

const writeEssay = task("writeEssay", async (topic: string) => {
  // This is a placeholder for a long-running task.
  await new Promise((resolve) => setTimeout(resolve, 1000));
  return `An essay about topic: ${topic}`;
});

const workflow = entrypoint(
  { checkpointer: new MemorySaver(), name: "workflow" },
  async (_topic: string) => {
    const essay = await writeEssay("cat");
    const isApproved = interrupt({
      // Any json-serializable payload provided to interrupt as argument.
      // It will be surfaced on the client side as an Interrupt when streaming data
      // from the workflow.
      essay, // The essay we want reviewed.
      // We can add any additional information that we need.
      // For example, introduce a key called "action" with some instructions.
      action: "Please approve/reject the essay",
    });

    return {
      essay, // The essay that was generated
      isApproved, // Response from HIL
    };
  },
);

const threadId = "functional-api-thread";
const config = {
  configurable: {
    thread_id: threadId,
  },
};

const stream = await workflow.streamEvents("cat", { ...config, version: "v2" });
const initialChunks: Record<string, unknown>[] = [];
for await (const event of stream) {
  const chunk = event.data?.chunk;
  if (chunk && typeof chunk === "object") {
    console.log(chunk);
    initialChunks.push(chunk as Record<string, unknown>);
  }
}
// { writeEssay: "An essay about topic: cat" }
// { __interrupt__: [Interrupt(...)] }
// :snippet-end:

// :snippet-start: langgraph-functional-api-interrupt-resume-js
import { Command } from "@langchain/langgraph";

// Get review from a user (e.g., via a UI)
// In this case, we're using a bool, but this can be any json-serializable value.
const humanReview = true;

const resumedStream = await workflow.streamEvents(
  new Command({ resume: humanReview }),
  { ...config, version: "v2" },
);
const resumedChunks: Record<string, unknown>[] = [];
for await (const event of resumedStream) {
  const chunk = event.data?.chunk;
  if (chunk && typeof chunk === "object") {
    console.log(chunk);
    resumedChunks.push(chunk as Record<string, unknown>);
  }
}
// { essay: "An essay about topic: cat", isApproved: true }
// :snippet-end:

// :remove-start:
const sawWriteEssay = initialChunks.some(
  (chunk) => "writeEssay" in chunk || "write_essay" in chunk,
);
if (!sawWriteEssay) {
  throw new Error(
    `Expected writeEssay chunk, got ${JSON.stringify(initialChunks)}`,
  );
}
const sawInterrupt = initialChunks.some((chunk) => "__interrupt__" in chunk);
if (!sawInterrupt) {
  throw new Error(
    `Expected interrupt chunk, got ${JSON.stringify(initialChunks)}`,
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
