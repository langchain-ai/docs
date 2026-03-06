"""PostgreSQL setup for code samples.

This module provides PostgreSQL connection setup for code samples.
It attempts to use testcontainers if available, otherwise provides
utilities to work with environment-configured postgres.
"""

import os
import subprocess
import time


def get_postgres_uri() -> str:
    """Get PostgreSQL connection URI.

    Tries multiple approaches in order:
    1. Check POSTGRES_URI environment variable
    2. Attempt to use testcontainers to spin up postgres
    3. Fall back to default local postgres connection
    """
    # Check environment variable first
    if env_uri := os.environ.get("POSTGRES_URI"):
        return env_uri

    # Try testcontainers
    try:
        from testcontainers.postgres import (  # type: ignore[import-not-found]
            PostgresContainer,
        )

        # Store container in a global so it persists
        if not hasattr(get_postgres_uri, "_container"):
            # Use pgvector image which includes the vector extension
            container = PostgresContainer("pgvector/pgvector:pg17")
            container.start()
            get_postgres_uri._container = container  # type: ignore[attr-defined]
            # Give it a moment to fully start
            time.sleep(2)

        return get_postgres_uri._container.get_connection_url()  # type: ignore[attr-defined]
    except ImportError:
        pass

    # Try to use docker directly if testcontainers not available
    try:
        # Check if postgres container is already running
        result = subprocess.run(
            [
                "docker",
                "ps",
                "--filter",
                "name=langchain-docs-postgres",
                "--format",
                "{{.Names}}",
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )

        if "langchain-docs-postgres" not in result.stdout:
            # Start a postgres container with pgvector extension
            subprocess.run(
                [
                    "docker",
                    "run",
                    "-d",
                    "--name",
                    "langchain-docs-postgres",
                    "-e",
                    "POSTGRES_PASSWORD=postgres",
                    "-e",
                    "POSTGRES_DB=postgres",
                    "-p",
                    "5442:5432",
                    "pgvector/pgvector:pg17",
                ],
                check=True,
                capture_output=True,
                timeout=30,
            )
            # Give it time to start
            time.sleep(3)

        return "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable"
    except (subprocess.SubprocessError, FileNotFoundError):
        pass

    # Fall back to default (assumes postgres is running locally)
    return "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable"
