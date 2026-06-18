# :snippet-start: frontend-sandbox-thread-backend-py
from deepagents import create_deep_agent
from deepagents.backends.langsmith import LangSmithSandbox
from langgraph.config import get_config


def get_or_create_sandbox_for_thread(thread_id: str) -> LangSmithSandbox:
    if not thread_id:
        raise ValueError("thread_id is required")
    # Look up sandbox_id from thread metadata, create if missing, and seed files.
    raise NotImplementedError(
        "Implement sandbox lookup and creation for your deployment environment."
    )


def get_thread_id_from_config() -> str:
    configurable = get_config().get("configurable", {})
    thread_id = configurable.get("thread_id")
    if not thread_id:
        raise ValueError("No thread_id, agent must run on a thread")
    return thread_id


def agent():
    return create_deep_agent(
        model="google_genai:gemini-3.5-flash",
        backend=lambda _runtime: get_or_create_sandbox_for_thread(
            get_thread_id_from_config()
        ),
    )
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    assert callable(agent)
    print("✓ frontend sandbox backend wiring sample loaded")
# :remove-end:
