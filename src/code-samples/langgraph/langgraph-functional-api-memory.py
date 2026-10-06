# :snippet-start: langgraph-functional-api-memory-accumulate-py
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import entrypoint

checkpointer = InMemorySaver()


@entrypoint(checkpointer=checkpointer)
def accumulate(n: int, *, previous: int | None = None) -> int:
    previous = previous or 0
    return previous + n


config = {"configurable": {"thread_id": "1"}}
print(accumulate.invoke(1, config))  # 1
print(accumulate.invoke(2, config))  # 3
print(accumulate.invoke(3, config))  # 6
# :snippet-end:

# :remove-start:
assert accumulate.invoke(0, config) == 6
# :remove-end:

# :snippet-start: langgraph-functional-api-memory-final-py
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import entrypoint

checkpointer = InMemorySaver()


@entrypoint(checkpointer=checkpointer)
def accumulate(n: int, *, previous: int | None = None) -> entrypoint.final[int, int]:
    previous = previous or 0
    total = previous + n
    # Return the *previous* value to the caller but save the *new* total.
    return entrypoint.final(value=previous, save=total)


config = {"configurable": {"thread_id": "my-thread"}}

print(accumulate.invoke(1, config=config))  # 0
print(accumulate.invoke(2, config=config))  # 1
print(accumulate.invoke(3, config=config))  # 3
# :snippet-end:

# :remove-start:
assert accumulate.get_state(config).values == 3
# :remove-end:

# :snippet-start: langgraph-functional-api-memory-get-state-py
config = {
    "configurable": {
        "thread_id": "my-thread",  # [!code highlight]
        # optionally provide an ID for a specific checkpoint,
        # otherwise the latest checkpoint is shown
        # "checkpoint_id": "1f1c1826-2179-626c-8004-96dc43069e17"  # [!code highlight]
    }
}
print(accumulate.get_state(config))  # [!code highlight]
# :snippet-end:

# :snippet-start: langgraph-functional-api-memory-history-py
config = {"configurable": {"thread_id": "my-thread"}}  # [!code highlight]
history = list(accumulate.get_state_history(config))  # [!code highlight]
print(history[0])
# :snippet-end:

# :remove-start:
assert history[0].values == 3
# :remove-end:

# :snippet-start: langgraph-functional-api-memory-delete-py
checkpointer.delete_thread("my-thread")
print(accumulate.get_state(config))
# StateSnapshot(values={}, next=(), config={'configurable': {'thread_id': 'my-thread'}}, ...)
# :snippet-end:

# :remove-start:
assert accumulate.get_state(config).values == {}
# :remove-end:

# :snippet-start: langgraph-functional-api-memory-store-py
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import entrypoint
from langgraph.runtime import Runtime
from langgraph.store.memory import InMemoryStore

checkpointer = InMemorySaver()
store = InMemoryStore()


@entrypoint(checkpointer=checkpointer, store=store)
def remember(inputs: dict, *, runtime: Runtime):
    memory_store = runtime.store
    namespace = (inputs["user_id"], "memories")
    fact = inputs.get("fact")
    if fact:
        memory_store.put(namespace, "profile", {"fact": fact})
    items = memory_store.search(namespace)
    return [item.value for item in items]


config_a = {"configurable": {"thread_id": "thread-a"}}
config_b = {"configurable": {"thread_id": "thread-b"}}

remember.invoke(
    {"user_id": "user-1", "fact": "Prefers dark mode"},
    config_a,
)
print(remember.invoke({"user_id": "user-1"}, config_b))
# -> [{'fact': 'Prefers dark mode'}]
# :snippet-end:

# :remove-start:
assert remember.invoke({"user_id": "user-1"}, config_b) == [
    {"fact": "Prefers dark mode"}
]
print("✓ langgraph-functional-api-memory")
# :remove-end:

# :snippet-start: langgraph-functional-api-memory-chatbot-py
from langchain_core.messages import BaseMessage
from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import entrypoint, task
from langgraph.graph import add_messages

# :remove-start:
import os

os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-test-key")
# :remove-end:
model = ChatAnthropic(model="claude-sonnet-4-6")
# :remove-start:
from langchain.messages import AIMessage
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel

model = GenericFakeChatModel(
    messages=iter(
        [
            AIMessage(content="Hi Bob!"),
            AIMessage(content="Your name is Bob"),
        ]
    )
)
# :remove-end:


@task
def call_model(messages: list[BaseMessage]):
    response = model.invoke(messages)
    return response


checkpointer = InMemorySaver()


@entrypoint(checkpointer=checkpointer)
def workflow(inputs: list[BaseMessage], *, previous: list[BaseMessage] | None = None):
    if previous:
        inputs = add_messages(previous, inputs)

    response = call_model(inputs).result()
    return entrypoint.final(value=response, save=add_messages(inputs, response))


config = {"configurable": {"thread_id": "1"}}
input_message = {"role": "user", "content": "hi! I'm bob"}
print(workflow.invoke([input_message], config))
# -> AIMessage with a greeting that uses the name Bob

input_message = {"role": "user", "content": "what's my name?"}
print(workflow.invoke([input_message], config))
# -> AIMessage that answers "Bob"
# :snippet-end:

# :remove-start:
assert workflow.get_state(config).values is not None
print("✓ langgraph-functional-api-memory-chatbot")
# :remove-end:
