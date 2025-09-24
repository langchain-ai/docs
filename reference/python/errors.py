"""Errors for the Python reference docs build."""


class TarPathTraversalError(Exception):
    """Raised when a tar extraction would escape the target directory."""

    def __init__(self) -> None:
        """Initialize the exception."""
        super().__init__("Attempted path traversal in tar file")


class InvalidTarballURLSchemeError(ValueError):
    """Raised when the tarball URL uses an unsupported scheme."""

    def __init__(self, scheme: str) -> None:
        """Initialize the exception."""
        super().__init__(
            f"Only https URLs are allowed for tarball downloads (got {scheme!r})"
        )
