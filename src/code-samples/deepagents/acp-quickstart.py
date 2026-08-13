# :snippet-start: acp-quickstart-py
# :codegroup-fence-mods: icon="server"
import asyncio

from acp import run_agent
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver

from deepagents_acp.server import AgentServerACP


async def main() -> None:
    agent = create_deep_agent(
        model="google_genai:gemini-3.5-flash",
        # You can customize your deep agent here: set a custom prompt,
        # add your own tools, attach middleware, or compose subagents.
        system_prompt="You are a helpful coding assistant",
        checkpointer=MemorySaver(),
    )

    server = AgentServerACP(agent)
    await run_agent(server)

# :remove-start:
import sys

# Validate construction without blocking on stdio.
_agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    system_prompt="You are a helpful coding assistant",
    checkpointer=MemorySaver(),
)
_server = AgentServerACP(_agent)
assert _server is not None
print("✓ acp-quickstart sample validated")
sys.exit(0);
# :remove-end:
if __name__ == "__main__":
    asyncio.run(main())
# :snippet-end:
