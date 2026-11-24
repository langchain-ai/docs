"""Backends: StoreBackend namespace factory type alias."""

# :snippet-start: backends-namespace-factory-type-py
from collections.abc import Callable

from langgraph.runtime import Runtime

NamespaceFactory = Callable[[Runtime], tuple[str, ...]]
# :snippet-end:

# :remove-start:
assert NamespaceFactory is not None
print("✓ backends-namespace-factory-type validated")
# :remove-end:
