// :snippet-start: langgraph-functional-api-overview-essay-js
import { MemorySaver, entrypoint, task, interrupt } from "@langchain/langgraph";

const writeEssay = task("writeEssay", async (topic: string) => {
  // Placeholder for a long-running task.
  await new Promise((resolve) => setTimeout(resolve, 1000));
  return `An essay about topic: ${topic}`;
});

const workflow = entrypoint(
  { checkpointer: new MemorySaver(), name: "workflow" },
  async (topic: string) => {
    const essay = await writeEssay(topic);
    const isApproved = interrupt({
      // Any JSON-serializable payload. Surfaces as an Interrupt when streaming.
      essay,
      action: "Please approve/reject the essay",
    });

    return {
      essay,
      isApproved,
    };
  }
);
// :snippet-end:

// :remove-start:
import { Command } from "@langchain/langgraph";

const essayConfig = { configurable: { thread_id: "essay-1" } };
const paused = await workflow.invoke("cat", essayConfig);
const interrupts = (paused as { __interrupt__?: { value?: { essay?: string } }[] })
  .__interrupt__;
if (interrupts?.[0]?.value?.essay !== "An essay about topic: cat") {
  throw new Error(`expected interrupt with essay, got ${JSON.stringify(paused)}`);
}
const resumed = await workflow.invoke(new Command({ resume: true }), essayConfig);
if (
  JSON.stringify(resumed) !==
  JSON.stringify({ essay: "An essay about topic: cat", isApproved: true })
) {
  throw new Error(`unexpected resume result: ${JSON.stringify(resumed)}`);
}
console.log("✓ langgraph-functional-api-overview-essay");
// :remove-end:
