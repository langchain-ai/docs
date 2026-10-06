# :snippet-start: langgraph-functional-api-tasks-retry-py
from langgraph.func import entrypoint, task
from langgraph.types import RetryPolicy

# Used only to simulate a transient failure. Do not use a global like this in production.
attempts = 0

retry_policy = RetryPolicy(retry_on=ValueError)


@task(retry_policy=retry_policy)
def get_info():
    global attempts
    attempts += 1

    if attempts < 2:
        raise ValueError("Failure")
    return "OK"


@entrypoint()
def main(inputs):
    return get_info().result()


print(main.invoke({"any_input": "foobar"}))
# 'OK'
# :snippet-end:

# :remove-start:
assert main.invoke({"any_input": "foobar"}) == "OK"
# :remove-end:

# :snippet-start: langgraph-functional-api-tasks-timeout-py
import asyncio

from langgraph.errors import NodeTimeoutError
from langgraph.func import entrypoint, task
from langgraph.types import RetryPolicy

attempts = 0


@task(
    timeout=1.0,
    retry_policy=RetryPolicy(retry_on=NodeTimeoutError),
)
async def call_api(url: str) -> str:
    global attempts
    attempts += 1
    if attempts < 2:
        await asyncio.sleep(2)
    return f"result from {url}"


@entrypoint(timeout=5.0)
async def workflow(inputs: dict) -> str:
    return await call_api(inputs["url"])


print(asyncio.run(workflow.ainvoke({"url": "https://example.com"})))
# 'result from https://example.com'
# :snippet-end:

# :remove-start:
assert (
    asyncio.run(workflow.ainvoke({"url": "https://example.com"}))
    == "result from https://example.com"
)
# :remove-end:

# :snippet-start: langgraph-functional-api-tasks-cache-py
import time

from langgraph.cache.memory import InMemoryCache
from langgraph.func import entrypoint, task
from langgraph.types import CachePolicy


@task(cache_policy=CachePolicy(ttl=120))  # [!code highlight]
def slow_add(x: int) -> int:
    time.sleep(1)
    return x * 2


@entrypoint(cache=InMemoryCache())
def main(inputs: dict) -> dict[str, int]:
    result1 = slow_add(inputs["x"]).result()
    result2 = slow_add(inputs["x"]).result()
    return {"result1": result1, "result2": result2}


print(main.invoke({"x": 5}))
# {'result1': 10, 'result2': 10}
# :snippet-end:

# :remove-start:
assert main.invoke({"x": 5}) == {"result1": 10, "result2": 10}
# :remove-end:

# :snippet-start: langgraph-functional-api-tasks-resume-py
import time

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import entrypoint, task

# Used only to simulate a transient failure. Do not use a global like this in production.
attempts = 0


@task()
def get_info():
    global attempts
    attempts += 1

    if attempts < 2:
        raise ValueError("Failure")
    return "OK"


checkpointer = InMemorySaver()


@task
def slow_task():
    time.sleep(1)
    return "Ran slow task."


@entrypoint(checkpointer=checkpointer)
def main(inputs):
    slow_task_result = slow_task().result()
    get_info().result()  # raises ValueError on the first run
    return slow_task_result


config = {"configurable": {"thread_id": "1"}}

try:
    main.invoke({"any_input": "foobar"}, config=config)
except ValueError:
    pass

print(main.invoke(None, config=config))
# 'Ran slow task.'
# :snippet-end:

# :remove-start:
assert main.invoke(None, config=config) == "Ran slow task."
print("✓ langgraph-functional-api-tasks")
# :remove-end:
