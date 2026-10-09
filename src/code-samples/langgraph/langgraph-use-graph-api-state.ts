// :snippet-start: langgraph-use-graph-api-state-js
import { StateSchema, ReducedValue } from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  foo: z.number(),
  bar: new ReducedValue(
    z.array(z.string()).default(() => []),
    { reducer: (left, right) => left.concat(right) }
  ),
});
// :snippet-end:

// :remove-start:
if (!State) throw new Error("State not created");
console.log("✓ langgraph-use-graph-api-state-js validated");
// :remove-end:
