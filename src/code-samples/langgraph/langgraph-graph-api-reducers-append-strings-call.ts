// :snippet-start: langgraph-graph-api-reducers-append-strings-call-js
const reducer = (left: string[], right: string[]) => left.concat(right);

reducer(["draft"], ["review"]); // left, right → ["draft", "review"]
// :snippet-end:

// :remove-start:
const result = reducer(["draft"], ["review"]);
if (JSON.stringify(result) !== JSON.stringify(["draft", "review"])) {
  throw new Error(`Unexpected reducer result: ${JSON.stringify(result)}`);
}

console.log("✓ langgraph-graph-api-reducers-append-strings-call-js");
// :remove-end:
