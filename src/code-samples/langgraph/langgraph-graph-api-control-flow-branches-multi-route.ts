// :remove-start:
import {
  ConditionalEdgeRouter,
  ReducedValue,
  StateSchema,
} from "@langchain/langgraph";
import * as z from "zod";

const State = new StateSchema({
  aggregate: new ReducedValue(z.array(z.string()).default(() => []), {
    reducer: (x, y) => x.concat(y),
  }),
  which: z.string(),
});
// :remove-end:

// :snippet-start: langgraph-graph-api-control-flow-branches-multi-route-js
const routeBcOrCd: ConditionalEdgeRouter<{ InputSchema: typeof State; Nodes: "b" | "c" | "d" }> = (state) => {
  if (state.which === "cd") {
    return ["c", "d"];
  }
  return ["b", "c"];
};
// :snippet-end:

// :remove-start:
const cd = routeBcOrCd({ aggregate: [], which: "cd" });
const bc = routeBcOrCd({ aggregate: [], which: "bc" });
if (JSON.stringify(cd) !== '["c","d"]' || JSON.stringify(bc) !== '["b","c"]') {
  throw new Error(`Unexpected routes: ${JSON.stringify([cd, bc])}`);
}
console.log("✓ langgraph-graph-api-control-flow-branches-multi-route-js");
// :remove-end:
