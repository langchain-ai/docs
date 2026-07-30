# :snippet-start: deepagents-sandbox-basic-daytona-py
from daytona import Daytona
from deepagents import create_deep_agent
from langchain_anthropic import ChatAnthropic
from langchain_daytona import DaytonaSandbox

sandbox = Daytona().create()
backend = DaytonaSandbox(sandbox=sandbox)

agent = create_deep_agent(
    model=ChatAnthropic(model="claude-sonnet-4-6"),
    system_prompt="You are a Python coding assistant with sandbox access.",
    backend=backend,
)

try:
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Create a small Python package and run pytest",
                }
            ]
        }
    )
finally:
    sandbox.stop()
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    assert agent is not None
    print("✓ deepagents-sandbox-basic-daytona-py validated")
# :remove-end:
