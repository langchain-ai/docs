# :remove-start:
import asyncio
import time
import uuid

import langsmith as ls


def _is_not_found(error: Exception) -> bool:
    return getattr(error, "status_code", None) == 404


def _seed_agent(address: ls.AgentAddress, timeout: float = 120) -> None:
    """Send a trace to the agent, then wait for it to resolve.

    An agent exists once it has received a trace, and ingestion is asynchronous.
    """
    seed_client = ls.Client()

    @ls.traceable(name="docs-resolve-an-agent-seed")
    def seed() -> str:
        return "ok"

    with ls.tracing_context(enabled=True, client=seed_client, address=address):
        seed()
    seed_client.flush()

    deadline = time.monotonic() + timeout
    while True:
        try:
            asyncio.run(seed_client.sessions.resolve(**address))
            return
        except Exception as error:
            if not _is_not_found(error) or time.monotonic() > deadline:
                raise
            time.sleep(3)


# :remove-end:


# :snippet-start: resolve-agent-py
import asyncio

import langsmith as ls

client = ls.Client()
agent = ls.agent_address("checkout", "production")
# :remove-start:
_seed_agent(agent)
# :remove-end:


async def main() -> None:
    project = await client.sessions.resolve(**agent)

    async for run in client.runs.query(project_ids=[project.session_id]):
        print(run.id)


asyncio.run(main())
# :snippet-end:

# :remove-start:
print("✓ resolve-agent validated")
# :remove-end:


# :snippet-start: resolve-experiment-py
import asyncio

import langsmith as ls

client = ls.Client()
experiment_id = "<experiment-id>"
# :remove-start:
dataset = client.create_dataset(f"docs-resolve-an-agent-{uuid.uuid4().hex[:8]}")
seeded_experiment = client.create_project(
    f"docs-resolve-an-agent-{uuid.uuid4().hex[:8]}",
    reference_dataset_id=dataset.id,
)
experiment_id = str(seeded_experiment.id)
# :remove-end:
experiment = ls.experiment_address(experiment_id)


async def main() -> None:
    project = await client.sessions.resolve(**experiment)

    async for run in client.runs.query(project_ids=[project.session_id]):
        print(run.id)


asyncio.run(main())
# :snippet-end:

# :remove-start:
client.delete_project(project_id=experiment_id)
client.delete_dataset(dataset_id=dataset.id)
print("✓ resolve-experiment validated")
# :remove-end:


# :snippet-start: resolve-evaluators-py
import asyncio

import langsmith as ls

client = ls.Client()
evaluators = ls.evaluator_address()
# :remove-start:
# Evaluator traces go to the workspace's project named "evaluators".
client.create_project("evaluators", upsert=True)
# :remove-end:


async def main() -> None:
    project = await client.sessions.resolve(**evaluators)

    async for run in client.runs.query(project_ids=[project.session_id]):
        print(run.id)


asyncio.run(main())
# :snippet-end:

# :remove-start:
print("✓ resolve-evaluators validated")
# :remove-end:
