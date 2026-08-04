# :snippet-start: deepagents-sandbox-download-langsmith-py
from deepagents.backends.langsmith import LangSmithSandbox
from langsmith.sandbox import SandboxClient

client = SandboxClient()
ls_sandbox = client.create_sandbox()
backend = LangSmithSandbox(sandbox=ls_sandbox)

# :remove-start:
backend.upload_files(
    [
        ("/src/index.py", b"print('Hello')\n"),
        ("/output.txt", b"done\n"),
    ]
)
# :remove-end:

results = backend.download_files(["/src/index.py", "/output.txt"])
for result in results:
    if result.content is not None:
        print(f"{result.path}: {result.content.decode()}")
    else:
        print(f"Failed to download {result.path}: {result.error}")
# :snippet-end:

# :remove-start:
try:
    assert any(r.content is not None for r in results)
    print("✓ deepagents-sandbox-download-langsmith-py validated")
finally:
    client.delete_sandbox(ls_sandbox.name)
# :remove-end:
