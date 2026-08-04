"""Agents docs: core component examples (intro, model, tools, system prompt, structured output, name)."""

# :remove-start:
tools: list = []
# :remove-end:

# :snippet-start: agents-intro-py
from langchain.agents import create_agent

agent = create_agent(model="openai:gpt-5.4", tools=tools)
# :snippet-end:

# :remove-start:
_intro_agent = agent
# :remove-end:

# :snippet-start: agents-model-py
from langchain.agents import create_agent

agent = create_agent(model="openai:gpt-5.4", tools=tools)
# :snippet-end:

# :remove-start:
_model_agent = agent
# :remove-end:

# :snippet-start: agents-tools-py
from langchain.agents import create_agent
from langchain.tools import tool


@tool
def search(query: str) -> str:
    """Search for information."""
    return f"Results for: {query}"


agent = create_agent(model="openai:gpt-5.4", tools=[search])
# :snippet-end:

# :remove-start:
_tools_agent = agent
# :remove-end:

# :snippet-start: agents-system-prompt-py
agent = create_agent(
    model="openai:gpt-5.4",
    tools=tools,
    system_prompt="You are a helpful assistant. Be concise and accurate.",
)
# :snippet-end:

# :remove-start:
_system_prompt_agent = agent
# :remove-end:

# :snippet-start: agents-structured-output-py
from pydantic import BaseModel
from langchain.agents import create_agent


class Answer(BaseModel):
    summary: str
    confidence: float


agent = create_agent(model="openai:gpt-5.4", tools=tools, response_format=Answer)
result = agent.invoke({"messages": [{"role": "user", "content": "Summarize AI trends"}]})
result["structured_response"]  # Answer(summary=..., confidence=...)
# :snippet-end:

# :remove-start:
_structured_output_agent = agent
_structured_output_result = result
# :remove-end:

# :snippet-start: agents-name-py
agent = create_agent(model="openai:gpt-5.4", tools=tools, name="research_assistant")
# :snippet-end:

# :remove-start:
_name_agent = agent


def _assistant_text(result: dict) -> str:
    last = result["messages"][-1]
    if last.content_blocks:
        return last.content_blocks[0]["text"]
    return str(last.content)


def _assert_invokes(agent, label: str) -> None:
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "Say hello in one short sentence."}]}
    )
    assert _assistant_text(result).strip(), f"{label}: expected non-empty reply"
    print(f"✓ {label}")


if __name__ == "__main__":
    _assert_invokes(_intro_agent, "agents intro")
    _assert_invokes(_model_agent, "agents model")
    _assert_invokes(
        _tools_agent,
        "agents tools",
    )
    _assert_invokes(_system_prompt_agent, "agents system prompt")
    structured = _structured_output_result["structured_response"]
    assert structured.summary.strip(), "expected structured summary"
    assert 0.0 <= structured.confidence <= 1.0, "expected confidence in [0, 1]"
    print("✓ agents structured output")
    assert _name_agent.name == "research_assistant"
    _assert_invokes(_name_agent, "agents name")
# :remove-end:
