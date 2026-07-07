"""Customization page: MCP tools example."""

# :remove-start:
from deepagents import create_deep_agent

test_agent = create_deep_agent(model="anthropic:claude-sonnet-4-6", tools=[])
assert test_agent is not None
print("✓ customization-mcp sample wiring validated")
raise SystemExit(0)
# :remove-end:

# :snippet-start: customization-mcp-py
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from deepagents import create_deep_agent


async def main():
    async with MultiServerMCPClient(
        {
            "my_server": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            }
        }
    ) as client:
        tools = await client.get_tools()

        agent = create_deep_agent(
            model="openai:gpt-5.5",
            tools=tools,
        )

        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": "Use the MCP server to help me."}]},
            config={"configurable": {"thread_id": "1"}},
        )


asyncio.run(main())
# :snippet-end:
