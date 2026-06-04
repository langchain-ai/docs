# :snippet-start: tool-runtime-context-thread-py
from dataclasses import dataclass

from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langchain_core.utils.uuid import uuid7
from langchain_openai import ChatOpenAI


USER_DATABASE = {
    "user123": {
        "name": "Alice Johnson",
        "account_type": "Premium",
        "balance": 5000,
        "email": "alice@example.com",
    },
    "user456": {
        "name": "Bob Smith",
        "account_type": "Standard",
        "balance": 1200,
        "email": "bob@example.com",
    },
}


@dataclass
class UserContext:
    user_id: str


@tool
def get_account_info(runtime: ToolRuntime[UserContext]) -> str:
    """Get the current user's account information."""
    user_id = runtime.context.user_id

    if user_id in USER_DATABASE:
        user = USER_DATABASE[user_id]
        return (
            f"Account holder: {user['name']}\n"
            f"Type: {user['account_type']}\n"
            f"Balance: ${user['balance']}"
        )
    return "User not found"


model = ChatOpenAI(model="gpt-5.4")
agent = create_agent(
    model,
    tools=[get_account_info],
    context_schema=UserContext,
    system_prompt="You are a financial assistant.",
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "What's my current balance?"}]},
    config={"configurable": {"thread_id": str(uuid7())}},
    context=UserContext(user_id="user123"),
)
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    last = result["messages"][-1]
    text = last.content_blocks[0]["text"] if last.content_blocks else str(last.content)
    assert "5000" in text or "$5" in text or "5,000" in text, text
    print("✓ tool runtime context and thread_id invoke sample completed")
# :remove-end:
