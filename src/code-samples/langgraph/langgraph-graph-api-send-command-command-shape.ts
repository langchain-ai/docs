// :remove-start:
import { StateSchema } from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  foo: z.string(),
});
// :remove-end:

// :snippet-start: langgraph-graph-api-send-command-command-shape-js
import { Command } from "@langchain/langgraph";

const myNode = (state: typeof State.State) => {
  return new Command({
    // state update
    update: { foo: "bar" },
    // control flow
    goto: "myOtherNode",
  });
};
// :snippet-end:

// :remove-start:
const shapeResult = myNode({ foo: "" });
if (!(shapeResult instanceof Command)) {
  throw new Error("Expected a Command");
}
if (shapeResult.update?.foo !== "bar" || !shapeResult.goto?.includes("myOtherNode")) {
  throw new Error(`Unexpected Command: ${JSON.stringify(shapeResult)}`);
}
console.log("✓ langgraph-graph-api-send-command-command-shape-js");
// :remove-end:
