// :snippet-start: langgraph-functional-api-memory-chatbot-js
import { BaseMessage } from "@langchain/core/messages";
import { ChatAnthropic } from "@langchain/anthropic";
import {
  addMessages,
  entrypoint,
  getPreviousState,
  task,
  MemorySaver,
} from "@langchain/langgraph";

// :remove-start:
process.env.ANTHROPIC_API_KEY ??= "sk-ant-test-key";
import { FakeListChatModel } from "@langchain/core/utils/testing";
// :remove-end:
let model = new ChatAnthropic({ model: "claude-sonnet-4-6" });
// :remove-start:
model = new FakeListChatModel({
  responses: ["Hi Bob!", "Your name is Bob"],
}) as unknown as ChatAnthropic;
// :remove-end:

const callModel = task(
  "callModel",
  async (messages: BaseMessage[]): Promise<BaseMessage> => {
    const response = await model.invoke(messages);
    return response;
  }
);

const checkpointer = new MemorySaver();

const workflow = entrypoint(
  { checkpointer, name: "workflow" },
  async (inputs: BaseMessage[]): Promise<BaseMessage> => {
    const previous = getPreviousState<BaseMessage[]>();
    let messages = inputs;
    if (previous) {
      messages = addMessages(previous, inputs);
    }

    const response = await callModel(messages);
    return entrypoint.final({
      value: response,
      save: addMessages(messages, response),
    });
  }
);

const config = { configurable: { thread_id: "1" } };
const inputMessage = { role: "user", content: "hi! I'm bob" };
console.log(await workflow.invoke([inputMessage], config));
// -> AIMessage with a greeting that uses the name Bob

const inputMessage2 = { role: "user", content: "what's my name?" };
console.log(await workflow.invoke([inputMessage2], config));
// -> AIMessage that answers "Bob"
// :snippet-end:

// :remove-start:
const saved = await workflow.getState(config);
if (saved.values == null) {
  throw new Error("expected checkpointed conversation state");
}
console.log("✓ langgraph-functional-api-memory-chatbot");
// :remove-end:
