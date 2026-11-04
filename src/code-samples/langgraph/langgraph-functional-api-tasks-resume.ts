// :snippet-start: langgraph-functional-api-tasks-resume-js
import { entrypoint, task, MemorySaver } from "@langchain/langgraph";

// Used only to simulate a transient failure. Do not use a variable like this in production.
let attempts = 0;
const called: string[] = [];

const getInfo = task("getInfo", async () => {
  called.push("getInfo");
  attempts += 1;

  if (attempts < 2) {
    throw new Error("Failure");
  }
  return "OK";
});

const checkpointer = new MemorySaver();

const slowTask = task("slowTask", async () => {
  called.push("slowTask");
  await new Promise((resolve) => setTimeout(resolve, 1000));
  return "Ran slow task.";
});

const main = entrypoint(
  { checkpointer, name: "main" },
  async (inputs: Record<string, unknown>) => {
    called.push("entrypoint");
    const slowTaskResult = await slowTask();
    await getInfo(); // throws on the first run
    return slowTaskResult;
  }
);

const config = {
  configurable: {
    thread_id: "1",
  },
};

try {
  await main.invoke({ any_input: "foobar" }, config);
} catch (err) {
  // First run fails in getInfo.
}

// :remove-start:
if (JSON.stringify(called) !== JSON.stringify(["entrypoint", "slowTask", "getInfo"])) {
  throw new Error(`unexpected initial execution: ${called}`);
}
// :remove-end:
called.length = 0;
console.log(await main.invoke(null, config));
// 'Ran slow task.'
console.log(called);
// ['entrypoint', 'getInfo']
// :snippet-end:

// :remove-start:
if (JSON.stringify(called) !== JSON.stringify(["entrypoint", "getInfo"])) {
  throw new Error(`completed slowTask ran again: ${called}`);
}
const resumed = await main.invoke(null, config);
if (resumed !== "Ran slow task.") {
  throw new Error(`expected restored slow task, got ${resumed}`);
}
console.log("✓ langgraph-functional-api-tasks-resume");
// :remove-end:
