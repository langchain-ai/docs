"""Customization: virtual filesystem backend examples."""

# :snippet-start: backend-state-py
from deepagents import create_deep_agent
from deepagents.backends import StateBackend

# By default we provide a StateBackend
# KEEP MODEL
agent = create_deep_agent(model="google_genai:gemini-3.1-pro-preview")

# Under the hood, it looks like
# KEEP MODEL
agent2 = create_deep_agent(
    model="google_genai:gemini-3.1-pro-preview",
    backend=StateBackend(),
)
# :snippet-end:

# :snippet-start: backend-filesystem-py
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

# KEEP MODEL
agent = create_deep_agent(
    model="google_genai:gemini-3.1-pro-preview",
    backend=FilesystemBackend(root_dir=".", virtual_mode=True),
)
# :snippet-end:

# :snippet-start: backend-local-shell-py
from deepagents import create_deep_agent
from deepagents.backends import LocalShellBackend

# KEEP MODEL
agent = create_deep_agent(
    model="google_genai:gemini-3.1-pro-preview",
    backend=LocalShellBackend(root_dir=".", virtual_mode=True, env={"PATH": "/usr/bin:/bin"}),
)
# :snippet-end:

# :snippet-start: backend-store-py
from deepagents import create_deep_agent
from deepagents.backends import StoreBackend
from langgraph.store.memory import InMemoryStore

# KEEP MODEL
agent = create_deep_agent(
    model="google_genai:gemini-3.1-pro-preview",
    backend=StoreBackend(
        namespace=lambda ctx: (ctx.runtime.context.user_id,),
    ),
    store=InMemoryStore(),  # Good for local dev; omit for LangSmith Deployment
)
# :snippet-end:

# :snippet-start: backend-context-hub-py
from deepagents import create_deep_agent
from deepagents.backends import ContextHubBackend

# KEEP MODEL
agent = create_deep_agent(
    model="google_genai:gemini-3.1-pro-preview",
    backend=ContextHubBackend("my-agent"),
)
# :snippet-end:

# :snippet-start: backend-composite-py
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore

# KEEP MODEL
agent = create_deep_agent(
    model="google_genai:gemini-3.1-pro-preview",
    backend=CompositeBackend(
        default=StateBackend(),
        routes={
            "/memories/": StoreBackend(),
        },
    ),
    store=InMemoryStore(),  # Store passed to create_deep_agent, not backend
)
# :snippet-end:

# :remove-start:
assert agent is not None
assert agent2 is not None
# :remove-end:
