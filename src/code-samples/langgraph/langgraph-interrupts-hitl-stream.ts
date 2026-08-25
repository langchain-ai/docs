// :remove-start:
import {
  Annotation,
  Command,
  END,
  MemorySaver,
  START,
  StateGraph,
  interrupt,
} from "@langchain/langgraph";

const StreamState = Annotation.Root({
  step: Annotation<number>(),
  done: Annotation<boolean>(),
});

function firstInterrupt(_state: typeof StreamState.State) {
  interrupt("first question");
  return { step: 1 };
}

function secondInterrupt(_state: typeof StreamState.State) {
  interrupt("second question");
  return { done: true };
}

const graph = new StateGraph(StreamState)
  .addNode("first", firstInterrupt)
  .addNode("second", secondInterrupt)
  .addEdge(START, "first")
  .addEdge("first", "second")
  .addEdge("second", END)
  .compile({ checkpointer: new MemorySaver() });

const config = { configurable: { thread_id: "stream-1" } };
const initialInput: Record<string, unknown> = {};

function displayStreamingContent(_content: string): void {
  // Application-specific UI hook
}

async function getUserInput(_interruptInfo: unknown): Promise<string> {
  return "ok";
}
// :remove-end:

// :snippet-start: langgraph-interrupts-hitl-stream-js
import { Command } from "@langchain/langgraph";

let streamInput: Record<string, unknown> | Command = initialInput;

while (true) {
  const stream = await graph.streamEvents(streamInput, {
    ...config,
    version: "v3",
  });

  // Stream LLM message chunks (including any in subgraphs) as they arrive.
  for await (const message of stream.messages) {
    for await (const token of message.text) {
      displayStreamingContent(token);
    }
  }

  // After the run finishes (or pauses), check for interrupts and resume.
  if (!stream.interrupted) {
    const finalState = await stream.output;
    break;
  }

  const interruptInfo = stream.interrupts[0].payload;
  const userResponse = await getUserInput(interruptInfo);
  streamInput = new Command({ resume: userResponse });
}
// :snippet-end:

// :remove-start:
async function main() {
  const testConfig = { configurable: { thread_id: "stream-test" } };
  let streamInput: Record<string, unknown> | Command = {};
  let resumeRounds = 0;
  let final: typeof StreamState.State | undefined;

  while (true) {
    const testStream = await graph.streamEvents(streamInput, {
      ...testConfig,
      version: "v3",
    });
    for await (const _message of testStream.messages) {
      // Drain message stream so the run completes.
    }
    if (!testStream.interrupted) {
      final = await testStream.output;
      break;
    }
    streamInput = new Command({ resume: "ok" });
    resumeRounds += 1;
  }

  if (resumeRounds !== 2) {
    throw new Error(`Expected 2 resume rounds, got ${resumeRounds}`);
  }
  if (!final?.done) {
    throw new Error(`Expected done=true, got ${JSON.stringify(final)}`);
  }
  console.log("✓ langgraph-interrupts-hitl-stream");
}

main();
// :remove-end:
