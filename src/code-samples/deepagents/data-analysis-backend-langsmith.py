"""Data analysis tutorial: LangSmith sandbox backend."""

# :snippet-start: data-analysis-backend-langsmith-py
from deepagents.backends.langsmith import LangSmithSandbox
from langsmith.sandbox import SandboxClient

client = SandboxClient()
ls_sandbox = client.create_sandbox()
backend = LangSmithSandbox(sandbox=ls_sandbox)
# :snippet-end:

# :remove-start:
try:
    assert backend is not None
    print("✓ data-analysis-backend-langsmith sample validated")
finally:
    client.delete_sandbox(ls_sandbox.name)
# :remove-end:
