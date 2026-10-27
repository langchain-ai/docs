"""Managed LangSmith sandbox declaration.

MDA owns the run-scoped name, reuse across turns, and lifecycle. Delete this
directory to run without a sandbox.

To provision a recipe snapshot, add ``sandbox/setup.sh``. ``mda deploy`` and
``mda dev`` bake it once; new threads clone it without re-running the script.
"""

from managed_deepagents import define_sandbox

sandbox = define_sandbox(
    # Doc review and clone work can take longer than the default window.
    idle_ttl_seconds=3600,
    default_timeout=900,
)
