# :snippet-start: dns-aid-discovery
from langchain.agents import create_agent
from langchain_dns_aid import DnsAidMiddleware

# Create middleware with auto-publish and discovery tools
dns_middleware = DnsAidMiddleware(
    agent_name="research-assistant",
    domain="agents.example.com",
    endpoint="research.example.com",
    capabilities=["search", "summarize"],
    backend_name="route53",
)

# Agent auto-publishes to DNS on startup
agent = create_agent(
    model="gpt-4o",
    middleware=[dns_middleware],
)

# Agent can discover other agents during execution
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Find agents at agents.example.com that can help with data analysis"}]}
)
print(result["messages"][-1].content)
# :snippet-end:
