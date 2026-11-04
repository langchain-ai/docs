// :remove-start:
import { RunControl } from "@langchain/langgraph";

// Context for the snippet below.
const doWork = async () => "done";
// :remove-end:

// :snippet-start: langgraph-graph-api-nodes-drain-js
import { StateSchema, type Runtime } from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  status: z.string(),
  reason: z.string().optional(),
});

const myNode = async (
  state: typeof State.State,
  runtime: Runtime<typeof State>
) => {
  if (runtime.control?.drainRequested) {  // [!code highlight]
    return { status: "skipped", reason: runtime.control.drainReason };
  }
  return { status: await doWork() };
};
// :snippet-end:

// :remove-start:
const idle = await myNode({ status: "" }, {} as Runtime<typeof State>);
if (idle.status !== "done") throw new Error(`Unexpected: ${JSON.stringify(idle)}`);

const control = new RunControl();
control.requestDrain("shutdown");
const drained = await myNode(
  { status: "" },
  { control } as unknown as Runtime<typeof State>
);
if (drained.status !== "skipped" || drained.reason !== "shutdown") {
  throw new Error(`Unexpected: ${JSON.stringify(drained)}`);
}
console.log("✓ langgraph-graph-api-nodes-drain-js validated");
// :remove-end:
