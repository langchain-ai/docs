// :remove-start:
import { Command } from "@langchain/langgraph";
// :remove-end:

// :snippet-start: langgraph-graph-api-send-command-command-parent-shape-js
const myNode = (state: { foo: string }) => {
  return new Command({
    update: { foo: "bar" },
    goto: "otherSubgraph", // node in the parent graph
    graph: Command.PARENT,
  });
};
// :snippet-end:

// :remove-start:
const parentShapeResult = myNode({ foo: "" });
if (
  parentShapeResult.graph !== Command.PARENT ||
  !parentShapeResult.goto?.includes("otherSubgraph")
) {
  throw new Error(`Unexpected Command: ${JSON.stringify(parentShapeResult)}`);
}
console.log("✓ langgraph-graph-api-send-command-command-parent-shape-js");
// :remove-end:
