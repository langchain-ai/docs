"""Build a data analysis agent from scratch using create_agent and Deep Agents middleware."""

# :snippet-start: deep-agent-from-scratch-minimal-py
from langchain.agents import create_agent

agent = create_agent("anthropic:claude-sonnet-4-6", tools=[])
# :snippet-end:

# :snippet-start: deep-agent-from-scratch-sandbox-py
from langchain.agents import create_agent
from deepagents.backends.langsmith import LangSmithSandbox
from deepagents.middleware import FilesystemMiddleware
from langsmith.sandbox import SandboxClient

client = SandboxClient()
# :remove-start:
sandboxes = client.list_sandboxes()
for existing in sandboxes:
    if existing.name == "langchain-docs":
        client.delete_sandbox(existing.name)
# :remove-end:
sandbox = client.create_sandbox(name="langchain-docs")
backend = LangSmithSandbox(sandbox=sandbox)

agent = create_agent(
    "anthropic:claude-sonnet-4-6",
    tools=[],
    middleware=[FilesystemMiddleware(backend=backend)],
)

# :snippet-end:

# :snippet-start: deep-agent-from-scratch-upload-py
import csv
import io

rows = [
    ["Date", "Product", "Units", "Revenue"],
    ["2025-08-01", "Widget A", 10, 250],
    ["2025-08-02", "Widget B", 5, 125],
    ["2025-08-03", "Widget A", 7, 175],
    ["2025-08-04", "Widget C", 3, 90],
]
buf = io.StringIO()
csv.writer(buf).writerows(rows)
backend.upload_files([("/sales.csv", buf.getvalue().encode())])

upload_stream = agent.stream_events(
    {
        "messages": [
            {"role": "user", "content": "Analyze sales.csv. Summarize trends."}
        ]
    },
    version="v3",
    config={"recursion_limit": 30},
)
for item in upload_stream.messages:
    print(item.text)
upload_stream.output
# :snippet-end:

# :snippet-start: deep-agent-from-scratch-summarization-py
from deepagents.middleware import FilesystemMiddleware, SummarizationMiddleware

model = "anthropic:claude-sonnet-4-6"

agent = create_agent(
    model=model,
    tools=[],
    middleware=[
        FilesystemMiddleware(backend=backend),
        SummarizationMiddleware(model=model, backend=backend),
    ],
)
# :snippet-end:

# :snippet-start: deep-agent-from-scratch-skills-upload-py
from pathlib import Path

skills_dir = (Path(__file__).resolve().parent / "skills").resolve()
# :remove-start:
skills_dir = Path("src/code-samples/langchain/skills").resolve()
# :remove-end:
skill_files: list[tuple[str, bytes]] = []
for path in sorted(skills_dir.rglob("*")):
    if not path.is_file():
        continue
    rel = path.resolve().relative_to(skills_dir)
    skill_files.append((f"/skills/{rel.as_posix()}", path.read_bytes()))
backend.upload_files(skill_files)
# :snippet-end:

# :snippet-start: deep-agent-from-scratch-skills-py
from deepagents.middleware import FilesystemMiddleware, SkillsMiddleware, SummarizationMiddleware

agent = create_agent(
    model=model,
    tools=[],
    middleware=[
        FilesystemMiddleware(backend=backend),
        SummarizationMiddleware(model=model, backend=backend),
        SkillsMiddleware(backend=backend, sources=["/skills/"]),
    ],
)
# :snippet-end:

# :snippet-start: deep-agent-from-scratch-subagent-py
from deepagents import SubAgent
from deepagents.middleware import (
    FilesystemMiddleware,
    SkillsMiddleware,
    SubAgentMiddleware,
    SummarizationMiddleware,
)
from langchain.agents.middleware import TodoListMiddleware

visualizer: SubAgent = {
    "name": "visualizer",
    "description": "Generates charts and visualizations from data files in the sandbox.",
    "system_prompt": "You are a data visualization specialist. Write Python scripts using matplotlib and seaborn. Save all figures as PNG files.",
    "tools": [],
    "model": "anthropic:claude-sonnet-4-6",
}

agent = create_agent(
    model=model,
    tools=[],
    middleware=[
        FilesystemMiddleware(backend=backend),
        SummarizationMiddleware(model=model, backend=backend),
        SkillsMiddleware(backend=backend, sources=["/skills/"]),
        TodoListMiddleware(),
        SubAgentMiddleware(backend=backend, subagents=[visualizer]),
    ],
)
# :snippet-end:

# :remove-start:
assert backend.read("/sales.csv").error is None
assert backend.read("/skills/pandas-patterns/SKILL.md").error is None
assert agent is not None

stream = agent.stream_events(
    {
        "messages": [
            {
                "role": "user",
                "content": (
                    "Use read_file on /sales.csv only. Summarize total revenue "
                    "by product in one short sentence. Do not use glob or "
                    "list other directories."
                ),
            }
        ]
    },
    version="v3",
    config={"recursion_limit": 30},
)
saw_message = False
for item in stream.messages:
    saw_message = True
    print("[agent]", item.text)
stream.output
assert saw_message, "expected at least one streamed message"
print("✓ deep-agent-from-scratch sample completed")
# :remove-end:
